import datetime
import uuid

from keystone.openstack.common import timeutils

import test_v3


class MappingTestCase(test_v3.RestfulTestCase):
    """Test mapping CRUD"""

    def setUp(self):
        super(MappingTestCase, self).setUp()
        self.org_attribute_set_id = uuid.uuid4().hex
        self.org_attribute_set = self.new_org_attribute_set_ref()
        self.org_attribute_set['id'] = self.org_attribute_set_id
        self.mapping_api.create_org_attribute_set(
            self.org_attribute_set_id,
            self.org_attribute_set.copy())

        self.os_attribute_set_id = uuid.uuid4().hex
        self.os_attribute_set = self.new_os_attribute_set_ref()
        self.os_attribute_set['id'] = self.os_attribute_set_id
        self.mapping_api.create_os_attribute_set(
            self.os_attribute_set_id,
            self.os_attribute_set.copy())

        self.org_attribute_id = uuid.uuid4().hex
        self.org_attribute = self.new_org_attribute_ref()
        self.org_attribute['id'] = self.org_attribute_id
        self.mapping_api.create_org_attribute(
            self.org_attribute_id,
            self.org_attribute.copy())

        self.role_id = uuid.uuid4().hex
        self.role = self.new_role_ref()
        self.role['id'] = self.role_id
        self.identity_api.create_role(
            self.role_id,
            self.role.copy())

        self.admin_role_id = uuid.uuid4().hex
        self.admin_role = self.new_role_ref()
        self.admin_role['id'] = self.admin_role_id
        self.identity_api.create_role(
            self.admin_role_id,
            self.admin_role.copy())

        self.service_id = uuid.uuid4().hex
        self.service = self.new_service_ref()
        self.service['id'] = self.service_id
        self.catalog_api.create_service(
            self.service_id,
            self.service.copy())

        self.attribute_mapping_id = uuid.uuid4().hex
        self.attribute_mapping = self.new_attribute_mapping_ref()
        self.attribute_mapping['id'] = self.attribute_mapping_id
        os_set = self.os_attribute_set_id
        org_set = self.org_attribute_set_id
        self.attribute_mapping['org_attribute_set_id'] = org_set
        self.attribute_mapping['os_attribute_set_id'] = os_set
        self.mapping_api.create_attribute_set_mapping(
            self.attribute_mapping_id,
            self.attribute_mapping.copy())

        self.attribute_mapping_detailed = self.new_attribute_mapping_ref()
        self.attribute_mapping_detailed['id'] = self.attribute_mapping_id
        self.org_attribute_set_detailed = self.org_attribute_set.copy()
        attributes = []
        attributes.append(self.org_attribute)
        self.org_attribute_set_detailed["attributes"] = attributes
        self.os_attribute_set_detailed = self.os_attribute_set.copy()
        attributes = []
        attributes.append(
            {"id": self.role_id, "type": "role", "value": self.role["name"]})
        self.os_attribute_set_detailed["attributes"] = attributes
        org_set = self.org_attribute_set_detailed
        self.attribute_mapping_detailed["org_attribute_set"] = org_set
        os_set = self.os_attribute_set_detailed
        self.attribute_mapping_detailed["os_attribute_set"] = os_set

    # Org Attribute set validation

    def assertValidOrgAttributeSetListResponse(self, resp, ref):
        return self.assertValidListResponse(
            resp,
            'org_attribute_sets',
            self.assertValidOrgAttributeSet,
            ref)

    def assertValidOrgAttributeSetResponse(self, resp, ref):
        return self.assertValidResponse(
            resp,
            'org_attribute_set',
            self.assertValidOrgAttributeSet,
            ref)

    def assertValidOrgAttributeSet(self, entity, ref=None):
        self.assertIsNotNone(entity.get('name'))
        if ref:
            self.assertEqual(ref['name'], entity['name'])
        return entity

    def test_create_org_attribute_set(self):
        """POST /org_attribute_sets"""
        ref = self.new_org_attribute_set_ref()
        r = self.post(
            '/org_attribute_sets',
            body={'org_attribute_set': ref})
        return self.assertValidOrgAttributeSetResponse(r, ref)

    def test_list_org_attribute_sets(self):
        """GET /org_attribute_sets"""
        r = self.get('/org_attribute_sets')
        self.assertValidOrgAttributeSetListResponse(r, self.org_attribute_set)

    def test_get_org_attribute_set(self):
        """GET /org_attribute_sets/{org_attribute_set_id}"""
        r = self.get('/org_attribute_sets/%(set_id)s' % {
            'set_id': self.org_attribute_set_id})
        self.assertValidOrgAttributeSetResponse(r, self.org_attribute_set)

    def test_delete_org_attribute_set(self):
        """DELETE /org_attribute_sets/{org_attribute_set_id}"""
        self.delete('/org_attribute_sets/%(set_id)s' % {
            'set_id': self.org_attribute_set_id})

    def test_list_attributes_in_org_set(self):
        """GET /org_attribute_sets/{set_id}/attributes"""
        self.get('/org_attribute_sets/%(set_id)s/attributes' % {
            'set_id': self.org_attribute_set_id})

    def test_add_attribute_to_org_set(self):
        """PUT /org_attribute_sets/{set_id}/attributes/{attribute_id}"""
        url = '/org_attribute_sets/%(set_id)s/' % {
              'set_id': self.org_attribute_set_id}
        url += 'attributes/%(attribute_id)s' % {
            'attribute_id': self.org_attribute_id}
        self.put(url)

    def test_check_attribute_in_org_set(self):
        """HEAD /org_attribute_sets/{set_id}/attributes/{attribute_id}"""
        url = '/org_attribute_sets/%(set_id)s/' % {
              'set_id': self.org_attribute_set_id}
        url += 'attributes/%(attribute_id)s' % {
            'attribute_id': self.org_attribute_id}
        self.put(url)
        self.head(url)

    def test_remove_attribute_from_org_set(self):
        """DELETE /org_attribute_sets/{set_id}/attributes/{attribute_id}"""
        url = '/org_attribute_sets/%(set_id)s/' % {
              'set_id': self.org_attribute_set_id}
        url += 'attributes/%(attribute_id)s' % {
            'attribute_id': self.org_attribute_id}
        self.put(url)
        self.delete(url)

    # Os Attribute Set validation

    def assertValidOsAttributeSetListResponse(self, resp, ref):
        return self.assertValidListResponse(
            resp,
            'os_attribute_sets',
            self.assertValidOsAttributeSet,
            ref)

    def assertValidOsAttributeSetResponse(self, resp, ref):
        return self.assertValidResponse(
            resp,
            'os_attribute_set',
            self.assertValidOsAttributeSet,
            ref)

    def assertValidOsAttributeSet(self, entity, ref=None):
        self.assertIsNotNone(entity.get('name'))
        if ref:
            self.assertEqual(ref['name'], entity['name'])
        return entity

    def test_create_os_attribute_set(self):
        """POST /os_attribute_sets"""
        ref = self.new_os_attribute_set_ref()
        r = self.post(
            '/os_attribute_sets',
            body={'os_attribute_set': ref})
        return self.assertValidOsAttributeSetResponse(r, ref)

    def test_list_os_attribute_sets(self):
        """GET /os_attribute_sets"""
        r = self.get('/os_attribute_sets')
        self.assertValidOsAttributeSetListResponse(r, self.os_attribute_set)

    def test_get_os_attribute_set(self):
        """GET /os_attribute_sets/{os_attribute_set_id}"""
        r = self.get('/os_attribute_sets/%(set_id)s' % {
            'set_id': self.os_attribute_set_id})
        self.assertValidOsAttributeSetResponse(r, self.os_attribute_set)

    def test_delete_os_attribute_set(self):
        """DELETE /os_attribute_sets/{os_attribute_set_id}"""
        self.delete('/os_attribute_sets/%(set_id)s' % {
            'set_id': self.os_attribute_set_id})

    def test_list_attributes_in_os_set(self):
        """GET /os_attribute_sets/{os_attribute_set_id/attributes"""
        url = '/os_attribute_sets/%(os_attribute_set_id)s/attributes' % {
            'os_attribute_set_id': self.os_attribute_set_id}
        self.get(url)

    def test_add_attribute_to_os_set(self):
        """PUT /os_attribute_sets/{set_id}/attributes/{attribute_id}"""
        url = '/os_attribute_sets/%(set_id)s/' % {
              'set_id': self.os_attribute_set_id}
        url += 'attributes/%(attribute_id)s?type=role' % {
            'attribute_id': self.role_id}
        self.put(url)

    def test_remove_attribute_from_os_set(self):
        """DELETE /os_attribute_sets/{set_id}/attributes/{attribute_id}"""
        url = '/os_attribute_sets/%(set_id)s/' % {
              'set_id': self.os_attribute_set_id}
        url += 'attributes/%(attribute_id)s?type=role' % {
            'attribute_id': self.role_id}
        self.put(url)
        self.delete(url)

    def test_check_attribute_in_os_set(self):
        """HEAD /os_attribute_sets/{set_id}/attributes/{attribute_id}"""
        url = '/os_attribute_sets/%(set_id)s/' % {
              'set_id': self.os_attribute_set_id}
        url += 'attributes/%(attribute_id)s?type=role' % {
            'attribute_id': self.role_id}
        self.put(url)
        self.head(url)

    # Org Attribute validation

    def assertValidOrgAttributeListResponse(self, resp, ref):
        return self.assertValidListResponse(
            resp,
            'org_attributes',
            self.assertValidOrgAttribute,
            ref)

    def assertValidOrgAttributeResponse(self, resp, ref):
        return self.assertValidResponse(
            resp,
            'org_attribute',
            self.assertValidOrgAttribute,
            ref)

    def assertValidOrgAttribute(self, entity, ref=None):
        self.assertIsNotNone(entity.get('name'))
        if ref:
            self.assertEqual(ref['name'], entity['name'])
        return entity

    def test_create_org_attribute(self):
        """POST /org_attributes"""
        ref = self.new_org_attribute_ref()
        r = self.post(
            '/org_attributes',
            body={'org_attribute': ref})
        return self.assertValidOrgAttributeResponse(r, ref)

    def test_list_org_attributes(self):
        """GET /org_attributes"""
        r = self.get('/org_attributes')
        self.assertValidOrgAttributeListResponse(r, self.org_attribute)

    def test_get_org_attribute(self):
        """GET /org_attributes/{org_attribute_id}"""
        r = self.get('/org_attributes/%(set_id)s' % {
            'set_id': self.org_attribute_id})
        self.assertValidOrgAttributeResponse(r, self.org_attribute)

    def test_delete_org_attribute(self):
        """DELETE /org_attributes/{org_attribute_id}"""
        self.delete('/org_attributes/%(set_id)s' % {
            'set_id': self.org_attribute_id})

    def test_list_issuers_for_attribute(self):
        """GET /org_attributes/{attribute_id}/issuers"""
        self.get('/org_attributes/%(att_id)s/issuers' % {
            'att_id': self.org_attribute_id})

    def test_add_issuer_to_attribute(self):
        """PUT /org_attributes/{attribute_id}/issuers/{service_id}"""
        url = '/org_attributes/%(att_id)s/' % {
              'att_id': self.org_attribute_id}
        url += 'issuers/%(service_id)s' % {
            'service_id': self.service_id}
        self.put(url)

    def test_check_attribute_can_be_issued(self):
        """HEAD /org_attributes/{attribute_id}/issuers/{service_id}"""
        url = '/org_attributes/%(att_id)s/' % {
              'att_id': self.org_attribute_id}
        url += 'issuers/%(service_id)s' % {
            'service_id': self.service_id}
        self.put(url)
        self.head(url)

    def test_remove_issuer_from_attribute(self):
        """DELETE /org_attributes/{attribute_id}/issuers/{service_id}"""
        url = '/org_attributes/%(att_id)s/' % {
              'att_id': self.org_attribute_id}
        url += 'issuers/%(service_id)s' % {
            'service_id': self.service_id}
        self.put(url)
        self.delete(url)

    # attribute mapping validation

    def assertValidAttributeMappingListResponse(self, resp, ref):
        return self.assertValidListResponse(
            resp,
            'attribute_set_mappings',
            self.assertValidAttributeMapping,
            ref)

    def assertValidAttributeMappingResponse(self, resp, ref):
        return self.assertValidResponse(
            resp,
            'attribute_set_mapping',
            self.assertValidAttributeMapping,
            ref)

    def assertValidAttributeMapping(self, entity, ref=None):
        self.assertIsNotNone(entity.get('name'))
        if ref:
            self.assertEqual(ref['name'], entity['name'])
        return entity

    def test_create_attribute_set_mapping(self):
        """POST /attribute_set_mappings"""
        ref = self.new_attribute_mapping_ref()
        ref['org_attribute_set_id'] = self.org_attribute_set_id
        ref['os_attribute_set_id'] = self.os_attribute_set_id
        r = self.post(
            '/attribute_set_mappings',
            body={'attribute_set_mapping': ref})
        return self.assertValidAttributeMappingResponse(r, ref)

    def test_list_attribute_set_mappings(self):
        """GET /attribute_set_mappings"""
        r = self.get('/attribute_set_mappings')
        self.assertValidAttributeMappingListResponse(r, self.attribute_mapping)

    def test_get_attribute_set_mapping(self):
        """GET /attribute_set_mappings/{attribute_set_mapping_id}"""
        r = self.get('/attribute_set_mappings/%(mapping_id)s' % {
            'mapping_id': self.attribute_mapping_id})
        self.assertValidAttributeMappingResponse(r, self.attribute_mapping)

    def test_delete_attribute_set_mapping(self):
        """DELETE /attribute_set_mappings/{attribute_set_mapping_id}"""
        self.delete('/attribute_set_mappings/%(mapping_id)s' % {
            'mapping_id': self.attribute_mapping_id})

    def assertValidAttributeMappingDetailedListResponse(self, resp, ref):
        entities = resp.body.get("attribute_mappings")
        self.assertIsNotNone(entities)
        self.assertTrue(len(entities))
        for entity in entities:
            self.assertIsNotNone(entity)
            self.assertValidAttributeMappingDetailed(entity)
        if ref:
            entity = [x for x in entities if x['id'] == ref['id']][0]
            self.assertValidAttributeMappingDetailed(entity, ref)
        return entities

    def assertValidAttributeMappingDetailedResponse(self, resp, ref):
        entity = resp.body.get("attribute_mapping")
        self.assertIsNotNone(entity)
        self.assertValidAttributeMappingDetailed(entity)
        if ref:
            self.assertValidAttributeMappingDetailed(entity, ref)
        return entity

    def assertValidAttributeMappingDetailed(self, entity, ref=None):
        self.assertIsNotNone(entity.get('os_attribute_set'))
        self.assertIsNotNone(entity.get('org_attribute_set'))
        if ref:
            self.assertEqual(ref['id'], entity['id'])
        return entity

    def test_list_attribute_mappings(self):
        """GET /attribute_mappings"""
        url = '/org_attribute_sets/%(set_id)s/' % {
              'set_id': self.org_attribute_set_id}
        url += 'attributes/%(attribute_id)s' % {
            'attribute_id': self.org_attribute_id}
        self.put(url)
        url = '/os_attribute_sets/%(set_id)s/' % {
              'set_id': self.os_attribute_set_id}
        url += 'attributes/%(attribute_id)s?type=role' % {
            'attribute_id': self.role_id}
        self.put(url)
        r = self.get('/attribute_mappings')
        self.assertValidAttributeMappingDetailedListResponse(
            r, self.attribute_mapping_detailed)

    def test_get_attribute_mapping(self):
        """GET /attribute_mappings/{mapping_id}"""
        url = '/org_attribute_sets/%(set_id)s/' % {
              'set_id': self.org_attribute_set_id}
        url += 'attributes/%(attribute_id)s' % {
            'attribute_id': self.org_attribute_id}
        self.put(url)
        url = '/os_attribute_sets/%(set_id)s/' % {
              'set_id': self.os_attribute_set_id}
        url += 'attributes/%(attribute_id)s?type=role' % {
            'attribute_id': self.role_id}
        self.put(url)
        r = self.get('/attribute_mappings/%(mapping_id)s' % {
            'mapping_id': self.attribute_mapping_id})
        self.assertValidAttributeMappingDetailedResponse(
            r, self.attribute_mapping_detailed)

    def test_delete_attribute_mapping(self):
        """DELETE /attribute_mappings/{mapping_id}"""
        r = self.delete('/attribute_mappings/%(mapping_id)s' % {
            'mapping_id': self.attribute_mapping_id})

    def test_create_attribute_mapping(self):
        """POST /attribute_mappings"""
        org_set = {}
        org_set['name'] = 'some name'
        org_set['description'] = 'some description'
        org_set['attributes'] = [self.org_attribute_id]
        #org_set['attributes'].append(self.org_attribute_id)

        os_set = {}
        os_set['name'] = 'some name'
        os_set['description'] = 'some description'
        os_set['attributes'] = {}
        os_set['attributes'][self.role_id] = 'role'

        mapping = {}
        mapping['org_attribute_set'] = org_set
        mapping['os_attribute_set'] = os_set

        r = self.post('/attribute_mappings',
                      body={'attribute_mapping': mapping})
        self.assertValidAttributeMappingDetailedResponse(
            r, None)

    def test_create_user_with_validity_date(self):
        """POST /users"""
        domain = self.new_domain_ref()
        self.post('/domains', body={"domain":domain})
        user = self.new_user_ref(domain["id"])
        expires = timeutils.utcnow() + datetime.timedelta(minutes=1)
        user['expires'] = expires
        r = self.post('/users', body={"user":user})
        print r.body
        self.assertIsNotNone(r.body.get("user")["expires"])

    def test_get_expired_users(self):
        """"""
        domain = self.new_domain_ref()
        self.post('/domains', body={"domain":domain})
        user = self.new_user_ref(domain["id"])
        expires = timeutils.utcnow() - datetime.timedelta(minutes=1)
        user['expires'] = expires
        r = self.post('/users', body={"user":user})
        users = self.identity_api.get_expired_users()
        print users
        self.assertTrue(len(users))

    def test_add_admin_permission(self):
        """PUT /admin-role-permissions/{admin_role_id}/permissions/roles/{role_id}"""
        url = '/admin-role-permissions/%(role_id)s/' % {
              'role_id': self.admin_role_id}
        url += 'permissions/roles/%(role_id)s' % {
            'role_id': self.role_id}
        self.put(url)

    def test_list_admin_role_permissions(self):
        """GET /admin-role-permissions/{admin_role_id}/permissions"""
        url = '/admin-role-permissions/%(role_id)s/permissions' % {
              'role_id': self.admin_role_id}
        self.get(url)

    def test_revoke_admin_permission(self):
        """DELETE /admin-role-permissions/{admin_role_id}/permissions/roles/{role_id}"""
        url = '/admin-role-permissions/%(role_id)s/' % {
              'role_id': self.admin_role_id}
        url += 'permissions/roles/%(role_id)s' % {
            'role_id': self.role_id}
        self.put(url)
        self.delete(url)

    def test_check_admin_permission(self):
        """HEAD /admin-role-permissions/{admin_role_id}/permissions/roles/{role_id}"""
        url = '/admin-role-permissions/%(role_id)s/' % {
              'role_id': self.admin_role_id}
        url += 'permissions/roles/%(role_id)s' % {
            'role_id': self.role_id}
        self.put(url)
        self.head(url)
