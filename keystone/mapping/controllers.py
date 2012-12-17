import uuid

<<<<<<< HEAD
from keystone import identity
from keystone.common import dependency
from keystone.common import controller
from keystone.common import manager
from keystone.common import logging
from keystone import config
=======
from keystone.common import wsgi
from keystone.common import manager
from keystone.common import logging
from keystone import config
from keystone.mapping.core import Manager
>>>>>>> bf50ba9... Added attribute mapping service

CONF = config.CONF
LOG = logging.getLogger(__name__)


<<<<<<< HEAD
class AttributeSetMappingController(controller.V3Controller):
    # Sets
    @controller.protected
    def get_attribute_set_mapping(self, context, attribute_set_mapping_id):
        mapping_id = attribute_set_mapping_id
        mapping = self.mapping_api.get_attribute_set_mapping(context,
                                                             mapping_id)
        return {'attribute_set_mapping': mapping}

    @controller.protected
    def list_attribute_set_mappings(self, context):
        return {'attribute_set_mappings':
                self.mapping_api.list_attribute_set_mappings(context)}

    @controller.protected
    def delete_attribute_set_mapping(self, context, attribute_set_mapping_id):
        self.mapping_api.delete_attribute_set_mapping(context,
                                                      attribute_set_mapping_id)

    @controller.protected
    def create_attribute_set_mapping(self, context, attribute_set_mapping):
        self.assert_admin(context)
        mapping_id = uuid.uuid4().hex
        mapping_ref = attribute_set_mapping.copy()
        mapping_ref['id'] = mapping_id
        new_mapping_ref = self.mapping_api.create_attribute_set_mapping(
            context, mapping_id, mapping_ref)
        return {'attribute_set_mapping': new_mapping_ref}


class OrgMappingController(controller.V3Controller):

    # Sets

    @controller.protected
    def list_org_attribute_sets(self, context):
        return {'org_attribute_sets':
                self.mapping_api.list_org_attribute_sets(context)}

    @controller.protected
    def get_org_attribute_set(self, context, org_attribute_set_id):
        set_id = org_attribute_set_id
        org_set = self.mapping_api.get_org_attribute_set(context,
                                                         set_id)
        return {'org_attribute_set': org_set}

    @controller.protected
    def delete_org_attribute_set(self, context, org_attribute_set_id):
        set_id = org_attribute_set_id
        mappings = self.mapping_api.list_attribute_set_mappings(
            context,
            org_attribute_set_id=set_id)
        for mapping in mappings:
            self.mapping_api.delete_attribute_set_mapping(context,
                                                          mapping['id'])
        links = self.mapping_api.list_attributes_in_org_set(context,
                                                            set_id)
        for att in links:
            self.remove_attribute_from_org_set(context,
                                               set_id,
                                               att)
        self.mapping_api.delete_org_attribute_set(context,
                                                  set_id)

    @controller.protected
=======
class AttributeMappingController(wsgi.Application):
    def __init__(self):
        self.mapping_api = Manager()
        super(AttributeMappingController)
    # Sets

    def get_mapping(self, context, mapping_id):
        mapping = self.mapping_api.get_mapping(context, mapping_id)
        return {'attribute_mapping': mapping}

    def list_mappings(self, context):
        return {'attribute_mappings': self.mapping_api.list_mappings()}

    def delete_mapping(self, context, mapping_id):
        self.mapping_api.delete_mapping(mapping_id)

    def create_mapping(self, context, attribute_mapping):
        self.assert_admin(context)
        mapping_id = uuid.uuid4().hex
        mapping_ref = attribute_mapping.copy()
        mapping_ref['id'] = mapping_id
        new_mapping_ref = self.mapping_api.create_mapping(
            context, mapping_ref)
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

    def list_org_attribute_sets(self, context):
        return {'org_attribute_sets':
                self.mapping_api.list_org_attribute_sets()}

    def get_org_attribute_set(self, context, org_attribute_set_id):
        org_set = self.mapping_api.get_org_attribute_set(context,
                                                         org_attribute_set_id)
        return {'org_attribute_set': org_set}

    def delete_org_attribute_set(self, context, org_attribute_set_id):
        self.mapping_api.delete_org_attribute_set(org_attribute_set_id)

>>>>>>> bf50ba9... Added attribute mapping service
    def create_org_attribute_set(self, context, org_attribute_set):
        LOG.debug("Creating set: " + str(org_attribute_set))
        self.assert_admin(context)
        set_id = uuid.uuid4().hex
        set_ref = org_attribute_set.copy()
        set_ref['id'] = set_id
        new_set_ref = self.mapping_api.create_org_attribute_set(
<<<<<<< HEAD
            context, set_id, set_ref)
        return {'org_attribute_set': new_set_ref}

    @controller.protected
    def add_attribute_to_org_set(self, context, org_attribute_set_id,
                                 attribute_id):
        return self.mapping_api.add_attribute_to_org_set(context,
                                                         org_attribute_set_id,
                                                         attribute_id)

    @controller.protected
    def remove_attribute_from_org_set(self, context,
                                      org_attribute_set_id, attribute_id):
        set_id = org_attribute_set_id
        return self.mapping_api.remove_attribute_from_org_set(context,
                                                              set_id,
                                                              attribute_id)

    @controller.protected
    def check_attribute_in_org_set(self, context,
                                   org_attribute_set_id, attribute_id):
        set_id = org_attribute_set_id
        return self.mapping_api.check_attribute_in_org_set(context,
                                                           set_id,
                                                           attribute_id)

    @controller.protected
    def list_attributes_in_org_set(self, context, org_attribute_set_id):
        return self.mapping_api.list_attributes_in_org_set(
            context, org_attribute_set_id)
    # Attributes

    @controller.protected
=======
            context, set_ref)
        return {'org_attribute_set': new_set_ref}

    # Attributes

>>>>>>> bf50ba9... Added attribute mapping service
    def get_org_attribute(self, context, org_attribute_id=None):
        att = self.mapping_api.get_org_attribute(context, org_attribute_id)
        return {'org_attribute': att}

<<<<<<< HEAD
    @controller.protected
    def list_org_attributes(self, context):
        atts = self.mapping_api.list_org_attributes(context)
        return {'org_attributes': atts}

    @controller.protected
    def delete_org_attribute(self, context, org_attribute_id):
        att_id = org_attribute_id
        sets = self.mapping_api.list_org_sets_containing_attribute(
            context,
            org_attribute_id=att_id)
        for set in sets:
            self.delete_org_attribute_set(set)
        self.mapping_api.delete_org_attribute(context, att_id)

    @controller.protected
=======
    def list_org_attributes(self, context):
        atts = self.mapping_api.list_org_attributes()
        return {'org_attributes': atts}

    def delete_org_attribute(self, context, org_attribute_id):
        self.mapping_api.delete_org_attribute(org_attribute_id)

>>>>>>> bf50ba9... Added attribute mapping service
    def create_org_attribute(self, context, org_attribute):
        self.assert_admin(context)
        attribute_id = uuid.uuid4().hex
        attribute_ref = org_attribute.copy()
        attribute_ref['id'] = attribute_id
        new_attribute_ref = self.mapping_api.create_org_attribute(
<<<<<<< HEAD
            context, attribute_id, attribute_ref)
        return {'org_attribute': new_attribute_ref}


class OsMappingController(controller.V3Controller):

    # Sets

    def list_attributes_in_os_set(self, context, os_attribute_set_id):
        set_id = os_attribute_set_id
        return self.mapping_api.list_attributes_in_os_set(context,
                                                          set_id)

    @controller.protected
    def add_attribute_to_os_set(self, context,
                                os_attribute_set_id, attribute_id):
        type = context['query_string']['type']
        if not type:
            msg = "Attribute Type is required"
            raise exception.ValidationError(msg)
        identity_api = identity.Manager()
        if type == 'role':
            identity_api.get_role(context, attribute_id)
        if type == 'project':
            identity_api.get_project(context, attribute_id)
        if type == 'domain':
            identity_api.get_domain(context, attribute_id)
        set_id = os_attribute_set_id
        return self.mapping_api.add_attribute_to_os_set(context,
                                                        set_id,
                                                        attribute_id,
                                                        type)

    @controller.protected
    def remove_attribute_from_os_set(self, context,
                                     os_attribute_set_id, attribute_id):
        type = context['query_string']['type']
        if not type:
            msg = "Attribute Type is required"
            raise exception.ValidationError(msg)
        set_id = os_attribute_set_id
        return self.mapping_api.remove_attribute_from_os_set(context,
                                                             set_id,
                                                             attribute_id,
                                                             type)

    @controller.protected
    def check_attribute_in_os_set(self, context,
                                  os_attribute_set_id, attribute_id):
        type = context['query_string']['type']
        if not type:
            msg = "Attribute Type is required"
            raise exception.ValidationError(msg)
        set_id = os_attribute_set_id
        return self.mapping_api.check_attribute_in_os_set(context,
                                                          set_id,
                                                          attribute_id,
                                                          type)

    @controller.protected
=======
            context, attribute_ref)
        return {'org_attribute': new_attribute_ref}

    # Associations

    def get_org_attribute_association(self, context,
                                      org_attribute_association_id=None):
        assoc_id = org_attribute_association_id
        assoc = self.mapping_api.get_org_attribute_association(context,
                                                               assoc_id)
        return {'org_attribute_association': assoc}

    def list_org_attribute_associations(self, context):
        assocs = self.mapping_api.list_org_attribute_associations()
        return {'org_attribute_associations': assocs}

    def delete_org_attribute_association(self, context,
                                         org_attribute_association_id):
        assoc_id = org_attribute_association_id
        self.mapping_api.delete_org_attribute_association(assoc_id)

    def create_org_attribute_association(self, context,
                                         org_attribute_association):
        self.assert_admin(context)
        assoc_id = uuid.uuid4().hex
        assoc_ref = org_attribute_association.copy()
        assoc_ref['id'] = assoc_id
        new_assoc_ref = self.mapping_api.create_org_attribute_association(
            context, assoc_ref)
        return {'org_attribute_association': new_assoc_ref}


class OsMappingController(wsgi.Application):

    def __init__(self):
        self.mapping_api = Manager()
        super(OsMappingController)

    # Sets

>>>>>>> bf50ba9... Added attribute mapping service
    def get_os_attribute_set(self, context, os_attribute_set_id=None):
        if os_attribute_set_id:
            os_set = self.mapping_api.get_os_attribute_set(context,
                                                           os_attribute_set_id)
            return {'os_attribute_set': os_set}

<<<<<<< HEAD
    @controller.protected
    def list_os_attribute_sets(self, context):
        return {'os_attribute_sets':
                self.mapping_api.list_os_attribute_sets(context)}

    @controller.protected
    def delete_os_attribute_set(self, context, os_attribute_set_id):
        mappings = self.mapping_api.list_attribute_set_mappings(
            context,
            os_attribute_set_id=os_attribute_set_id)
        for mapping in mappings:
            self.mapping_api.delete_attribute_set_mapping(context,
                                                          mapping['id'])
        links = self.list_attributes_in_os_set(context, os_attribute_set_id)
        for att, type in links:
            self.remove_attribute_from_os_set(context,
                                              os_attribute_set_id,
                                              att, type)

        self.mapping_api.delete_os_attribute_set(context, os_attribute_set_id)

    @controller.protected
=======
    def list_os_attribute_sets(self, context):
        return {'os_attribute_sets': self.mapping_api.list_os_attribute_sets()}

    def delete_os_attribute_set(self, context, os_attribute_set_id):
        LOG.debug("Start of controller os set delete")
        self.mapping_api.delete_os_attribute_set(os_attribute_set_id)

>>>>>>> bf50ba9... Added attribute mapping service
    def create_os_attribute_set(self, context, os_attribute_set):
        self.assert_admin(context)
        set_id = uuid.uuid4().hex
        set_ref = os_attribute_set.copy()
        set_ref['id'] = set_id
        new_set_ref = self.mapping_api.create_os_attribute_set(context,
<<<<<<< HEAD
                                                               set_id, set_ref)
        return {'os_attribute_set': new_set_ref}

    def clean_up_os_sets(context, attribute_id, type):
        sets = self.mapping_api.list_os_sets_containing_attribute(
            attribute_id=attribute_id,
            type=type)
        for set in sets:
            self.delete_os_attribute_set(context, set['id'])
=======
                                                               set_ref)
        return {'os_attribute_set': new_set_ref}

    # Associations

    def get_os_attribute_association(self, context,
                                     os_attribute_association_id=None):
        assoc_id = os_attribute_association_id
        assoc = self.mapping_api.get_os_attribute_association(context,
                                                              assoc_id)
        return {'os_attribute_association': assoc}

    def list_os_attribute_associations(self, context):
        assocs = self.mapping_api.list_os_attribute_associations()
        return {'os_attribute_associations': assocs}

    def delete_os_attribute_association(self, context,
                                        os_attribute_association_id):
        self.mapping_api.delete_os_attribute_association(
            os_attribute_association_id)

    def create_os_attribute_association(self, context,
                                        os_attribute_association):
        self.assert_admin(context)
        assoc_id = uuid.uuid4().hex
        assoc_ref = os_attribute_association.copy()
        assoc_ref['id'] = assoc_id
        new_assoc_ref = self.mapping_api.create_os_attribute_association(
            context, assoc_ref)
        return {'os_attribute_association': new_assoc_ref}
>>>>>>> bf50ba9... Added attribute mapping service
