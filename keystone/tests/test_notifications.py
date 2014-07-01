# Copyright 2013 IBM Corp.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import uuid

import mock
from oslo.config import cfg
from oslotest import mockpatch
import testtools

from keystone.common import dependency
from keystone import notifications
from keystone.tests import test_v3


CONF = cfg.CONF

EXP_RESOURCE_TYPE = uuid.uuid4().hex
CREATED_OPERATION = 'created'
UPDATED_OPERATION = 'updated'
DELETED_OPERATION = 'deleted'


class ArbitraryException(Exception):
    pass


def register_callback(operation, resource_type=EXP_RESOURCE_TYPE):
    """Helper for creating and registering a mock callback.

    """
    callback = mock.Mock(__name__='callback',
                         im_class=mock.Mock(__name__='class'))
    notifications.register_event_callback(operation, resource_type, callback)
    return callback


class NotificationsWrapperTestCase(testtools.TestCase):
    def create_fake_ref(self):
        resource_id = uuid.uuid4().hex
        return resource_id, {
            'id': resource_id,
            'key': uuid.uuid4().hex
        }

    @notifications.created(EXP_RESOURCE_TYPE)
    def create_resource(self, resource_id, data):
        return data

    def test_resource_created_notification(self):
        exp_resource_id, data = self.create_fake_ref()
        callback = register_callback(CREATED_OPERATION)

        self.create_resource(exp_resource_id, data)
        callback.assert_called_with('identity', EXP_RESOURCE_TYPE,
                                    CREATED_OPERATION,
                                    {'resource_info': exp_resource_id})

    @notifications.updated(EXP_RESOURCE_TYPE)
    def update_resource(self, resource_id, data):
        return data

    def test_resource_updated_notification(self):
        exp_resource_id, data = self.create_fake_ref()
        callback = register_callback(UPDATED_OPERATION)

        self.update_resource(exp_resource_id, data)
        callback.assert_called_with('identity', EXP_RESOURCE_TYPE,
                                    UPDATED_OPERATION,
                                    {'resource_info': exp_resource_id})

    @notifications.deleted(EXP_RESOURCE_TYPE)
    def delete_resource(self, resource_id):
        pass

    def test_resource_deleted_notification(self):
        exp_resource_id = uuid.uuid4().hex
        callback = register_callback(DELETED_OPERATION)

        self.delete_resource(exp_resource_id)
        callback.assert_called_with('identity', EXP_RESOURCE_TYPE,
                                    DELETED_OPERATION,
                                    {'resource_info': exp_resource_id})

    @notifications.created(EXP_RESOURCE_TYPE)
    def create_exception(self, resource_id):
        raise ArbitraryException()

    def test_create_exception_without_notification(self):
        callback = register_callback(CREATED_OPERATION)
        self.assertRaises(
            ArbitraryException, self.create_exception, uuid.uuid4().hex)
        self.assertFalse(callback.called)

    @notifications.created(EXP_RESOURCE_TYPE)
    def update_exception(self, resource_id):
        raise ArbitraryException()

    def test_update_exception_without_notification(self):
        callback = register_callback(UPDATED_OPERATION)
        self.assertRaises(
            ArbitraryException, self.update_exception, uuid.uuid4().hex)
        self.assertFalse(callback.called)

    @notifications.deleted(EXP_RESOURCE_TYPE)
    def delete_exception(self, resource_id):
        raise ArbitraryException()

    def test_delete_exception_without_notification(self):
        callback = register_callback(DELETED_OPERATION)
        self.assertRaises(
            ArbitraryException, self.delete_exception, uuid.uuid4().hex)
        self.assertFalse(callback.called)


class NotificationsTestCase(testtools.TestCase):
    def setUp(self):
        super(NotificationsTestCase, self).setUp()

        # these should use self.config_fixture.config(), but they haven't
        # been registered yet
        CONF.rpc_backend = 'fake'
        CONF.notification_driver = ['fake']

    def test_send_notification(self):
        """Test the private method _send_notification to ensure event_type,
           payload, and context are built and passed properly.
        """
        resource = uuid.uuid4().hex
        resource_type = EXP_RESOURCE_TYPE
        operation = CREATED_OPERATION

        # NOTE(ldbragst): Even though notifications._send_notification doesn't
        # contain logic that creates cases, this is supposed to test that
        # context is always empty and that we ensure the resource ID of the
        # resource in the notification is contained in the payload. It was
        # agreed that context should be empty in Keystone's case, which is
        # also noted in the /keystone/notifications.py module. This test
        # ensures and maintains these conditions.
        expected_args = [
            {},  # empty context
            'identity.%s.created' % resource_type,  # event_type
            {'resource_info': resource},  # payload
            'INFO',  # priority is always INFO...
        ]

        with mock.patch.object(notifications._get_notifier(),
                               '_notify') as mocked:
            notifications._send_notification(operation, resource_type,
                                             resource)
            mocked.assert_called_once_with(*expected_args)


class NotificationsForEntities(test_v3.RestfulTestCase):
    def setUp(self):
        super(NotificationsForEntities, self).setUp()
        self._notifications = []

        def fake_notify(operation, resource_type, resource_id,
                        public=True):
            note = {
                'resource_id': resource_id,
                'operation': operation,
                'resource_type': resource_type,
                'send_notification_called': True,
                'public': public}
            self._notifications.append(note)

        self.useFixture(mockpatch.PatchObject(
            notifications, '_send_notification', fake_notify))

    def _assertNotifySeen(self, resource_id, operation, resource_type):
        self.assertIn(operation, self.exp_operations)
        self.assertIn(resource_id, self.exp_resource_ids)
        self.assertIn(resource_type, self.exp_resource_types)
        self.assertTrue(self.send_notification_called)

    def _assertLastNotify(self, resource_id, operation, resource_type):
        self.assertTrue(len(self._notifications) > 0)
        note = self._notifications[-1]
        self.assertEqual(note['operation'], operation)
        self.assertEqual(note['resource_id'], resource_id)
        self.assertEqual(note['resource_type'], resource_type)
        self.assertTrue(note['send_notification_called'])

    def _assertNotifyNotSent(self, resource_id, operation, resource_type,
                             public=True):
        unexpected = {
            'resource_id': resource_id,
            'operation': operation,
            'resource_type': resource_type,
            'send_notification_called': True,
            'public': public}
        for note in self._notifications:
            self.assertNotEqual(unexpected, note)

    def _assertNotifySent(self, resource_id, operation, resource_type, public):
        expected = {
            'resource_id': resource_id,
            'operation': operation,
            'resource_type': resource_type,
            'send_notification_called': True,
            'public': public}
        for note in self._notifications:
            if expected == note:
                break
        else:
            self.fail("Notification not sent.")

    def test_create_group(self):
        group_ref = self.new_group_ref(domain_id=self.domain_id)
        group_ref = self.identity_api.create_group(group_ref)
        self._assertLastNotify(group_ref['id'], CREATED_OPERATION, 'group')

    def test_create_project(self):
        project_ref = self.new_project_ref(domain_id=self.domain_id)
        self.assignment_api.create_project(project_ref['id'], project_ref)
        self._assertLastNotify(
            project_ref['id'], CREATED_OPERATION, 'project')

    def test_create_role(self):
        role_ref = self.new_role_ref()
        self.assignment_api.create_role(role_ref['id'], role_ref)
        self._assertLastNotify(role_ref['id'], CREATED_OPERATION, 'role')

    def test_create_user(self):
        user_ref = self.new_user_ref(domain_id=self.domain_id)
        user_ref = self.identity_api.create_user(user_ref)
        self._assertLastNotify(user_ref['id'], CREATED_OPERATION, 'user')

    def test_create_trust(self):
        trustor = self.new_user_ref(domain_id=self.domain_id)
        trustor = self.identity_api.create_user(trustor)
        trustee = self.new_user_ref(domain_id=self.domain_id)
        trustee = self.identity_api.create_user(trustee)
        role_ref = self.new_role_ref()
        self.assignment_api.create_role(role_ref['id'], role_ref)
        trust_ref = self.new_trust_ref(trustor['id'],
                                       trustee['id'])
        self.trust_api.create_trust(trust_ref['id'],
                                    trust_ref,
                                    [role_ref])
        self._assertLastNotify(
            trust_ref['id'], CREATED_OPERATION, 'OS-TRUST:trust')

    def test_delete_group(self):
        group_ref = self.new_group_ref(domain_id=self.domain_id)
        group_ref = self.identity_api.create_group(group_ref)
        self.identity_api.delete_group(group_ref['id'])
        self._assertLastNotify(group_ref['id'], DELETED_OPERATION, 'group')

    def test_delete_project(self):
        project_ref = self.new_project_ref(domain_id=self.domain_id)
        self.assignment_api.create_project(project_ref['id'], project_ref)
        self.assignment_api.delete_project(project_ref['id'])
        self._assertLastNotify(
            project_ref['id'], DELETED_OPERATION, 'project')

    def test_delete_role(self):
        role_ref = self.new_role_ref()
        self.assignment_api.create_role(role_ref['id'], role_ref)
        self.assignment_api.delete_role(role_ref['id'])
        self._assertLastNotify(role_ref['id'], DELETED_OPERATION, 'role')

    def test_delete_user(self):
        user_ref = self.new_user_ref(domain_id=self.domain_id)
        user_ref = self.identity_api.create_user(user_ref)
        self.identity_api.delete_user(user_ref['id'])
        self._assertLastNotify(user_ref['id'], DELETED_OPERATION, 'user')

    def test_update_domain(self):
        domain_ref = self.new_domain_ref()
        self.assignment_api.create_domain(domain_ref['id'], domain_ref)
        domain_ref['description'] = uuid.uuid4().hex
        self.assignment_api.update_domain(domain_ref['id'], domain_ref)
        self._assertLastNotify(domain_ref['id'], UPDATED_OPERATION, 'domain')

    def test_delete_trust(self):
        trustor = self.new_user_ref(domain_id=self.domain_id)
        trustor = self.identity_api.create_user(trustor)
        trustee = self.new_user_ref(domain_id=self.domain_id)
        trustee = self.identity_api.create_user(trustee)
        role_ref = self.new_role_ref()
        trust_ref = self.new_trust_ref(trustor['id'], trustee['id'])
        self.trust_api.create_trust(trust_ref['id'],
                                    trust_ref,
                                    [role_ref])
        self.trust_api.delete_trust(trust_ref['id'])
        self._assertLastNotify(
            trust_ref['id'], DELETED_OPERATION, 'OS-TRUST:trust')

    def test_delete_domain(self):
        domain_ref = self.new_domain_ref()
        self.assignment_api.create_domain(domain_ref['id'], domain_ref)
        domain_ref['enabled'] = False
        self.assignment_api.update_domain(domain_ref['id'], domain_ref)
        self.assignment_api.delete_domain(domain_ref['id'])
        self._assertLastNotify(domain_ref['id'], DELETED_OPERATION, 'domain')

    def test_disable_domain(self):
        domain_ref = self.new_domain_ref()
        self.assignment_api.create_domain(domain_ref['id'], domain_ref)
        domain_ref['enabled'] = False
        self.assignment_api.update_domain(domain_ref['id'], domain_ref)
        self._assertNotifySent(domain_ref['id'], 'disabled', 'domain',
                               public=False)

    def test_disable_of_disabled_domain_does_not_notify(self):
        domain_ref = self.new_domain_ref()
        domain_ref['enabled'] = False
        self.assignment_api.create_domain(domain_ref['id'], domain_ref)
        # The domain_ref above is not changed during the create process. We
        # can use the same ref to perform the update.
        self.assignment_api.update_domain(domain_ref['id'], domain_ref)
        self._assertNotifyNotSent(domain_ref['id'], 'disabled', 'domain',
                                  public=False)

    def test_update_group(self):
        group_ref = self.new_group_ref(domain_id=self.domain_id)
        group_ref = self.identity_api.create_group(group_ref)
        self.identity_api.update_group(group_ref['id'], group_ref)
        self._assertLastNotify(group_ref['id'], UPDATED_OPERATION, 'group')

    def test_update_project(self):
        project_ref = self.new_project_ref(domain_id=self.domain_id)
        self.assignment_api.create_project(project_ref['id'], project_ref)
        self.assignment_api.update_project(project_ref['id'], project_ref)
        self._assertNotifySent(
            project_ref['id'], UPDATED_OPERATION, 'project', public=True)

    def test_disable_project(self):
        project_ref = self.new_project_ref(domain_id=self.domain_id)
        self.assignment_api.create_project(project_ref['id'], project_ref)
        project_ref['enabled'] = False
        self.assignment_api.update_project(project_ref['id'], project_ref)
        self._assertNotifySent(project_ref['id'], 'disabled', 'project',
                               public=False)

    def test_disable_of_disabled_project_does_not_notify(self):
        project_ref = self.new_project_ref(domain_id=self.domain_id)
        project_ref['enabled'] = False
        self.assignment_api.create_project(project_ref['id'], project_ref)
        # The project_ref above is not changed during the create process. We
        # can use the same ref to perform the update.
        self.assignment_api.update_project(project_ref['id'], project_ref)
        self._assertNotifyNotSent(project_ref['id'], 'disabled', 'project',
                                  public=False)

    def test_update_project_does_not_send_disable(self):
        project_ref = self.new_project_ref(domain_id=self.domain_id)
        self.assignment_api.create_project(project_ref['id'], project_ref)
        project_ref['enabled'] = True
        self.assignment_api.update_project(project_ref['id'], project_ref)
        self._assertLastNotify(
            project_ref['id'], UPDATED_OPERATION, 'project')
        self._assertNotifyNotSent(project_ref['id'], 'disabled', 'project')

    def test_update_role(self):
        role_ref = self.new_role_ref()
        self.assignment_api.create_role(role_ref['id'], role_ref)
        self.assignment_api.update_role(role_ref['id'], role_ref)
        self._assertLastNotify(role_ref['id'], UPDATED_OPERATION, 'role')

    def test_update_user(self):
        user_ref = self.new_user_ref(domain_id=self.domain_id)
        user_ref = self.identity_api.create_user(user_ref)
        self.identity_api.update_user(user_ref['id'], user_ref)
        self._assertLastNotify(user_ref['id'], UPDATED_OPERATION, 'user')


class TestEventCallbacks(test_v3.RestfulTestCase):

    def setUp(self):
        super(TestEventCallbacks, self).setUp()
        self.has_been_called = False

    def _project_deleted_callback(self, service, resource_type, operation,
                                  payload):
        self.has_been_called = True

    def _project_created_callback(self, service, resource_type, operation,
                                  payload):
        self.has_been_called = True

    def test_notification_received(self):
        callback = register_callback(CREATED_OPERATION, 'project')
        project_ref = self.new_project_ref(domain_id=self.domain_id)
        self.assignment_api.create_project(project_ref['id'], project_ref)
        self.assertTrue(callback.called)

    def test_notification_method_not_callable(self):
        fake_method = None
        self.assertRaises(TypeError,
                          notifications.register_event_callback,
                          UPDATED_OPERATION,
                          'project',
                          [fake_method])

    def test_notification_event_not_valid(self):
        self.assertRaises(ValueError,
                          notifications.register_event_callback,
                          uuid.uuid4().hex,
                          'project',
                          self._project_deleted_callback)

    def test_event_registration_for_unknown_resource_type(self):
        # Registration for unknown resource types should succeed.  If no event
        # is issued for that resource type, the callback wont be triggered.
        notifications.register_event_callback(DELETED_OPERATION,
                                              uuid.uuid4().hex,
                                              self._project_deleted_callback)
        resource_type = uuid.uuid4().hex
        notifications.register_event_callback(DELETED_OPERATION,
                                              resource_type,
                                              self._project_deleted_callback)

    def test_provider_event_callbacks_subscription(self):
        callback_called = []

        @dependency.provider('foo_api')
        class Foo:
            def __init__(self):
                self.event_callbacks = {
                    CREATED_OPERATION: {'project': [self.foo_callback]}}

            def foo_callback(self, service, resource_type, operation,
                             payload):
                # uses callback_called from the closure
                callback_called.append(True)

        Foo()
        project_ref = self.new_project_ref(domain_id=self.domain_id)
        self.assignment_api.create_project(project_ref['id'], project_ref)
        self.assertEqual([True], callback_called)

    def test_invalid_event_callbacks(self):
        @dependency.provider('foo_api')
        class Foo:
            def __init__(self):
                self.event_callbacks = 'bogus'

        self.assertRaises(ValueError, Foo)

    def test_invalid_event_callbacks_event(self):
        @dependency.provider('foo_api')
        class Foo:
            def __init__(self):
                self.event_callbacks = {CREATED_OPERATION: 'bogus'}

        self.assertRaises(ValueError, Foo)


class CadfNotificationsWrapperTestCase(test_v3.RestfulTestCase):

    LOCAL_HOST = 'localhost'
    ACTION = 'authenticate'

    def setUp(self):
        super(CadfNotificationsWrapperTestCase, self).setUp()
        self._notifications = []

        def fake_notify(action, initiator, outcome):
            note = {
                'action': action,
                'initiator': initiator,
                # NOTE(stevemar): outcome has 2 stages, pending and success
                # so we are ignoring it for now.
                # 'outcome': outcome,
                'send_notification_called': True}
            self._notifications.append(note)

        self.useFixture(mockpatch.PatchObject(
            notifications, '_send_audit_notification', fake_notify))

    def _assertLastNotify(self, action, user_id):
        self.assertTrue(self._notifications)
        note = self._notifications[-1]
        self.assertEqual(note['action'], action)
        initiator = note['initiator']
        self.assertEqual(initiator.name, user_id)
        self.assertEqual(initiator.host.address, self.LOCAL_HOST)
        self.assertTrue(note['send_notification_called'])

    def test_v3_authenticate_user_name_and_domain_id(self):
        user_id = self.user_id
        user_name = self.user['name']
        password = self.user['password']
        domain_id = self.domain_id
        data = self.build_authentication_request(username=user_name,
                                                 user_domain_id=domain_id,
                                                 password=password)
        self.post('/auth/tokens', body=data)
        self._assertLastNotify(self.ACTION, user_id)

    def test_v3_authenticate_user_id(self):
        user_id = self.user_id
        password = self.user['password']
        data = self.build_authentication_request(user_id=user_id,
                                                 password=password)
        self.post('/auth/tokens', body=data)
        self._assertLastNotify(self.ACTION, user_id)

    def test_v3_authenticate_user_name_and_domain_name(self):
        user_id = self.user_id
        user_name = self.user['name']
        password = self.user['password']
        domain_name = self.domain['name']
        data = self.build_authentication_request(username=user_name,
                                                 user_domain_name=domain_name,
                                                 password=password)
        self.post('/auth/tokens', body=data)
        self._assertLastNotify(self.ACTION, user_id)


class TestCallbackRegistration(testtools.TestCase):
    def setUp(self):
        super(TestCallbackRegistration, self).setUp()
        self.mock_log = mock.Mock()
        # Force the callback logging to occur
        self.mock_log.logger.getEffectiveLevel.return_value = 1

    def verify_log_message(self, data):
        """Tests that use this are a little brittle because adding more
        logging can break them.

        TODO(dstanek): remove the need for this in a future refactoring

        """
        self.assertEqual(len(data), self.mock_log.info.call_count)
        for i, data in enumerate(data):
            self.mock_log.info.assert_any_call(mock.ANY, data)

    def test_a_function_callback(self):
        def callback(*args, **kwargs):
            pass

        resource_type = 'thing'
        with mock.patch('keystone.notifications.LOG', self.mock_log):
            notifications.register_event_callback(
                CREATED_OPERATION, resource_type, callback)

        expected_log_data = {
            'callback': 'keystone.tests.test_notifications.callback',
            'event': 'identity.%s.created' % resource_type
        }
        self.verify_log_message([expected_log_data])

    def test_a_method_callback(self):
        class C(object):
            def callback(self, *args, **kwargs):
                pass

        with mock.patch('keystone.notifications.LOG', self.mock_log):
            notifications.register_event_callback(
                CREATED_OPERATION, 'thing', C.callback)

        expected_log_data = {
            'callback': 'keystone.tests.test_notifications.C.callback',
            'event': 'identity.thing.created'
        }
        self.verify_log_message([expected_log_data])

    def test_a_list_of_callbacks(self):
        def callback(*args, **kwargs):
            pass

        class C(object):
            def callback(self, *args, **kwargs):
                pass

        with mock.patch('keystone.notifications.LOG', self.mock_log):
            notifications.register_event_callback(
                CREATED_OPERATION, 'thing', [callback, C.callback])

        expected_log_data = [
            {
                'callback': 'keystone.tests.test_notifications.callback',
                'event': 'identity.thing.created'
            },
            {
                'callback': 'keystone.tests.test_notifications.C.callback',
                'event': 'identity.thing.created'
            },
        ]
        self.verify_log_message(expected_log_data)

    def test_an_invalid_callback(self):
        self.assertRaises(TypeError,
                          notifications.register_event_callback,
                          (CREATED_OPERATION, 'thing', object()))

    def test_an_invalid_event(self):
        def callback(*args, **kwargs):
            pass

        self.assertRaises(ValueError,
                          notifications.register_event_callback,
                          uuid.uuid4().hex,
                          'thing',
                          callback)
