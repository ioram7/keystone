import uuid

from keystone.common import wsgi
from keystone.common import manager
from keystone.common import logging
from keystone import config

CONF = config.CONF
LOG = logging.getLogger(__name__)


class Manager(manager.Manager):

    def __init__(self):
        super(Manager, self).__init__(CONF.mapping.driver)
    # Sets
    def create_os_set(self, context, set_id, set_ref):
        return self.driver.create_os_attribute_set(context, set_id, set_ref)

    def get_os_set(self, context, set_id):
        return self.driver.get_os_set(set_id)

    def list_os_sets(self):
        return self.driver.list_os_sets()

    def delete_os_set(self, set_id):
        self.driver.delete_os_set(set_id)

    # Associations
    def create_os_assoc(self, context, assoc_id, assoc_ref):
        return self.driver.create_os_assoc(context, assoc_id, assoc_ref)

    def get_os_assoc(self, context, assoc_id):
        return self.driver.get_os_assoc(assoc_id)

    def list_os_assocs(self):
        return self.driver.list_os_assocs()

    def delete_os_att(self, assoc_id):
        self.driver.delete_os_assoc(assoc_id)

    def __init__(self):
        super(Manager, self).__init__(CONF.mapping.driver)

    # Sets
    def create_org_set(self, context, set_id, set_ref):
        return self.driver.create_org_attribute_set(
            context, set_id, set_ref)

    def get_org_set(self, context, set_id):
        return self.driver.get_org_set(set_id)

    def list_org_sets(self):
        return self.driver.list_org_sets()

    def delete_org_set(self, set_id):
        self.driver.delete_org_set(set_id)

    # Attributes
    def create_org_att(self, context, attribute_id, attribute_ref):
        return self.driver.create_org_attribute(
            context, attribute_id, attribute_ref)

    def get_org_att(self, context, attribute_id):
        return self.driver.get_org_att(attribute_id)

    def list_org_atts(self):
        return self.driver.list_org_atts()

    def delete_org_att(self, attribute_id):
        self.driver.delete_org_att(attribute_id)

    # Associations
    def create_org_assoc(self, context, assoc_id, assoc_ref):
        return self.driver.create_org_assoc(
            context, assoc_id, assoc_ref)

    def get_org_assoc(self, context, assoc_id):
        return self.driver.get_org_assoc(assoc_id)

    def list_org_assocs(self):
        return self.driver.list_org_assocs()

    def delete_org_att(self, assoc_id):
        self.driver.delete_org_assoc(assoc_id)

    # Mappings
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
