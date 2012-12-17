import uuid

from keystone.common import wsgi
from keystone.common import manager
from keystone.common import logging
from keystone import config
from keystone.mapping.core import Manager

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


class OrgMappingController(wsgi.Application):

    def __init__(self):
        self.mapping_api = Manager()
        super(OrgMappingController)

    # Sets
    def get_org_sets(self, context, set_id=None):
        if set_id:
            org_set = self.mapping_api.get_org_set(context, set_id)
            return {'orgattributeset': org_set}
        return {'orgattributesets': self.mapping_api.list_org_sets()}

    def delete_org_set(self, context, set_id):
        self.mapping_api.delete_org_set(set_id)

    def create_org_set(self, context, org_attribute_set):
        LOG.debug("Creating set: " + str(org_attribute_set))
        self.assert_admin(context)
        set_id = uuid.uuid4().hex
        set_ref = org_attribute_set.copy()
        set_ref['id'] = set_id
        new_set_ref = self.mapping_api.create_org_set(
            context, set_id, set_ref)
        return {'orgattributeset': new_set_ref}

    # Attributes
    def get_org_atts(self, context, attribute_id=None):
        if attribute_id:
            att = self.mapping_api.get_org_att(context, attribute_id)
            return {'orgattribute': att}
        atts = self.mapping_api.list_org_atts()
        return {'orgattributes': atts}

    def delete_org_att(self, context, attribute_id):
        self.mapping_api.delete_org_att(attribute_id)

    def create_org_att(self, context, orgattribute):
        self.assert_admin(context)
        attribute_id = uuid.uuid4().hex
        attribute_ref = orgattribute.copy()
        attribute_ref['id'] = attribute_id
        new_attribute_ref = self.mapping_api.create_org_att(
            context, attribute_id, attribute_ref)
        return {'orgattributeset': new_attribute_ref}

    # Associations
    def get_org_assocs(self, context, assoc_id=None):
        if assoc_id:
            assoc = self.mapping_api.get_org_assoc(context, assoc_id)
            return {'orgattributeassociation': assoc}
        assocs = self.mapping_api.list_org_assocs()
        return {'orgattributeassociations': assocs}

    def delete_org_assoc(self, context, assoc_id):
        self.mapping_api.delete_org_att(assoc_id)

    def create_org_assoc(self, context, orgattributeassociation):
        self.assert_admin(context)
        assoc_id = uuid.uuid4().hex
        assoc_ref = orgattributeassociation.copy()
        assoc_ref['id'] = assoc_id
        new_assoc_ref = self.mapping_api.create_org_assoc(
            context, assoc_id, assoc_ref)
        return {'orgattributeassociation': new_assoc_ref}


class OsMappingController(wsgi.Application):

    def __init__(self):
        self.mapping_api = Manager()
        super(OsMappingController)

    # Sets
    def get_os_sets(self, context, set_id=None):
        if set_id:
            os_set = self.mapping_api.get_os_set(context, set_id)
            return {'osattributeset': os_set}
        return {'osattributesets': self.mapping_api.list_os_sets()}

    def delete_os_set(self, context, set_id):
        LOG.debug("Deleting set with ID: " + str(set_id))
        self.mapping_api.delete_os_set(set_id)

    def create_os_set(self, context, os_attribute_set):
        LOG.debug("Creating set: " + str(os_attribute_set))
        self.assert_admin(context)
        set_id = uuid.uuid4().hex
        set_ref = os_attribute_set.copy()
        set_ref['id'] = set_id
        new_set_ref = self.mapping_api.create_os_set(context, set_id, set_ref)
        return {'osattributeset': new_set_ref}

    # Associations
    def get_os_assocs(self, context, assoc_id=None):
        if assoc_id:
            assoc = self.mapping_api.get_os_assoc(context, assoc_id)
            return {'osattributeassociation': assoc}
        assocs = self.mapping_api.list_os_assocs()
        return {'osattributeassociations': assocs}

    def delete_os_assoc(self, context, assoc_id):
        self.mapping_api.delete_os_att(assoc_id)

    def create_os_assoc(self, context, osattributeassociation):
        LOG.debug("Creating attribute: " + str(osattributeassociation))
        self.assert_admin(context)
        assoc_id = uuid.uuid4().hex
        assoc_ref = osattributeassociation.copy()
        assoc_ref['id'] = assoc_id
        new_assoc_ref = self.mapping_api.create_os_assoc(
            context, assoc_id, assoc_ref)
        return {'osattributeassociation': new_assoc_ref}
