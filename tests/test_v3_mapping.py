import uuid


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

    def assertValidServiceListResponse(self, resp, ref):
        return self.assertValidListResponse(
            resp,
            'services',
            self.assertValidService,
            ref)

    def assertValidServiceResponse(self, resp, ref):
        return self.assertValidResponse(
            resp,
            'service',
            self.assertValidService,
            ref)

    def assertValidService(self, entity, ref=None):
        self.assertIsNotNone(entity.get('type'))
        if ref:
            self.assertEqual(ref['type'], entity['type'])
        return entity


    def test_create_org_attribute_set(self):
        """POST /mapping/orgattributeset"""
        ref = self.new_org_attribute_set_ref()
        r = self.post(
            '/mapping/orgattributeset',
            body={'orgattributeset': ref})
        return True

    def test_list_org_attribute_sets(self):
        """GET /mapping/orgattributeset"""
        r = self.get('/mapping/orgattributeset')
        self.assertValidServiceListResponse(r, self.service)

    def test_get_org_attribute_set(self):
        """GET /mapping/orgattributeset/{set_id}"""
        r = self.get('/mapping/orgattributeset/%(set_id)s' % {
            'set_id': self.org_attribute_set})
        self.assertValidServiceResponse(r, self.org_attribute_set)

    def test_delete_org_attribute_set(self):
        """DELETE /mapping/org_attribute_set/{set_id}"""
        self.delete('/mapping/orgattributeset/%(set_id)s' % {
            'set_id': self.org_attribute_set_id})
