import uuid

from keystone.common import wsgi
from keystone.common import manager
from keystone.common import logging
from keystone import config


CONF = config.CONF
LOG = logging.getLogger(__name__)

class OrgMappingController(wsgi.Application):
	def __init__(self):
		self.mapping_api = OrgMappingManager()
		super(OrgMappingController)
		
	def get_org_sets(self, context, set_id = None):
		if set_id:
			LOG.debug("Retrieving Organisational Attribute Set with ID: "+ str(set_id))
			return {'something':'specific'}
		LOG.debug("Retrieving Organisational Attribute Sets")
		return {'something':'something'}

	def delete_org_set(self, context, set_id):
		LOG.debug("Deleting set with ID: " + str(set_id))

	def create_org_set(self, context, orgattributeset):
		LOG.debug("Creating set: " + str(orgattributeset))
		self.assert_admin(context)
		set_id = uuid.uuid4().hex
		set_ref = orgattributeset.copy()
		set_ref['id'] = set_id
		new_set_ref = self.mapping_api.create_org_set(context, set_id, set_ref)
		return {'orgattributeset': new_set_ref}

class OrgMappingManager(manager.Manager):
	def __init__(self):
		super(OrgMappingManager, self).__init__(CONF.mapping.driver)
	def create_org_set(self, context, set_id, set_ref):
		return self.driver.create_org_attribute_set(context, set_id, set_ref)
	

class Driver(object):
    """Interface description for an Org Mapping driver."""
    def list_org_att_sets(self):
        """List all service ids in catalog.

        :returns: list of service_ids or an empty list.

        """
        raise exception.NotImplemented()

