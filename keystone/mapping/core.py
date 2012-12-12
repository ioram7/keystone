# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from keystone.common import wsgi
from keystone.mapping import org

class MappingExtension(wsgi.ExtensionRouter):
	"""

	Provides a bunch of CRUD operations for internal data types.

	"""
	def add_routes(self, mapper):
		mapping_controller = org.OrgMappingController()
		# Role mapping operations
		mapper.connect('/mappings/orgattributeset',
			controller=mapping_controller,
			action='get_org_sets',
			conditions=dict(method=['GET']))
		mapper.connect('/mappings/orgattributeset/{set_id}',
			controller=mapping_controller,
			action='get_org_sets',
			conditions=dict(method=['GET']))
		mapper.connect('/mappings/orgattributeset/{set_id}',
			controller=mapping_controller,
			action='delete_org_set',
			conditions=dict(method=['DELETE']))
		mapper.connect('/mappings/orgattributeset',
			controller=mapping_controller,
			action='create_org_set',
			conditions=dict(method=['POST']))
