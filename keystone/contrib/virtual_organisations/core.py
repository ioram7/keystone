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

"""Extension supporting Federation."""

import abc

import six

from keystone.common import dependency
from keystone.common import extension
from keystone.common import manager
from keystone import config
from keystone import exception
from keystone.openstack.common import log as logging


CONF = config.CONF
LOG = logging.getLogger(__name__)
EXTENSION_DATA = {
    'name': 'OpenStack Virtual Organisation APIs',
    'namespace': 'http://docs.openstack.org/identity/api/ext/'
                 'OS-FEDERATION/v1.0',
    'alias': 'OS-VIRTUAL-ORG',
    'updated': '2013-12-17T12:00:0-00:00',
    'description': 'OpenStack VO roles Mechanism.',
    'links': [{
        'rel': 'describedby',
        'type': 'text/html',
        'href': 'https://github.com/openstack/identity-api'
    }]}
extension.register_admin_extension(EXTENSION_DATA['alias'], EXTENSION_DATA)
extension.register_public_extension(EXTENSION_DATA['alias'], EXTENSION_DATA)

VOROLES = 'OS-FEDERATION:vo_roles'
VOREQUESTS = 'OS-FEDERATION:vo_requests'
VOBLACKLIST = 'OS-VIRTUAL-ORG:vo_blacklist'


@dependency.provider('virtual_organisations_api')
class Manager(manager.Manager):
    """Default pivot point for the Federation backend.

    See :mod:`keystone.common.manager.Manager` for more details on how this
    dynamically calls the backend.

    """
    def __init__(self):
        super(Manager, self).__init__(CONF.virtual_organisations.driver)


@six.add_metaclass(abc.ABCMeta)
class Driver(object):

    # VO role CRUD
    def create_vo_role(self, vo_role_id, vo_role):
        """Create a VO role.

        :returns: vo_role_ref

        """
        raise exception.NotImplemented()

    def delete_vo_role(self, vo_role_id):
        """Delete an VO role.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def list_vo_roles(self):
        """List all VO roles.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def list_my_vo_roles(self, user_id, idp):
        """List VO roles assigned to the user@idp.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def get_vo_role(self, vo_role_id):
        """Get an VO role by ID.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def update_vo_role(self, vo_role_id, vo_role):
        """Update an VO role by ID.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    # VO request CRUD
    def create_vo_request(self, vo_request_id, vo_request):
        """Create an VO request.

        :returns: vo_request_ref

        """
        raise exception.NotImplemented()

    def delete_vo_request(self, vo_request_id):
        """Delete an VO request.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def list_vo_requests(self, vo_role_id):
        """List all VO requests.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def get_vo_request(self, vo_request_id):
        """Get an VO request by ID.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def update_vo_request(self, vo_request_id, vo_request):
        """Update an VO request by ID.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    # VO blacklist CRUD
    def create_vo_blacklist(self, vo_blacklist_id, vo_blacklist):
        """Create an VO blacklist.

        :returns: vo_blacklist_ref

        """
        raise exception.NotImplemented()

    def delete_vo_blacklist(self, vo_blacklist_id):
        """Delete an VO blacklist.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def list_vo_blacklists(self):
        """List all VO blacklists.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def get_vo_blacklist(self, vo_blacklist_id):
        """Get an VO blacklist by ID.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def update_vo_blacklist(self, vo_blacklist_id, vo_blacklist):
        """Update an VO blacklist by ID.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()

    def get_vo_blacklist_for_user(self, user_id, idp):
        """Update an VO blacklist by ID.

        :raises: keystone.exception.VirtualOrganisationRoleNotFound

        """
        raise exception.NotImplemented()
