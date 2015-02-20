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
from keystone.contrib import virtual_organisations
from keystone.contrib.virtual_organisations import controllers


class VirtualOrganisationExtension(wsgi.ExtensionRouter):
    """API Endpoints for the Federation extension.

    The API looks like::
        
        ADMIN CRUD ON VO ROLES
        ----------------------
        PUT /OS-FEDERATION/vo_roles # List VO Roles assigned to the current user
        GET /OS-FEDERATION/vo_roles # List all VO Roles
        GET /OS-FEDERATION/vo_roles/$vo_role #
        DELETE /OS-FEDERATION/vo_roles/$vo_role #
        PATCH /OS-FEDERATION/vo_roles/$vo_role #

        ADMIN API for membership
        -------------------------
        PUT /OS-FEDERATION/vo_roles/$vo_role/members/$user_id
        GET /OS-FEDERATION/vo_roles/$vo_role/members/$user_id
        GET /OS-FEDERATION/vo_roles/$vo_role/members
        PATCH /OS-FEDERATION/vo_roles/$vo_role/members/$user_id
        DELETE /OS-FEDERATION/vo_roles/$vo_role/identity_providers/$idp/members/$user_id

        ADMIN API for request management
        -----------------------
        GET /OS-FEDERATION/vo_roles/requests
        HEAD /OS-FEDERATION/vo_roles/requests/$vo_request
        DELETE /OS-FEDERATION/vo_roles/requests/$vo_request

        ADMIN API for blacklist
        -----------------------
        GET /OS-FEDERATION/vo_roles/blacklist
        DELETE /OS-FEDERATION/vo_roles/blacklist/$vo_blacklist

        USER API for membership
        -----------------------
        GET /OS-FEDERATION/vo_users/$user_id/identity_providers/$idp_id/vo_roles # list vo_roles assigned to the user@idp
        PUT /OS-FEDERATION/vo_users - join VO
        GET /OS-FEDERATION/vo_roles/$vo_role_id/users - check status
        DELETE /OS-FEDERATION/vo_roles/$vo_role_id/members

    """

    def _construct_url(self, suffix):
        return "/OS-FEDERATION/%s" % suffix

    def add_routes(self, mapper):
        # This is needed for dependency injection
        # it loads the Virtual Organisation driver which registers it as a dependency.
        #print "Adding VO routes"
        virtual_organisations.Manager()
        vo_controller = controllers.VirtualOrganisation()
        vo_request_controller = controllers.VirtualOrganisationRequest()
        vo_blacklist_controller = controllers.VirtualOrganisationBlackList()

        # Virtual Organisation Role ADMIN CRUD operations

        mapper.connect(
            self._construct_url('vo_roles'),
            controller=vo_controller,
            action='create_vo_role',
            conditions=dict(method=['POST']))

        mapper.connect(
            self._construct_url('vo_roles'),
            controller=vo_controller,
            action='list_vo_roles',
            conditions=dict(method=['GET']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}'),
            controller=vo_controller,
            action='get_vo_role',
            conditions=dict(method=['GET']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}'),
            controller=vo_controller,
            action='delete_vo_role',
            conditions=dict(method=['DELETE']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}'),
            controller=vo_controller,
            action='update_vo_role',
            conditions=dict(method=['PATCH']))

        # Virtual Organisation Membership ADMIN CRUD operations

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/members/{user_id}'),
            controller=vo_controller,
            action='add_user_to_vo_role',
            conditions=dict(method=['PUT']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/members'),
            controller=vo_controller,
            action='list_vo_roles_members',
            conditions=dict(method=['GET']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/members/{user_id}'),
            controller=vo_controller,
            action='get_vo_role_member',
            conditions=dict(method=['GET']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/identity_providers/{idp}/members/{user_id}'),
            controller=vo_controller,
            action='remove_vo_role_membership_from_user',
            conditions=dict(method=['DELETE']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/members/{user_id}'),
            controller=vo_controller,
            action='switch_vo_role_for_user',
            conditions=dict(method=['PATCH']))

        # ADMIN API Request Management
        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/requests'),
            controller=vo_request_controller,
            action='list_vo_requests',
            conditions=dict(method=['GET']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/requests/{vo_request_id}'),
            controller=vo_request_controller,
            action='decline_vo_request',
            conditions=dict(method=['DELETE']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/requests/{vo_request_id}'),
            controller=vo_request_controller,
            action='approve_vo_request',
            conditions=dict(method=['HEAD']))

	# Duplicate for SAML work (bug)
        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/requests/{vo_request_id}'),
            controller=vo_request_controller,
            action='approve_vo_request',
            conditions=dict(method=['GET']))

        # ADMIN API blacklist Management
        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/blacklist'),
            controller=vo_blacklist_controller,
            action='get_vo_blacklist',
            conditions=dict(method=['GET']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/blacklist/{vo_blacklist_id}'),
            controller=vo_blacklist_controller,
            action='remove_user_from_blacklist',
            conditions=dict(method=['DELETE']))

        # USER API
        mapper.connect(
            self._construct_url('vo_users/{user_id}/identity_providers/{idp}/vo_roles'),
            controller=vo_controller,
            action='list_my_vo_roles',
            conditions=dict(method=['GET']))

        mapper.connect(
            self._construct_url('vo_users'),
            controller=vo_controller,
            action='join_vo_role',
            conditions=dict(method=['PUT']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/users'),
            controller=vo_controller,
            action='check_vo_membership_status',
            conditions=dict(method=['GET']))

        mapper.connect(
            self._construct_url('vo_roles/{vo_role_id}/members'),
            controller=vo_controller,
            action='resign_from_role',
            conditions=dict(method=['DELETE']))
