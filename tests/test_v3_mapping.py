import uuid

import test_v3


class MappingTestCase(test_v3.RestfulTestCase):
    """Test mapping CRUD"""

    def setUp(self):
        super(MappingTestCase, self).setUp()
        self.org_attribute_set_id = uuid.uuid4().hex
        self.org_attribute_set = self.new_service_ref()
        self.org_attribute_set['id'] = self.org_attribute_set_id
        self.mapping_api.create_org_attribute_set(
            self.org_attribute_set_id,
            self.org_attribute_set.copy())

    # service validation

    def assertValidOrgAttributeListResponse(self, resp, ref):
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
        return self.assertValidOrgAttributeSet(r, self.org_attribute_set)

    def test_list_org_attribute_sets(self):
        """GET /org_attribute_sets"""
        r = self.get('/org_attribute_sets')
        self.assertValidOrgAttributeSetListResponse(r)

    def test_get_org_attribute_set(self):
        """GET /org_attribute_sets/{org_attribute_set_id}"""
        r = self.get('/org_attribute_sets/%(set_id)s' % {
            'set_id': self.org_attribute_set_id})
        self.assertValidOrgAttributeSetResponse(r)

    def test_delete_org_attribute_set(self):
        """DELETE /org_attribute_sets/{org_attribute_set_id}"""
        self.delete('/org_attribute_sets/%(set_id)s' % {
            'set_id': self.org_attribute_set_id})
