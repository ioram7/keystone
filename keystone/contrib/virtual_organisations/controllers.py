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

"""Extensions supporting Virtual Organisations."""
from keystone.common import authorization
from keystone.common import controller
from keystone.identity import controllers as identity
from keystone.assignment import controllers as assignment
from keystone.common import dependency
from keystone.common import wsgi
from keystone.contrib import federation
from keystone import exception
from keystone import config

import uuid
import json

from keystone.openstack.common import log


LOG = log.getLogger(__name__)


CONF = config.CONF


class _ControllerBase(controller.V3Controller):
    """Base behaviors for vo controllers."""

    @classmethod
    def base_url(cls, context, path=None):
        """Construct a path and pass it to V3Controller.base_url method."""

        path = '/OS-FEDERATION/' + cls.collection_name
        return super(_ControllerBase, cls).base_url(context, path=path)


@dependency.requires('virtual_organisations_api', 'identity_api')
@dependency.requires('token_provider_api', 'federation_api')
class VirtualOrganisation(_ControllerBase):
    """Virtual Organisation Role representation."""
    collection_name = 'vo_roles'
    member_name = 'vo_role'

    _mutable_parameters = frozenset(['id', 'description', 'enabled', 'pin',
                                     'vo_is_domain', 'vo_name', 'vo_role', 'group_id',
                                     'automatic_join'])
    _public_parameters = frozenset(['id', 'group_id', 'enabled', 'vo_name', 'vo_role', 'description', 'links', 'automatic_join'])

    @classmethod
    def _add_related_links(cls, context, ref):
        """Add URLs for entities related with Virtual Organisation Role.

        """
        ref.setdefault('links', {})
        base_path = ref['links'].get('self')
        if base_path is None:
            base_path = '/'.join([VirtualOrganisationRole.base_url(context),
                                  ref['id']])

    @classmethod
    def _add_self_referential_link(cls, context, ref):
        id = ref.get('id')
        self_path = '/'.join([cls.base_url(context), id])
        ref.setdefault('links', {})
        ref['links']['self'] = self_path

    @classmethod
    def wrap_member(cls, context, ref):
        cls._add_self_referential_link(context, ref)
        cls._add_related_links(context, ref)
        ref = cls.filter_params(ref)
        return {cls.member_name: ref}

    @controller.protected()
    def create_vo_role(self, context, vo_role):
        # Set the VO Role object
        virtual_organisation_role = self._normalize_dict(vo_role)
        virtual_organisation_role.setdefault('enabled', False)
        virtual_organisation_role["id"] = uuid.uuid4().hex
        vo_role_id = virtual_organisation_role["id"]
        group_api = identity.GroupV3()
        domain_api = assignment.DomainV3()
        if virtual_organisation_role.get("automatic_join", None) is None:
            virtual_organisation_role["automatic_join"] = False
        if virtual_organisation_role.get("vo_is_domain", None) is None:
            virtual_organisation_role["vo_is_domain"] = False
        VirtualOrganisation.check_immutable_params(virtual_organisation_role)
	# Set the domain in the VO Role Object. Only accepts a unique domain match.
        domain = None
        if virtual_organisation_role.get("vo_is_domain", False):
            context["query_string"] = {"name":virtual_organisation_role["vo_name"]}
            domains = domain_api.list_domains(context)['domains']
            if len(domains) == 1:
                domain = domains.pop()
            elif len(domains) > 1:
                raise Exception("Unable to create VO domain with name: %s" % virtual_organisation_role["vo_name"])
            else:
                domain = domain_api.create_domain(context, {"name":virtual_organisation_role["vo_name"]})
	# Create a Group for the VO Role and Set the Group in the VO Role Object
        group_ref = {"name":virtual_organisation_role["vo_name"]+"."+virtual_organisation_role["vo_role"]}
        if domain.get('domain', None):
            group_ref = {"name":virtual_organisation_role["vo_role"]}
            group_ref["domain_id"] = domain["domain"]["id"] 
        elif domain:
            group_ref = {"name":virtual_organisation_role["vo_role"]}
            group_ref["domain_id"] = domain["id"]
        group = group_api.create_group(context, group_ref)["group"]
        virtual_organisation_role["group_id"] = group["id"];
	# Create the VO Role
        vo_role_ref = self.virtual_organisations_api.create_vo_role(vo_role_id, virtual_organisation_role)

	## Assign the VO Role to its creator

	# Get the token from the context
        token_id = context['token_id']
        if not token_id:
            token_id = context['subject_token_id']
	resp = self.token_provider_api.validate_token(token_id)
        token_ref = resp.get('token', resp.get('access'))

	# Set IdP Name
        try:
            idp = token_ref["user"]["OS-FEDERATION"]["identity_provider"]["id"]
        except KeyError:
            idp = "LOCAL"

	# Add owner to VO Role
	self._add_user_to_vo_role(vo_role_id, token_ref["user"]["id"], idp)

        response = VirtualOrganisation.wrap_member(context, vo_role_ref)
        return wsgi.render_response(body=response, status=('201', 'Created'))

    @controller.protected()
    def list_vo_roles(self, context):
        ref = self.virtual_organisations_api.list_vo_roles()
        ref = [self.filter_params(x) for x in ref]

        vo_role_list = []
        for vo in ref:
            roles = context.get('environment').get('KEYSTONE_AUTH_CONTEXT').get('roles', {})
            if not context.get("is_admin") and not 'admin' in roles:
                try:
                    self.check_vo_membership_status(context, vo["id"])
                    vo_role_list.append(vo)
                    #print "IORAM> ===== VO: "+vo["vo_name"]+" VO_ID: "+vo["id"]
                except Exception as e:
                    pass
            else:
                vo_role_list = ref

        return VirtualOrganisation.wrap_collection(context, vo_role_list)
#        return VirtualOrganisation.wrap_collection(context, ref)

    @controller.protected()
    def get_vo_role(self, context, vo_role_id):
        ref = self.virtual_organisations_api.get_vo_role(vo_role_id)
        return VirtualOrganisation.wrap_member(context, ref)

    @controller.protected()
    def delete_vo_role(self, context, vo_role_id):
	# Get reference to VO Role
        ref = self.virtual_organisations_api.get_vo_role(vo_role_id)

        # Remove users from the VO Role
        members = self._list_vo_roles_members(vo_role_id)
        members = members.get("members")
        for member in members:
	     user_id = member.get("id")
	     idp = member.get("idp")
             self._remove_vo_role_membership_from_user(vo_role_id, idp, user_id)

	# Remove the VO Role
        group_api = identity.GroupV3()
        self.virtual_organisations_api.delete_vo_role(vo_role_id)
        group_api.delete_group(context,ref["group_id"])

    @controller.protected()
    def update_vo_role(self, context, vo_role_id, vo_role):
        #print "NEW VALUESSSSSSSSSSSS"
        #print vo_role
        virtual_organisation_role = self._normalize_dict(vo_role)
        VirtualOrganisation.check_immutable_params(virtual_organisation_role)
        vo_role_ref = self.virtual_organisations_api.update_vo_role(vo_role_id, virtual_organisation_role)
        return VirtualOrganisation.wrap_member(context, vo_role_ref)

    # ADMIN Membership management
    @controller.protected()
    def add_user_to_vo_role(self, context, vo_role_id, user_id):
        self._add_user_to_vo_role(vo_role_id, user_id, "LOCAL")

    def _add_user_to_vo_role(self,vo_role_id, user_id, idp):

	# Get the reference for the VO Role
        vo_role_ref = self.virtual_organisations_api.get_vo_role(vo_role_id)

	# If IDP in request is local, add the user to the Group which represent the VO Role.
        if idp == "LOCAL":
            self.identity_api.add_user_to_group(user_id=user_id, group_id=vo_role_ref["group_id"])

	# Else... (Federated IdP)
	else:
       	    # Get the mapping for idp / protocol (protocols table)
            protocols = self.federation_api.list_protocols(idp)

	    # Gets the mapping for the first entry of the protocols object (each idp should have only one protocol/entry)
            mapping = self.federation_api.get_mapping(protocols[0].get("mapping_id"))

            # Find which attribute maps to user id
            rules = mapping.get("rules", None)
            for rule in json.loads(rules):
                local = rule.get("local")
                for att in local:
                    if att.get("user") is not None:
                        if att.get("user").get("name") is not None:
                            att_type = rule.get("remote")[0]["type"]
            if not att_type:
                raise Exception("Mapping must contain a user name attribute type")

            # Insert entry in mapping table
            new_rule = {}
            new_rule[u'local'] = [{'group':{'id': vo_role_ref['group_id']}}]
            new_rule[u'remote'] = [{'type': att_type, 'any_one_of': [user_id]}]
            rules = json.loads(mapping["rules"])
            rules.append(new_rule)
            mapping["rules"] = rules
            self.federation_api.update_mapping(mapping["id"], mapping)

    # End of _add_user_to_vo_role


    @controller.protected()
    def list_vo_roles_members(self, context, vo_role_id):
        roles = context.get('environment').get('KEYSTONE_AUTH_CONTEXT').get('roles', {})
        #Only admins can see members of all VO Roles! This is a hack...
        if not context.get("is_admin") and not 'admin' in roles:
            try:
                self.check_vo_membership_status(context, vo_role_id)
            except Exception as e:
                raise exception.Forbidden("You are not authorised to view members of this VO")
        return self._list_vo_roles_members(vo_role_id)

    def _list_vo_roles_members(self, vo_role_id):
        fed_users = [] 
        vo_ref = self.virtual_organisations_api.get_vo_role(vo_role_id)

        try:
            mappings = self.federation_api.list_mappings()
            for mapping in mappings:
		mapping_id = mapping.get("id", None)

		# Search which IdP this mapping belong
		idps = self.federation_api.list_idps()
		map_idp = "<Unknown_IdP>";
		for idp in idps:
			prots = self.federation_api.list_protocols(idp.get("id"))
			# Considering each IdP has only one protocol.
			if prots[0].get("mapping_id") == mapping_id:
				map_idp = idp.get("id")

		rules = mapping.get("rules", None)
                for rule in json.loads(rules):
                    local = rule.get("local")
                    for att in local:
                        if(att.get("group") is not None):
                            if vo_ref["group_id"] in att.get("group").get("id"):
				usr = {}
				usr["id"] = rule.get("remote")[0]["any_one_of"][0]
				usr["name"] = rule.get("remote")[0]["any_one_of"][0]
				usr["idp"] = map_idp
                                fed_users.append(usr)
        except Exception as e:
            pass
        users = self.identity_api.list_users_in_group(vo_ref["group_id"])
        for user in users:
            user["name"] = self.identity_api.get_user(user["id"])["name"]
            user["idp"] = "LOCAL"
        fed_users.extend(users)
        return {"members":fed_users}

    @controller.protected()
    def get_vo_role_member(self, context, vo_role_id, user_id):
        vo_ref = self.virtual_organisations_api.get_vo_role(vo_role_id)
        users = self.identity_api.list_users_in_group(vo_ref["group_id"])
        for user in users:
            if user["id"] == user_id:
                return
        raise exception.NotFound("User not member of VO")

    @controller.protected()
    def remove_vo_role_membership_from_user(self, context, vo_role_id, idp, user_id):
        self._remove_vo_role_membership_from_user(vo_role_id, idp, user_id)

    def _remove_vo_role_membership_from_user(self, vo_role_id, idp, user_id):
        vo_role_ref = self.virtual_organisations_api.get_vo_role(vo_role_id)
	if idp == "LOCAL" :
            try:
                self.identity_api.remove_user_from_group(user_id=user_id, group_id=vo_role_ref["group_id"])
            except exception.NotFound:
	        pass
        else :
            vo_ref = self.virtual_organisations_api.get_vo_role(vo_role_id)
            mappings = self.federation_api.list_mappings()
            fed_users = []
            for mapping in mappings:
                ruleString = mapping.get("rules")
                rules = json.loads(ruleString)
                for rule in rules:
                    local = rule.get("local")
                    for att in local:
                        if(att.get("group") is not None):
                            if vo_ref["group_id"] in att.get("group").get("id"):
                                if rule.get("remote")[0]["any_one_of"][0] == user_id:
                                    rules.remove(rule)
                                    mapping["rules"] = rules
                                    self.federation_api.update_mapping(mapping["id"], mapping)
        

    @controller.protected()
    def switch_vo_role_for_user(self, context, vo_role_id, user_id, new_vo_role_id):
        
        self.virtual_organisations_api.get_vo_role(vo_role_id)

    # User API
    @controller.protected()
    def list_my_vo_roles(self, context, user_id, idp):
        ref = self.virtual_organisations_api.list_my_vo_roles(user_id, idp)
        ref = [self.filter_params(x) for x in ref]
        return VirtualOrganisation.wrap_collection(context, ref)

    def join_vo_role(self, context, vo_request):

	# Get the token id from the context
        token_id = context['token_id']
        if not token_id:
            token_id = context['subject_token_id']
	
	# Get the token from the token_id
        response = self.token_provider_api.validate_token(token_id)

        # For V3 tokens, the essential data is under the 'token' value.
        # For V2, the comparable data was nested under 'access'.
        token_ref = response.get('token', response.get('access'))

	# Set IdP Name
        try:
            idp = token_ref["user"]["OS-FEDERATION"]["identity_provider"]["id"]
        except KeyError:
            idp = "LOCAL"

	# Get the VO and VO Role references
        vo_ref = self.virtual_organisations_api.get_vo_role_by_name_and_role(vo_request.get("vo_name"), vo_request.get("vo_role"))
	if vo_ref:
	    pass
        if not vo_ref:
            raise exception.NotFound("The VO Role %s was not found in VO" % vo_request.get("vo_role"))

	# Set the PIN from the user's request and the PIN from the VO Role table.
        given_pin = vo_request.get("secret", None)
        required_pin = vo_ref.get("pin")

	# Verify if there is already a request in the database
        vo_request = self.virtual_organisations_api.get_request_for_user(token_ref["user"]["id"], vo_ref["id"], idp)
        if (vo_request):
            raise exception.Forbidden("You have already requested to join this VO")

	# Verify if the user is blacklisted
        blacklist_ref = self.virtual_organisations_api.get_vo_blacklist_for_user(token_ref["user"]["id"], vo_ref["id"], idp)
        if blacklist_ref:
            count = blacklist_ref["count"]
            if count == 3L:
                raise exception.Forbidden("You have entered an incorrect "
                                          "PIN too many times. Please contact "
                                          "your administrator to ask for your "
                                          "account to be unlocked.")


        # Verify if the PIN is correct
        if(given_pin == required_pin or required_pin == ""):
            if blacklist_ref: # Reset blacklist counter
                self.virtual_organisations_api.delete_vo_blacklist(blacklist_ref["id"])

            vo_role_ref = self.virtual_organisations_api.get_vo_role(vo_ref["id"])
            status = "pending"

            if vo_role_ref["automatic_join"]:
                self._add_user_to_vo_role(vo_ref["id"], token_ref["user"]["id"], idp)
                status = "approved"
            else:
		# Create a new object for the VO Request
                vo_request_ref = {}
                vo_request_ref["id"] = uuid.uuid4().hex
                vo_request_ref["user_id"] = token_ref["user"]["id"]
                vo_request_ref["vo_role_id"] = vo_ref["id"]
                vo_request_ref["idp"] = idp
		# Create VO Request in database
                ref = self.virtual_organisations_api.create_vo_request(vo_request_ref["id"], vo_request_ref)
            resp = {}
            resp["vo_name"] = vo_role_ref["vo_name"]
            resp["status"] = status
            return {"vo_request":resp}
        else:
            if blacklist_ref:
                blacklist_ref["count"]+=1L
                self.virtual_organisations_api.update_vo_blacklist(blacklist_ref["id"], blacklist_ref)
            else:
                blacklist_ref = {}
                blacklist_ref["id"] = uuid.uuid4().hex
                blacklist_ref["vo_role_id"] = vo_ref["id"]
                blacklist_ref["user_id"] = token_ref["user"]["id"]
                blacklist_ref["idp"]  = idp
                if idp is None:
                   blacklist_ref["idp"] = "LOCAL"
                blacklist_ref["count"]=1L
                self.virtual_organisations_api.create_vo_blacklist(blacklist_ref["id"], blacklist_ref)
            raise exception.Forbidden("You have entered an incorrect PIN")

    def check_vo_membership_status(self, context, vo_role_id):
        token_id = context['token_id']
        response = self.token_provider_api.validate_token(token_id)
        roles = context.get('environment').get('KEYSTONE_AUTH_CONTEXT').get('roles', {})
	# Admins are in all VO Roles! This is a hack...
        if context.get("is_admin") or 'admin' in roles:
            return {"status":"approved"}
        # For V3 tokens, the essential data is under the 'token' value.
        # For V2, the comparable data was nested under 'access'.
        token_ref = response.get('token', response.get('access'))
        user_id = token_ref["user"]["id"]

	# Set IdP Name
        try:
            idp = token_ref["user"]["OS-FEDERATION"]["identity_provider"]["id"]
        except KeyError:
            idp = "LOCAL"

        vo_ref = self.virtual_organisations_api.get_vo_role(vo_role_id)
        vo_request = self.virtual_organisations_api.get_request_for_user(user_id, vo_role_id, idp) # IORAM
        users = self._list_vo_roles_members(vo_role_id)
        for user in users["members"]:
            if isinstance(user, dict):
                if user.get("id") == user_id and user.get("idp") == idp:
                    return {"status": "approved"}
            if user == user_id and idp == "LOCAL":
                return {"status": "approved"}
        if not vo_request:
            raise exception.NotFound("A request has not been made or has been declined")
        raise exception.Forbidden("Your request has not yet been approved")


    def resign_from_role(self, context, vo_role_id):
	#print "==========Resign_From_Role============="
        token_id = context['token_id']
        response = self.token_provider_api.validate_token(token_id)
        # For V3 tokens, the essential data is under the 'token' value.
        # For V2, the comparable data was nested under 'access'.
        token_ref = response.get('token', response.get('access'))
        user_id = token_ref["user"]["id"]
        #print "==== USERID = " + user_id
        if "OS-FEDERATION" in token_ref["user"]:
            idp = token_ref.get("user").get("OS-FEDERATION").get("identity_provider")
        else:
            idp = "LOCAL"
        vo_role_ref = self.virtual_organisations_api.get_vo_role(vo_role_id)
        self._remove_vo_role_membership_from_user(vo_role_id, idp, user_id)


@dependency.requires('virtual_organisations_api', 'identity_api', 'federation_api')
class VirtualOrganisationRequest(_ControllerBase):
    """Virtual Organisation Request representation."""
    collection_name = 'vo_requests'
    member_name = 'vo_request'

    _mutable_parameters = frozenset(['id', 'idp' 'vo_role_id', 'user_id'])
    _public_parameters = frozenset(['id', 'idp', 'vo_role_id', 'user_id'])

    @classmethod
    def _add_related_links(cls, context, ref):
        """Add URLs for entities related with Virtual Organisation Role.

        """
        ref.setdefault('links', {})
        base_path = ref['links'].get('self')
        if base_path is None:
            base_path = '/'.join([VirtualOrganisationRequest.base_url(context),
                                  ref['id']])

    @classmethod
    def _add_self_referential_link(cls, context, ref):
        id = ref.get('id')
        self_path = '/'.join([cls.base_url(context), id])
        ref.setdefault('links', {})
        ref['links']['self'] = self_path

    @classmethod
    def wrap_member(cls, context, ref):
        cls._add_self_referential_link(context, ref)
        cls._add_related_links(context, ref)
        ref = cls.filter_params(ref)
        return {cls.member_name: ref}

    # Request API
    @controller.protected()
    def list_vo_requests(self, context, vo_role_id):
        #LOG.warning(vo_role_id)
        ref = self.virtual_organisations_api.list_vo_requests(vo_role_id)
        return VirtualOrganisationRequest.wrap_collection(context, ref)

    @controller.protected()
    def decline_vo_request(self, context, vo_role_id, vo_request_id):
        #LOG.warning(vo_role_id)
        #LOG.warning(vo_request_id)
        self.virtual_organisations_api.delete_vo_request(vo_request_id)

    @controller.protected()
    def approve_vo_request(self, context, vo_role_id, vo_request_id):
	# Get the references for the VO Request and VO Role
        ref = self.virtual_organisations_api.get_vo_request(vo_request_id)
        #LOG.warning(ref)
	# Add user to the role
        self._add_user_to_vo_role(ref["vo_role_id"], ref["user_id"], ref["idp"])
	# Delete the request
        self.virtual_organisations_api.delete_vo_request(vo_request_id)

    def _add_user_to_vo_role(self,vo_role_id, user_id, idp):

	# Get the reference for the VO Role
        vo_role_ref = self.virtual_organisations_api.get_vo_role(vo_role_id)

	# If IDP in request is local, add the user to the Group which represent the VO Role.
        if idp == "LOCAL":
            self.identity_api.add_user_to_group(user_id=user_id, group_id=vo_role_ref["group_id"])

	# Else... (Federated IdP)
	else:

            # Get the mapping for idp / protocol (protocols table)
            protocols = self.federation_api.list_protocols(idp)

	    # Gets the mapping for the first entry of the protocols object (each idp should have only one protocol/entry)
            mapping = self.federation_api.get_mapping(protocols[0].get("mapping_id"))

            # Find which attribute maps to user id
            rules = mapping.get("rules", None)
            for rule in json.loads(rules):
                local = rule.get("local")
                for att in local:
                    if att.get("user") is not None:
                        if att.get("user").get("name") is not None:
                            att_type = rule.get("remote")[0]["type"]
            if not att_type:
                raise Exception("Mapping must contain a user name attribute type")

            # Insert entry in mapping table
            new_rule = {}
            new_rule[u'local'] = [{'group':{'id': vo_role_ref['group_id']}}]
            new_rule[u'remote'] = [{'type': att_type, 'any_one_of': [user_id]}]
            rules = json.loads(mapping["rules"])
            rules.append(new_rule)
            mapping["rules"] = rules
            self.federation_api.update_mapping(mapping["id"], mapping)

   # End of _add_user_to_vo_role


@dependency.requires('virtual_organisations_api')
class VirtualOrganisationBlackList(_ControllerBase):
    """Virtual Organisation Request representation."""
    collection_name = 'vo_blacklist'
    member_name = 'vo_blacklist'

    _mutable_parameters = frozenset(['id', 'idp' 'vo_role_id', 'user_id'])
    _public_parameters = frozenset(['id', 'idp', 'vo_role_id', 'user_id'])

    @classmethod
    def _add_related_links(cls, context, ref):
        """Add URLs for entities related with Virtual Organisation Role.

        """
        ref.setdefault('links', {})
        base_path = ref['links'].get('self')
        if base_path is None:
            base_path = '/'.join([VirtualOrganisationRequest.base_url(context),
                                  ref['id']])

    @classmethod
    def _add_self_referential_link(cls, context, ref):
        id = ref.get('id')
        self_path = '/'.join([cls.base_url(context), id])
        ref.setdefault('links', {})
        ref['links']['self'] = self_path

    @classmethod
    def wrap_member(cls, context, ref):
        cls._add_self_referential_link(context, ref)
        cls._add_related_links(context, ref)
        ref = cls.filter_params(ref)
        return {cls.member_name: ref}

    # Blacklist API
    @controller.protected()
    def get_vo_blacklist(self, context, vo_role_id):
        ref = self.virtual_organisations_api.list_vo_blacklists_for_vo(vo_role_id)
        return VirtualOrganisationBlackList.wrap_collection(context, ref)


    @controller.protected()
    def remove_user_from_blacklist(self, context, vo_role_id, vo_blacklist_id):
        self.virtual_organisations_api.delete_vo_blacklist(vo_blacklist_id)