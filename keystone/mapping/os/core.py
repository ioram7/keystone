import uuid

from keystone.common import wsgi
from keystone.common import manager
from keystone.common import logging
from keystone import config


CONF = config.CONF
LOG = logging.getLogger(__name__)

class OsMappingController(wsgi.Application):
	def __init__(self):
		self.mapping_api = OsMappingManager()
		super(OsMappingController)
	# Sets
	def get_os_sets(self, context, set_id = None):
		if set_id:
			return {'osattributeset': self.mapping_api.get_os_set(context, set_id)}
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
	def get_os_assocs(self, context, assoc_id = None):
		if assoc_id:
			return {'osattributeassociation': self.mapping_api.get_os_assoc(context, assoc_id)}
		assocs = self.mapping_api.list_os_assocs()
		return {'osattributeassociations': assocs}

	def delete_os_assoc(self, context, assoc_id):
		LOG.debug("Deleting os attribute association with ID: " + str(assoc_id))
		self.mapping_api.delete_os_att(assoc_id)

	def create_os_assoc(self, context, osattributeassociation):
		LOG.debug("Creating attribute: " + str(osattributeassociation))
		self.assert_admin(context)
		assoc_id = uuid.uuid4().hex
		assoc_ref = osattributeassociation.copy()
		assoc_ref['id'] = assoc_id
		new_assoc_ref = self.mapping_api.create_os_assoc(context, assoc_id, assoc_ref)
		return {'osattributeassociation': new_assoc_ref}

class OsMappingManager(manager.Manager):
	def __init__(self):
		super(OsMappingManager, self).__init__(CONF.mapping.driver)
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
