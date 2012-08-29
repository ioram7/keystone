# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import datetime
import uuid

from keystone import exception
from keystone.openstack.common import timeutils


class IdentityTests(object):
    def test_authenticate_bad_user(self):
        self.assertRaises(AssertionError,
                          self.identity_api.authenticate,
                          user_id=uuid.uuid4().hex,
                          tenant_id=self.tenant_bar['id'],
                          password=self.user_foo['password'])

    def test_authenticate_bad_password(self):
        self.assertRaises(AssertionError,
                          self.identity_api.authenticate,
                          user_id=self.user_foo['id'],
                          tenant_id=self.tenant_bar['id'],
                          password=uuid.uuid4().hex)

    def test_authenticate_bad_tenant(self):
        self.assertRaises(AssertionError,
                          self.identity_api.authenticate,
                          user_id=self.user_foo['id'],
                          tenant_id=uuid.uuid4().hex,
                          password=self.user_foo['password'])

    def test_authenticate_no_tenant(self):
        user_ref, tenant_ref, metadata_ref = self.identity_api.authenticate(
            user_id=self.user_foo['id'],
            password=self.user_foo['password'])
        # NOTE(termie): the password field is left in user_foo to make
        #               it easier to authenticate in tests, but should
        #               not be returned by the api
        self.user_foo.pop('password')
        self.assertDictEqual(user_ref, self.user_foo)
        self.assert_(tenant_ref is None)
        self.assert_(not metadata_ref)

    def test_authenticate(self):
        user_ref, tenant_ref, metadata_ref = self.identity_api.authenticate(
            user_id=self.user_foo['id'],
            tenant_id=self.tenant_bar['id'],
            password=self.user_foo['password'])
        # NOTE(termie): the password field is left in user_foo to make
        #               it easier to authenticate in tests, but should
        #               not be returned by the api
        self.user_foo.pop('password')
        self.assertDictEqual(user_ref, self.user_foo)
        self.assertDictEqual(tenant_ref, self.tenant_bar)
        self.assertDictEqual(metadata_ref, self.metadata_foobar)

    def test_authenticate_role_return(self):
        self.identity_api.add_role_to_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'], 'keystone_admin')
        user_ref, tenant_ref, metadata_ref = self.identity_api.authenticate(
            user_id=self.user_foo['id'],
            tenant_id=self.tenant_bar['id'],
            password=self.user_foo['password'])
        self.assertIn('roles', metadata_ref)
        self.assertIn('keystone_admin', metadata_ref['roles'])

    def test_authenticate_no_metadata(self):
        user = self.user_no_meta
        tenant = self.tenant_baz
        user_ref, tenant_ref, metadata_ref = self.identity_api.authenticate(
            user_id=user['id'],
            tenant_id=tenant['id'],
            password=user['password'])
        # NOTE(termie): the password field is left in user_foo to make
        #               it easier to authenticate in tests, but should
        #               not be returned by the api
        user.pop('password')
        self.assertEquals(metadata_ref, {})
        self.assertDictEqual(user_ref, user)
        self.assertDictEqual(tenant_ref, tenant)

    def test_password_hashed(self):
        user_ref = self.identity_api._get_user(self.user_foo['id'])
        self.assertNotEqual(user_ref['password'], self.user_foo['password'])

    def test_get_tenant(self):
        tenant_ref = self.identity_api.get_tenant(
            tenant_id=self.tenant_bar['id'])
        self.assertDictEqual(tenant_ref, self.tenant_bar)

    def test_get_tenant_404(self):
        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.get_tenant,
                          tenant_id=uuid.uuid4().hex)

    def test_get_tenant_by_name(self):
        tenant_ref = self.identity_api.get_tenant_by_name(
            tenant_name=self.tenant_bar['name'])
        self.assertDictEqual(tenant_ref, self.tenant_bar)

    def test_get_tenant_by_name_404(self):
        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.get_tenant,
                          tenant_id=uuid.uuid4().hex)

    def test_get_tenant_users_404(self):
        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.get_tenant_users,
                          tenant_id=uuid.uuid4().hex)

    def test_get_user(self):
        user_ref = self.identity_api.get_user(user_id=self.user_foo['id'])
        # NOTE(termie): the password field is left in user_foo to make
        #               it easier to authenticate in tests, but should
        #               not be returned by the api
        self.user_foo.pop('password')
        self.assertDictEqual(user_ref, self.user_foo)

    def test_get_user_404(self):
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.get_user,
                          user_id=uuid.uuid4().hex)

    def test_get_user_by_name(self):
        user_ref = self.identity_api.get_user_by_name(
            user_name=self.user_foo['name'])
        # NOTE(termie): the password field is left in user_foo to make
        #               it easier to authenticate in tests, but should
        #               not be returned by the api
        self.user_foo.pop('password')
        self.assertDictEqual(user_ref, self.user_foo)

    def test_get_user_by_name_404(self):
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.get_user_by_name,
                          user_name=uuid.uuid4().hex)

    def test_get_metadata(self):
        metadata_ref = self.identity_api.get_metadata(
            user_id=self.user_foo['id'],
            tenant_id=self.tenant_bar['id'])
        self.assertDictEqual(metadata_ref, self.metadata_foobar)

    def test_get_metadata_404(self):
        # FIXME(dolph): these exceptions could be more specific
        self.assertRaises(exception.NotFound,
                          self.identity_api.get_metadata,
                          user_id=uuid.uuid4().hex,
                          tenant_id=self.tenant_bar['id'])

        self.assertRaises(exception.NotFound,
                          self.identity_api.get_metadata,
                          user_id=self.user_foo['id'],
                          tenant_id=uuid.uuid4().hex)

    def test_get_role(self):
        role_ref = self.identity_api.get_role(
            role_id=self.role_keystone_admin['id'])
        role_ref_dict = dict((x, role_ref[x]) for x in role_ref)
        self.assertDictEqual(role_ref_dict, self.role_keystone_admin)

    def test_get_role_404(self):
        self.assertRaises(exception.RoleNotFound,
                          self.identity_api.get_role,
                          role_id=uuid.uuid4().hex)

    def test_create_duplicate_role_name_fails(self):
        role = {'id': 'fake1',
                'name': 'fake1name'}
        self.identity_api.create_role('fake1', role)
        role['id'] = 'fake2'
        self.assertRaises(exception.Conflict,
                          self.identity_api.create_role,
                          'fake2',
                          role)

    def test_rename_duplicate_role_name_fails(self):
        role1 = {
            'id': 'fake1',
            'name': 'fake1name'
        }
        role2 = {
            'id': 'fake2',
            'name': 'fake2name'
        }
        self.identity_api.create_role('fake1', role1)
        self.identity_api.create_role('fake2', role2)
        role1['name'] = 'fake2name'
        self.assertRaises(exception.Conflict,
                          self.identity_api.update_role,
                          'fake1',
                          role1)

    def test_create_duplicate_user_id_fails(self):
        user = {'id': 'fake1',
                'name': 'fake1',
                'password': 'fakepass',
                'tenants': ['bar']}
        self.identity_api.create_user('fake1', user)
        user['name'] = 'fake2'
        self.assertRaises(exception.Conflict,
                          self.identity_api.create_user,
                          'fake1',
                          user)

    def test_create_duplicate_user_name_fails(self):
        user = {'id': 'fake1',
                'name': 'fake1',
                'password': 'fakepass',
                'tenants': ['bar']}
        self.identity_api.create_user('fake1', user)
        user['id'] = 'fake2'
        self.assertRaises(exception.Conflict,
                          self.identity_api.create_user,
                          'fake2',
                          user)

    def test_rename_duplicate_user_name_fails(self):
        user1 = {'id': 'fake1',
                 'name': 'fake1',
                 'password': 'fakepass',
                 'tenants': ['bar']}
        user2 = {'id': 'fake2',
                 'name': 'fake2',
                 'password': 'fakepass',
                 'tenants': ['bar']}
        self.identity_api.create_user('fake1', user1)
        self.identity_api.create_user('fake2', user2)
        user2['name'] = 'fake1'
        self.assertRaises(exception.Conflict,
                          self.identity_api.update_user,
                          'fake2',
                          user2)

    def test_update_user_id_fails(self):
        user = {'id': 'fake1',
                'name': 'fake1',
                'password': 'fakepass',
                'tenants': ['bar']}
        self.identity_api.create_user('fake1', user)
        user['id'] = 'fake2'
        self.assertRaises(exception.ValidationError,
                          self.identity_api.update_user,
                          'fake1',
                          user)
        user_ref = self.identity_api.get_user('fake1')
        self.assertEqual(user_ref['id'], 'fake1')
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.get_user,
                          'fake2')

    def test_create_duplicate_tenant_id_fails(self):
        tenant = {'id': 'fake1', 'name': 'fake1'}
        self.identity_api.create_tenant('fake1', tenant)
        tenant['name'] = 'fake2'
        self.assertRaises(exception.Conflict,
                          self.identity_api.create_tenant,
                          'fake1',
                          tenant)

    def test_create_duplicate_tenant_name_fails(self):
        tenant = {'id': 'fake1', 'name': 'fake'}
        self.identity_api.create_tenant('fake1', tenant)
        tenant['id'] = 'fake2'
        self.assertRaises(exception.Conflict,
                          self.identity_api.create_tenant,
                          'fake1',
                          tenant)

    def test_rename_duplicate_tenant_name_fails(self):
        tenant1 = {'id': 'fake1', 'name': 'fake1'}
        tenant2 = {'id': 'fake2', 'name': 'fake2'}
        self.identity_api.create_tenant('fake1', tenant1)
        self.identity_api.create_tenant('fake2', tenant2)
        tenant2['name'] = 'fake1'
        self.assertRaises(exception.Error,
                          self.identity_api.update_tenant,
                          'fake2',
                          tenant2)

    def test_update_tenant_id_does_nothing(self):
        tenant = {'id': 'fake1', 'name': 'fake1'}
        self.identity_api.create_tenant('fake1', tenant)
        tenant['id'] = 'fake2'
        self.identity_api.update_tenant('fake1', tenant)
        tenant_ref = self.identity_api.get_tenant('fake1')
        self.assertEqual(tenant_ref['id'], 'fake1')
        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.get_tenant,
                          'fake2')

    def test_add_duplicate_role_grant(self):
        roles_ref = self.identity_api.get_roles_for_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'])
        self.assertNotIn('keystone_admin', roles_ref)
        self.identity_api.add_role_to_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'], 'keystone_admin')
        self.assertRaises(exception.Conflict,
                          self.identity_api.add_role_to_user_and_tenant,
                          self.user_foo['id'],
                          self.tenant_bar['id'],
                          'keystone_admin')

    def test_get_role_by_user_and_tenant(self):
        roles_ref = self.identity_api.get_roles_for_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'])
        self.assertNotIn('keystone_admin', roles_ref)
        self.identity_api.add_role_to_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'], 'keystone_admin')
        roles_ref = self.identity_api.get_roles_for_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'])
        self.assertIn('keystone_admin', roles_ref)
        self.assertNotIn('useless', roles_ref)

        self.identity_api.add_role_to_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'], 'useless')
        roles_ref = self.identity_api.get_roles_for_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'])
        self.assertIn('keystone_admin', roles_ref)
        self.assertIn('useless', roles_ref)

    def test_get_roles_for_user_and_tenant_404(self):
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.get_roles_for_user_and_tenant,
                          uuid.uuid4().hex,
                          self.tenant_bar['id'])

        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.get_roles_for_user_and_tenant,
                          self.user_foo['id'],
                          uuid.uuid4().hex)

    def test_add_role_to_user_and_tenant_404(self):
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.add_role_to_user_and_tenant,
                          uuid.uuid4().hex,
                          self.tenant_bar['id'],
                          'keystone_admin')

        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.add_role_to_user_and_tenant,
                          self.user_foo['id'],
                          uuid.uuid4().hex,
                          'keystone_admin')

        self.assertRaises(exception.RoleNotFound,
                          self.identity_api.add_role_to_user_and_tenant,
                          self.user_foo['id'],
                          self.tenant_bar['id'],
                          uuid.uuid4().hex)

    def test_remove_role_from_user_and_tenant(self):
        self.identity_api.add_role_to_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'], 'useless')
        self.identity_api.remove_role_from_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'], 'useless')
        roles_ref = self.identity_api.get_roles_for_user_and_tenant(
            self.user_foo['id'], self.tenant_bar['id'])
        self.assertNotIn('useless', roles_ref)
        self.assertRaises(exception.NotFound,
                          self.identity_api.remove_role_from_user_and_tenant,
                          self.user_foo['id'],
                          self.tenant_bar['id'],
                          'useless')

    def test_role_crud(self):
        role = {'id': uuid.uuid4().hex, 'name': uuid.uuid4().hex}
        self.identity_api.create_role(role['id'], role)
        role_ref = self.identity_api.get_role(role['id'])
        role_ref_dict = dict((x, role_ref[x]) for x in role_ref)
        self.assertDictEqual(role_ref_dict, role)

        role['name'] = uuid.uuid4().hex
        self.identity_api.update_role(role['id'], role)
        role_ref = self.identity_api.get_role(role['id'])
        role_ref_dict = dict((x, role_ref[x]) for x in role_ref)
        self.assertDictEqual(role_ref_dict, role)

        self.identity_api.delete_role(role['id'])
        self.assertRaises(exception.RoleNotFound,
                          self.identity_api.get_role,
                          role['id'])

    def test_update_role_404(self):
        role = {'id': uuid.uuid4().hex, 'name': uuid.uuid4().hex}
        self.assertRaises(exception.RoleNotFound,
                          self.identity_api.update_role,
                          role['id'],
                          role)

    def test_add_user_to_tenant(self):
        self.identity_api.add_user_to_tenant(self.tenant_bar['id'],
                                             self.user_foo['id'])
        tenants = self.identity_api.get_tenants_for_user(self.user_foo['id'])
        self.assertIn(self.tenant_bar['id'], tenants)

    def test_add_user_to_tenant_404(self):
        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.add_user_to_tenant,
                          uuid.uuid4().hex,
                          self.user_foo['id'])

        self.assertRaises(exception.UserNotFound,
                          self.identity_api.add_user_to_tenant,
                          self.tenant_bar['id'],
                          uuid.uuid4().hex)

    def test_remove_user_from_tenant(self):
        self.identity_api.add_user_to_tenant(self.tenant_bar['id'],
                                             self.user_foo['id'])
        self.identity_api.remove_user_from_tenant(self.tenant_bar['id'],
                                                  self.user_foo['id'])
        tenants = self.identity_api.get_tenants_for_user(self.user_foo['id'])
        self.assertNotIn(self.tenant_bar['id'], tenants)

    def test_remove_user_from_tenant_404(self):
        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.remove_user_from_tenant,
                          uuid.uuid4().hex,
                          self.user_foo['id'])

        self.assertRaises(exception.UserNotFound,
                          self.identity_api.remove_user_from_tenant,
                          self.tenant_bar['id'],
                          uuid.uuid4().hex)

        self.assertRaises(exception.NotFound,
                          self.identity_api.remove_user_from_tenant,
                          self.tenant_baz['id'],
                          self.user_foo['id'])

    def test_get_tenants_for_user_404(self):
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.get_tenants_for_user,
                          uuid.uuid4().hex)

    def test_update_tenant_404(self):
        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.update_tenant,
                          uuid.uuid4().hex,
                          dict())

    def test_delete_tenant_404(self):
        self.assertRaises(exception.TenantNotFound,
                          self.identity_api.delete_tenant,
                          uuid.uuid4().hex)

    def test_update_user_404(self):
        user_id = uuid.uuid4().hex
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.update_user,
                          user_id,
                          {'id': user_id})

    def test_delete_user_with_tenant_association(self):
        user = {'id': uuid.uuid4().hex,
                'name': uuid.uuid4().hex,
                'password': uuid.uuid4().hex}
        self.identity_api.create_user(user['id'], user)
        self.identity_api.add_user_to_tenant(self.tenant_bar['id'],
                                             user['id'])
        self.identity_api.delete_user(user['id'])
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.get_tenants_for_user,
                          user['id'])

    def test_delete_user_404(self):
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.delete_user,
                          uuid.uuid4().hex)

    def test_delete_role_404(self):
        self.assertRaises(exception.RoleNotFound,
                          self.identity_api.delete_role,
                          uuid.uuid4().hex)

    def test_create_tenant_long_name_fails(self):
        tenant = {'id': 'fake1', 'name': 'a' * 65}
        self.assertRaises(exception.ValidationError,
                          self.identity_api.create_tenant,
                          tenant['id'],
                          tenant)

    def test_create_tenant_blank_name_fails(self):
        tenant = {'id': 'fake1', 'name': ''}
        self.assertRaises(exception.ValidationError,
                          self.identity_api.create_tenant,
                          tenant['id'],
                          tenant)

    def test_create_tenant_invalid_name_fails(self):
        tenant = {'id': 'fake1', 'name': None}
        self.assertRaises(exception.ValidationError,
                          self.identity_api.create_tenant,
                          tenant['id'],
                          tenant)
        tenant = {'id': 'fake1', 'name': 123}
        self.assertRaises(exception.ValidationError,
                          self.identity_api.create_tenant,
                          tenant['id'],
                          tenant)

    def test_update_tenant_blank_name_fails(self):
        tenant = {'id': 'fake1', 'name': 'fake1'}
        self.identity_api.create_tenant('fake1', tenant)
        tenant['name'] = ''
        self.assertRaises(exception.ValidationError,
                          self.identity_api.update_tenant,
                          tenant['id'],
                          tenant)

    def test_update_tenant_long_name_fails(self):
        tenant = {'id': 'fake1', 'name': 'fake1'}
        self.identity_api.create_tenant('fake1', tenant)
        tenant['name'] = 'a' * 65
        self.assertRaises(exception.ValidationError,
                          self.identity_api.update_tenant,
                          tenant['id'],
                          tenant)

    def test_update_tenant_invalid_name_fails(self):
        tenant = {'id': 'fake1', 'name': 'fake1'}
        self.identity_api.create_tenant('fake1', tenant)
        tenant['name'] = None
        self.assertRaises(exception.ValidationError,
                          self.identity_api.update_tenant,
                          tenant['id'],
                          tenant)

        tenant['name'] = 123
        self.assertRaises(exception.ValidationError,
                          self.identity_api.update_tenant,
                          tenant['id'],
                          tenant)

    def test_create_user_long_name_fails(self):
        user = {'id': 'fake1', 'name': 'a' * 65}
        self.assertRaises(exception.ValidationError,
                          self.identity_api.create_user,
                          'fake1',
                          user)

    def test_create_user_blank_name_fails(self):
        user = {'id': 'fake1', 'name': ''}
        self.assertRaises(exception.ValidationError,
                          self.identity_api.create_user,
                          'fake1',
                          user)

    def test_create_user_invalid_name_fails(self):
        user = {'id': 'fake1', 'name': None}
        self.assertRaises(exception.ValidationError,
                          self.identity_api.create_user,
                          'fake1',
                          user)

        user = {'id': 'fake1', 'name': 123}
        self.assertRaises(exception.ValidationError,
                          self.identity_api.create_user,
                          'fake1',
                          user)

    def test_update_user_long_name_fails(self):
        user = {'id': 'fake1', 'name': 'fake1'}
        self.identity_api.create_user('fake1', user)
        user['name'] = 'a' * 65
        self.assertRaises(exception.ValidationError,
                          self.identity_api.update_user,
                          'fake1',
                          user)

    def test_update_user_blank_name_fails(self):
        user = {'id': 'fake1', 'name': 'fake1'}
        self.identity_api.create_user('fake1', user)
        user['name'] = ''
        self.assertRaises(exception.ValidationError,
                          self.identity_api.update_user,
                          'fake1',
                          user)

    def test_update_user_invalid_name_fails(self):
        user = {'id': 'fake1', 'name': 'fake1'}
        self.identity_api.create_user('fake1', user)

        user['name'] = None
        self.assertRaises(exception.ValidationError,
                          self.identity_api.update_user,
                          'fake1',
                          user)

        user['name'] = 123
        self.assertRaises(exception.ValidationError,
                          self.identity_api.update_user,
                          'fake1',
                          user)


class TokenTests(object):
    def test_token_crud(self):
        token_id = uuid.uuid4().hex
        data = {'id': token_id, 'id_hash': token_id, 'a': 'b'}
        data_ref = self.token_api.create_token(token_id, data)
        expires = data_ref.pop('expires')
        self.assertTrue(isinstance(expires, datetime.datetime))
        self.assertDictEqual(data_ref, data)

        new_data_ref = self.token_api.get_token(token_id)
        expires = new_data_ref.pop('expires')
        self.assertTrue(isinstance(expires, datetime.datetime))
        self.assertEquals(new_data_ref, data)

        self.token_api.delete_token(token_id)
        self.assertRaises(exception.TokenNotFound,
                          self.token_api.get_token, token_id)
        self.assertRaises(exception.TokenNotFound,
                          self.token_api.delete_token, token_id)

    def test_get_token_404(self):
        self.assertRaises(exception.TokenNotFound,
                          self.token_api.get_token,
                          uuid.uuid4().hex)

    def test_delete_token_404(self):
        self.assertRaises(exception.TokenNotFound,
                          self.token_api.delete_token,
                          uuid.uuid4().hex)

    def test_expired_token(self):
        token_id = uuid.uuid4().hex
        expire_time = timeutils.utcnow() - datetime.timedelta(minutes=1)
        data = {'id_hash': token_id, 'id': token_id, 'a': 'b',
                'expires': expire_time}
        data_ref = self.token_api.create_token(token_id, data)
        self.assertDictEqual(data_ref, data)
        self.assertRaises(exception.TokenNotFound,
                          self.token_api.get_token, token_id)

    def test_null_expires_token(self):
        token_id = uuid.uuid4().hex
        data = {'id': token_id, 'id_hash': token_id, 'a': 'b', 'expires': None}
        data_ref = self.token_api.create_token(token_id, data)
        self.assertDictEqual(data_ref, data)
        new_data_ref = self.token_api.get_token(token_id)
        self.assertEqual(data_ref, new_data_ref)

    def check_list_revoked_tokens(self, token_ids):
        revoked_ids = [x['id'] for x in self.token_api.list_revoked_tokens()]
        for token_id in token_ids:
            self.assertIn(token_id, revoked_ids)

    def delete_token(self):
        token_id = uuid.uuid4().hex
        data = {'id_hash': token_id, 'id': token_id, 'a': 'b'}
        data_ref = self.token_api.create_token(token_id, data)
        self.token_api.delete_token(token_id)
        return token_id

    def test_list_revoked_tokens_returns_empty_list(self):
        revoked_ids = [x['id'] for x in self.token_api.list_revoked_tokens()]
        self.assertEqual(revoked_ids, [])

    def test_list_revoked_tokens_for_single_token(self):
        self.check_list_revoked_tokens([self.delete_token()])

    def test_list_revoked_tokens_for_multiple_tokens(self):
        self.check_list_revoked_tokens([self.delete_token()
                                        for x in xrange(2)])


class CatalogTests(object):
    def test_service_crud(self):
        new_service = {
            'id': uuid.uuid4().hex,
            'type': uuid.uuid4().hex,
            'name': uuid.uuid4().hex,
            'description': uuid.uuid4().hex,
        }
        res = self.catalog_api.create_service(
            new_service['id'],
            new_service.copy())
        self.assertDictEqual(res, new_service)

        service_id = new_service['id']
        self.catalog_api.delete_service(service_id)
        self.assertRaises(exception.ServiceNotFound,
                          self.catalog_man.delete_service, {}, service_id)
        self.assertRaises(exception.ServiceNotFound,
                          self.catalog_man.get_service, {}, service_id)

    def test_get_service_404(self):
        self.assertRaises(exception.ServiceNotFound,
                          self.catalog_man.get_service,
                          {},
                          uuid.uuid4().hex)

    def test_delete_service_404(self):
        self.assertRaises(exception.ServiceNotFound,
                          self.catalog_man.delete_service,
                          {},
                          uuid.uuid4().hex)

    def test_create_endpoint_404(self):
        endpoint = {
            'id': uuid.uuid4().hex,
            'service_id': uuid.uuid4().hex,
        }
        self.assertRaises(exception.ServiceNotFound,
                          self.catalog_api.create_endpoint,
                          endpoint['id'],
                          endpoint)

    def test_get_endpoint_404(self):
        self.assertRaises(exception.EndpointNotFound,
                          self.catalog_api.get_endpoint,
                          uuid.uuid4().hex)

    def test_delete_endpoint_404(self):
        self.assertRaises(exception.EndpointNotFound,
                          self.catalog_api.delete_endpoint,
                          uuid.uuid4().hex)

    def test_service_list(self):
        services = self.catalog_api.list_services()
        self.assertEqual(3, len(services))
