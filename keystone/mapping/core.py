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


class Driver(object):

    def __init__(self):
        super(Mapping)

    # Organisational
    #Sets
    def create_org_attribute_set(self, org_set_id, org_set_ref):
        raise exception.NotImplemented()

    def get_org_set(self, set_id):
        raise exception.NotImplemented()

    def _get_org_set(self, session, set_id):
        raise exception.NotImplemented()

    def list_org_sets(self):
        raise exception.NotImplemented()

    def delete_org_set(self, set_id):
        raise exception.NotImplemented()

    # Attributes
    def create_org_attribute(self, context, org_att_id, org_att_ref):
        raise exception.NotImplemented()

    def get_org_att(self, attribute_id):
        raise exception.NotImplemented()

    def _get_org_att(self, session, attribute_id):
        raise exception.NotImplemented()

    def list_org_atts(self):
        raise exception.NotImplemented()

    def delete_org_att(self, attribute_id):
        raise exception.NotImplemented()

    # Associations
    def create_org_assoc(self, context, org_assoc_id, org_assoc_ref):
        raise exception.NotImplemented()

    def get_org_assoc(self, assoc_id):
        raise exception.NotImplemented()

    def _get_org_assoc(self, session, assoc_id):
        raise exception.NotImplemented()

    def list_org_assocs(self):
        raise exception.NotImplemented()

    def delete_org_assoc(self, assoc_id):
        raise exception.NotImplemented()

    # Openstack
    #Sets
    def create_os_attribute_set(self, context, os_set_id, os_set_ref):
        raise exception.NotImplemented()

    def get_os_set(self, set_id):
        raise exception.NotImplemented()

    def _get_os_set(self, session, set_id):
        raise exception.NotImplemented()

    def list_os_sets(self):
        raise exception.NotImplemented()

    def delete_os_set(self, set_id):
        raise exception.NotImplemented()

    def _get_os_set_details(self, session, set_id):
        raise exception.NotImplemented()

    # Associations
    def create_os_assoc(self, context, os_assoc_id, os_assoc_ref):
        raise exception.NotImplemented()

    def get_os_assoc(self, assoc_id):
        raise exception.NotImplemented()

    def _get_os_assoc(self, session, assoc_id):
        raise exception.NotImplemented()

    def list_os_assocs(self):
        raise exception.NotImplemented()

    def delete_os_assoc(self, assoc_id):
        raise exception.NotImplemented()

    def _get_os_att(self, session, att_id, type):
        raise exception.NotImplemented()

    # Attribute Mapping
    def create_mapping(self, context, mapping_id, mapping_ref):
        raise exception.NotImplemented()

    def get_mapping(self, mapping_id):
        raise exception.NotImplemented()

    def _get_mapping(self, session, mapping_id):
        raise exception.NotImplemented()

    def delete_mapping(self, mapping_id):
        raise exception.NotImplemented()

    def list_mappings(self):
        raise exception.NotImplemented()


