import uuid

from keystone.common import wsgi
from keystone.common import manager
from keystone.common import logging
from keystone import config

CONF = config.CONF
LOG = logging.getLogger(__name__)


class AttributeMappingController(wsgi.Application):
    def __init__(self):
        self.mapping_api = Manager()
        super(AttributeMappingController)
    # Sets

    def get_mappings(self, context, mapping_id=None):
        if mapping_id:
            mapping = self.mapping_api.get_mapping(context, mapping_id)
            return {'attribute_mapping': mapping}
        return {'attribute_mapping': self.mapping_api.list_mappings()}

    def delete_mapping(self, context, mapping_id):
        self.mapping_api.delete_mapping(mapping_id)

    def create_mapping(self, context, attribute_mapping):
        self.assert_admin(context)
        mapping_id = uuid.uuid4().hex
        mapping_ref = attribute_mapping.copy()
        mapping_ref['id'] = mapping_id
        new_mapping_ref = self.mapping_api.create_mapping(
            context, mapping_id, mapping_ref)
        return {'attribute_mapping': new_mapping_ref}

    def get_mappings_from_attributes(self, context, attributes):
        mappings = self.mapping_api.list_mappings()
        matches = []
        for m in mappings:
            LOG.debug(m)
            cur_set = {}
            for org in m['org_attribute_set']['attributes']:
                cur_set[org['type']] = org['value']
            for k, v in cur_set.iteritems():
                set_matched = True
                LOG.debug(k)
                matched = False
                for k2, v2 in attributes.iteritems():
                    if k2 == k and v in v2:
                        matched = True
                        break    # break out if we matched an attribute
                if not matched:
                    set_matched = False

            if set_matched:
                tenants = []
                roles = []
                # How do we do domains??
                for os in m['os_attribute_set']['attributes']:
                    if os['type'] in "tenant":
                        tenants.append(os)
                    if os['type'] in "role":
                        roles.append(os)
                matched_sets = {"roles": roles, "tenants": tenants}
                matches.append({"matched_set": matched_sets})

        return {'mapped_attributes': matches}


class Manager(manager.Manager):

    def __init__(self):
        super(Manager, self).__init__(CONF.mapping.driver)
    # Sets

    def create_mapping(self, context, mapping_id, mapping_ref):
        return self.driver.create_mapping(context, mapping_id, mapping_ref)

    def get_mapping(self, context, mapping_id):
        return self.driver.get_mapping(mapping_id)

    def list_mappings(self):
        return self.driver.list_mappings()

    def delete_mapping(self, mapping_id):
        self.driver.delete_mapping(mapping_id)

    def get_mappings_from_attributes(self, context, attributes):
        return self.driver.get_mappings_from_attributes(attributes)
