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
	# Sets
	def get_org_sets(self, context, set_id = None):
		if set_id:
			LOG.debug("Retrieving Organisational Attribute Set with ID: "+ str(set_id))
			return {'orgattributeset': self.mapping_api.get_org_set(context, set_id)}
		LOG.debug("Retrieving Organisational Attribute Sets")
		return {'orgattributesets': self.mapping_api.list_org_sets()}

	def delete_org_set(self, context, set_id):
		LOG.debug("Deleting set with ID: " + str(set_id))
		self.mapping_api.delete_org_set(set_id)

	def create_org_set(self, context, org_attribute_set):
		LOG.debug("Creating set: " + str(org_attribute_set))
		self.assert_admin(context)
		set_id = uuid.uuid4().hex
		set_ref = org_attribute_set.copy()
		set_ref['id'] = set_id
		new_set_ref = self.mapping_api.create_org_set(context, set_id, set_ref)
		return {'orgattributeset': new_set_ref}
	# Attributes
	def get_org_atts(self, context, attribute_id = None):
		if attribute_id:
			LOG.debug("Retrieving Organisational Attribute with ID: "+ str(attribute_id))
			return {'orgattribute': self.mapping_api.get_org_att(context, attribute_id)}
		LOG.debug("Retrieving Organisational Attributes")
		atts = self.mapping_api.list_org_atts()
		return {'orgattributes': atts}

	def delete_org_att(self, context, attribute_id):
		LOG.debug("Deleting org attribute with ID: " + str(attribute_id))
		self.mapping_api.delete_org_att(attribute_id)

	def create_org_att(self, context, orgattribute):
		LOG.debug("Creating attribute: " + str(orgattribute))
		self.assert_admin(context)
		attribute_id = uuid.uuid4().hex
		attribute_ref = orgattribute.copy()
		attribute_ref['id'] = attribute_id
		new_attribute_ref = self.mapping_api.create_org_att(context, attribute_id, attribute_ref)
		return {'orgattributeset': new_attribute_ref}
	
	# Attributes
	def get_org_assocs(self, context, assoc_id = None):
		if assoc_id:
			LOG.debug("Retrieving Organisational Attribute with ID: "+ str(assoc_id))
			return {'orgattributeassociation': self.mapping_api.get_org_assoc(context, assoc_id)}
		LOG.debug("Retrieving Organisational Attributes")
		assocs = self.mapping_api.list_org_assocs()
		return {'orgattributeassociations': assocs}

	def delete_org_assoc(self, context, assoc_id):
		LOG.debug("Deleting org attribute association with ID: " + str(assoc_id))
		self.mapping_api.delete_org_att(assoc_id)

	def create_org_assoc(self, context, orgattributeassociation):
		LOG.debug("Creating attribute: " + str(orgattributeassociation))
		self.assert_admin(context)
		assoc_id = uuid.uuid4().hex
		assoc_ref = orgattributeassociation.copy()
		assoc_ref['id'] = assoc_id
		new_assoc_ref = self.mapping_api.create_org_assoc(context, assoc_id, assoc_ref)
		return {'orgattributeassociation': new_assoc_ref}

class OrgMappingManager(manager.Manager):
	def __init__(self):
		super(OrgMappingManager, self).__init__(CONF.mapping.driver)
	# Sets
	def create_org_set(self, context, set_id, set_ref):
		return self.driver.create_org_attribute_set(context, set_id, set_ref)
	
	def get_org_set(self, context, set_id):
		return self.driver.get_org_set(set_id)
	
	def list_org_sets(self):
		return self.driver.list_org_sets()
	
	def delete_org_set(self, set_id):
		self.driver.delete_org_set(set_id)
	
	# Attributes
	def create_org_att(self, context, attribute_id, attribute_ref):
		return self.driver.create_org_attribute(context, attribute_id, attribute_ref)

	def get_org_att(self, context, attribute_id):
		return self.driver.get_org_att(attribute_id)
	
	def list_org_atts(self):
		return self.driver.list_org_atts()

	def delete_org_att(self, attribute_id):
		self.driver.delete_org_att(attribute_id)

	# Associations
	def create_org_assoc(self, context, assoc_id, assoc_ref):
		return self.driver.create_org_assoc(context, assoc_id, assoc_ref)

	def get_org_assoc(self, context, assoc_id):
		return self.driver.get_org_assoc(assoc_id)

	def list_org_assocs(self):
		return self.driver.list_org_assocs()

	def delete_org_att(self, assoc_id):
		self.driver.delete_org_assoc(assoc_id)
