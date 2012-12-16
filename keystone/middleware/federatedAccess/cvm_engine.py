'''
 * Copyright (c) 2011, University of Kent
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * 1. Neither the name of the University of Kent nor the names of its
 * contributors may be used to endorse or promote products derived from this
 * software without specific prior written permission.
 *
 * 2. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS 
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.
 *
 * 3. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 * 4. YOU AGREE THAT THE EXCLUSIONS IN PARAGRAPHS 2 AND 3 ABOVE ARE REASONABLE
 * IN THE CIRCUMSTANCES.  IN PARTICULAR, YOU ACKNOWLEDGE (1) THAT THIS
 * SOFTWARE HAS BEEN MADE AVAILABLE TO YOU FREE OF CHARGE, (2) THAT THIS
 * SOFTWARE IS NOT "PRODUCT" QUALITY, BUT HAS BEEN PRODUCED BY A RESEARCH
 * GROUP WHO DESIRE TO MAKE THIS SOFTWARE FREELY AVAILABLE TO PEOPLE WHO WISH
 * TO USE IT, AND (3) THAT BECAUSE THIS SOFTWARE IS NOT OF "PRODUCT" QUALITY
 * IT IS INEVITABLE THAT THERE WILL BE BUGS AND ERRORS, AND POSSIBLY MORE
 * SERIOUS FAULTS, IN THIS SOFTWARE.
 *
 * 5. This license is governed, except to the extent that local laws
 * necessarily apply, by the laws of England and Wales.
'''


'''
Created on 10 Jul 2012

@author: Matteo Casenove
'''

import logging
import uuid
import os
import hashlib
import webob.dec
import webob.exc
import json as simplejson
import json

from keystone import identity
from keystone.exception import UserNotFound
from keystone.exception import TenantNotFound
from keystone.token.core import Manager

from keystone import config
CONF = config.CONF

from keystone.common import manager

LOG = logging.getLogger(__name__)


class Request(webob.Request):
    pass


class ServiceError(Exception):
        pass


'''
Supposing the request respect the following specification:

{ 'account': 'accountName', 'realm': 'realmName', 'assertionId': 'id'}

also the http heather has

    X-Authentication-Type:federated

'''

class MyManager(manager.Manager):
    """Default pivot point for the Identity backend.

    See :mod:`keystone.common.manager.Manager` for more details on how this
    dynamically calls the backend.

    """

    def __init__(self,driver):
        super(MyManager, self).__init__(driver)


ATT_CONFIG_FILE = 'keystone/middleware/federatedAccess/config.xml'

class CVM_Engine(object):
    '''
    classdocs
    '''
    def __init__(self, app, conf):
        '''
        Constructor
        '''
        self.conf = conf
        self.app = app
        if 'attributeFile' in self.conf:
            self.confParser = AttributeConfigParser(self.conf['attributeFile'])
        else:
            self.confParser = AttributeConfigParser(ATT_CONFIG_FILE)
        self.identity = identity.controllers.Tenant()
        self.users = identity.controllers.User()
        self.role = identity.controllers.Role()
        self.token = Manager()

        LOG.info('Starting keystone CVM_Engine middleware')
        LOG.info('Init CVM_Engine!')

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, req):
        '''
        def __call__(self, env, start_response):
        '''
        """Handle incoming request.

        This intercepts the request and handle it.

        """
        LOG.debug('Request intercepted by CVM')
        LOG.debug('--------------------------')
        LOG.debug(req.environ)

        if not 'HTTP_X_AUTHENTICATION_TYPE' in req.environ:
            return self.app(req)
        if not req.environ['HTTP_X_AUTHENTICATION_TYPE'] in  ('federated'):
            return self.app(req)

        LOG.debug('Print env body')
        LOG.debug(req.body)

        LOG.debug('Print Conf --->')
        LOG.debug(self.conf)
        body = req.body
        data = simplejson.loads(body)
        attributesAssertion = {'permisRole': 'staff', 'uid' :'userUID1234', 'idp': 'kent.ac.uk', 'other': 'blablabla'}
        return self.engine(data,attributesAssertion)
        #return self.response_list_tenants('jonny')
        return self.app(req)

    def engine(self,data, userAttributes):
        '''
            The engine method for the middleware. It Creates
            user and tenants. It linkes them together accoding to
            the user needs.

                userAttributes: set of validated attributes coming from the
                    SAML Response from the IDP
                data:  information coming with the request
                tenant_id: optional parameter where the tenant_id is already known

        '''
        realm = data['realm']

        LOG.debug(' *** Engine On *** ')

        if userAttributes is None:
            ''' !!! This is used only for developing tests
            '''
            userAttributes = {'uid': 'userUID1234', 'permisRole': 'staff', 'eduPersonTargettedID' :'userUID1234', 'idp': 'kent.ac.uk', 'other': 'blablabla'}

        self.allAttributes = userAttributes
        user_name = self.get_userName(userAttributes,realm)
        if user_name is None:
            return self.response_Error()
        # create the user if it doen't exist
        self.me = self.create_user(user_name)
        LOG.debug('Logged User : ')
        LOG.debug(self.me)
        # pase the config file
        #valid = self.get_valid_userAttribute(userAttributes)
        conf_attributes = self.get_valid_userAttribute(userAttributes)
        LOG.debug(conf_attributes)
        tenants = self.get_available_tenants(conf_attributes)
        LOG.debug('List available tenants : ')
        LOG.debug(tenants)
        unsToken = self.create_UnscopeToken()
        LOG.debug('UnscopedToken created : '+unsToken)
        return self.response_list_tenants(tenants,unsToken)

       
    def response_Error(self):
        resp = webob.Response(content_type='application/json')
        response = {'Error':{'code':'666','message':'The user does not own enough attributes'}}
        resp.body = json.dumps(response)
        return resp

    def response_ErrorForToken(self):
        resp = webob.Response(content_type='application/json')
        response = {'Error':{'code':'666','message':'The user is not authorised to use this token ID.'}}
        resp.body = json.dumps(response)
        return resp

    def create_UnscopeToken(self,):
        context = self.get_context()
        token_id = uuid.uuid4().hex
        data = {'id': token_id, 'user': self.me}
        data_ref = self.token.create_token(context, token_id, data)
        return data_ref['id']

    def get_userName(self, userAttributes, realm):
        if not type(realm) == str:
            idpname = realm['name']
        idp = realm["service_id"]
        pid = self.confParser.getPID(idpname)
    if pid == None:
        pid = self.confParser.getPID("default")
        userAttributes = dict(userAttributes)
        if userAttributes.has_key(pid):
            s = hashlib.sha1()
            s.update(userAttributes[pid][0]+idp)
            return s.hexdigest()
        else:
            return None

  
    def create_user(self,user_name):
        user = {}
        context = self.get_context()
        try:
            ret = self.identity.identity_api.get_user_by_name(context,user_name)
            if ret is None:
                raise UserNotFound(user_id=user_name)
            user['name']=ret['name']
            user['id']=ret['id']
        except UserNotFound:
            ret = self.users.create_user(context,{'name':user_name})
            user['name'] = ret['user']['name']
            user['id'] = ret['user']['id']
        return user

    def response_list_tenants(self, tenants,unscopeToken):
        resp = webob.Response(content_type='application/json')
        response = {}
        response['tenants'] = tenants
        response['unscopedToken'] = unscopeToken
        resp.body = json.dumps(response)
        return resp

    def link_user_to_tenant(self,tenant_id,user_id):
        context = self.get_context()
        user = self.users.get_user(context, user_id)
        user = user['user']
        user['tenantId']=tenant_id
        updatedUser = self.users.update_user_tenant(context, user_id, user)
        return updatedUser['user']

    def is_linked(self, tenant_id, user_id):
        context = self.get_context()
        users = self.identity.get_tenant_users(context, tenant_id)
        for user in users['users']:
            if user['id'] == user_id:
                return True           
        return False

    def get_tenant_by_name(self, tenant_name):
        tenant = {}
        context = self.get_context()
        try:
            ret = self.identity.identity_api.get_tenant_by_name(context,tenant_name)
            if ret is None:
                raise TenantNotFound(tenant_id=tenant_name)
        except TenantNotFound:
            return None
        tenant['name']=ret['name']
        tenant['id']=ret['id']
        return tenant

    '''
    def get_list_tenants(self):
        LOG.debug('** get list tenants **')
        context = self.get_context()
        tenants_list = {}
        tenants = self.identity.get_all_tenants(context)
        for item in tenants['tenants']:
            LOG.debug(item['name']+" "+item['id'])
            tenants_list[item['name']]=item['id']
        return True
   '''

    def get_valid_userAttribute(self, userAttributes):
        '''
            Return the concatenation of the user attributes according to
            the attributes configured in the config file.

                 userAttributes: contains the attributes coming from the SAML Response

            !!! IMPORTANT: this method doen't support multiple attribute
                values. This is a TODO!

        '''
        confAtt = self.confParser.getSetsAndAtts()
        valid = {}
        for set in confAtt:
            str = ''
            count = 0
            jok = confAtt[set]
            for att in jok:
                values = confAtt[set][att]
                if userAttributes.has_key(att):
                    if values[0] is None or values[0]==userAttributes[att][0]:
                        str+=att+userAttributes[att][0]
                        count = count + 1
            if count==len(confAtt[set]):
                valid[set]=str
        return valid

    def is_permittedTenant(self,conf_attributes,tenant_id):
        user_id = self.me['id']
        ca = dict(conf_attributes)
        context = self.get_context()
        ten = self.identity.get_tenant(context, tenant_id)
        LOG.info('tenant')
        LOG.info(ten)
        for attr,value in ca.iteritems():
            if ten['tenant']['name']==value:
                return True
        return False

    def get_available_tenants(self, conf_attributes):
        filt_tenants = []
        user_id = self.me['id']
        LOG.info('get_available_tenants:')
        LOG.info(conf_attributes)
        ca = dict(conf_attributes)
        for attr,value in ca.iteritems():
            ten = self.get_tenant_by_name(value)
            context = self.get_context()
            if ten is None:
                newTenant = self.identity.create_tenant(context, {'name':value})
                ten={}
                ten['name'] = newTenant['tenant']['name']
                ten['id'] = newTenant['tenant']['id']
            ten['friendlyName'] = attr

            if not self.is_linked(ten['id'], user_id):
                self.link_user_to_tenant(ten['id'], user_id)

            self.check_roles(user_id, ten['id'],ten['friendlyName'],conf_attributes)

            filt_tenants.append(ten)
        return filt_tenants

    def get_available_roles(self,fn,conf_attributes):
        conf_attributes = self.allAttributes
        LOG.info("Finding roles for tenant: " + fn)
        roles = self.confParser.getMappedAttributefForSet(fn)
        LOG.info('From COnf Roles')
        LOG.info(roles)
        res = []
        roles = dict(roles)
        conf_attributes = dict(conf_attributes)
        for role,attr in roles.iteritems():
            LOG.info("Role "+role)
            LOG.info(attr)
            count = 0
            for role,attrib in attr.iteritems():
                LOG.info(role)
                LOG.info(attrib)
                attType = attrib.keys()[0]
                value = attrib[attType]
                LOG.info(conf_attributes.keys())
                if attType in conf_attributes.keys():
                    if value is None:
                        count = count + 1
                    else:
                        if not value is None and conf_attributes[attType]==value:
                            count = count + 1
        if count == len(attr):
                res.append(role)
        return res

    def check_roles(self,user_id,tenant_id,fn,conf_attributes):
        roles = self.get_available_roles(fn,conf_attributes);
        LOG.info('Aval Roles')
        LOG.info(roles)
        context = self.get_context()
        for role in roles:
            if not self.check_user_roles(role, user_id, tenant_id):
                newRole = self.get_role(role)
                newRole = self.role.add_role_to_user(context, user_id, newRole['id'], tenant_id)
                r = newRole['role']
                LOG.info('New Role Linked')
                LOG.info(r.name)

   
    def check_user_roles(self,roleName,user_id,tenant_id):
        context = self.get_context()
        roles = self.role.get_user_roles(context, user_id, tenant_id)
        for role in roles['roles']:
            if role['name']==roleName:
                return True
        return False

    def get_role(self, name):
        context = self.get_context()
        retRole = {}
        roles = self.role.get_roles(context)
        for role in roles['roles']:
            if role['name']==name:
                retRole['name']=role['name']
                retRole['id']=role['id']
                return retRole
        return self.role.create_role(context, {'name':name})['role']

           

   
    def get_context(self):
        context = {'query_string':{'limit':100000,'Marker':0}}
        context['is_admin'] = True
        return context



def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def auth_filter(app):
        return CVM_Engine(app, conf)
    return auth_filter

       
import xml.etree.ElementTree as ET

class AttributeConfigParser:
        def __init__(self, file):
                self.tree = ET.parse(file)

        def getMappedAttributefForSet(self, setName):
            element = None
            res = {}
            for set in self.getSets():

                if set.get("DisplayName") == setName:
                    element = set
                attlist = {}
            if element == None: return attlist
            for att in element.iter():
                role = ''
                attribute = {}
                if att.tag == "AttributeMapping":
                    for field in att.iter():
                        if field.tag == "Attribute":
                            if field.get("Value") is None:
                                attribute[field.get("Name")]=None
                            else:
                                attribute[field.get("Name")]=field.get("Value")
                        if field.tag == "RoleGranted":
                            role = field.text
                    attlist[role]=attribute
            res[set.get("DisplayName")]=attlist

            return res

        def getSets(self):
                return self.tree.getroot().find("SetOfTenants").findall("Tenant")

        def getAttributesForSet(self, setName):
            element = None
            for set in self.getSets():
                if set.get("DisplayName") == setName:
                    element = set
            attlist = {}
            if element == None: return attlist
            for att in element:
                if att.tag == "Attribute":
                    values = {}
                    name = att.get("Name")
                    friendly = att.get("DisplayName")
                    if friendly == None: friendly = name
                    val = att.get("Value")
                    values = [val,friendly]
                    attlist[name] = values
            return attlist

        def getTenantSets(self):
            tenantSets = {}
            for set in self.getSets():
                friendly = set.get("DisplayName")
                name = ""
                for att in set:
                    if att.tag == "Attribute":
                        name = name+att.get("Name")
                tenantSets[friendly] = name
            return tenantSets

        def getSetsAndAtts(self):
            sets = {}
            for set in self.getSets():
                sets[set.get("DisplayName")] = self.getAttributesForSet(set.get("DisplayName"))
            return sets

        def getAttributes(self):
            # Return atts
            atts = []
            for set in self.getSets():
                for att in set.findall("Attribute"):
                    name = att.get("Name")
                    if not name in atts:
                        atts.append(name)   
            return atts

        def getPID(self, idp):
            for i in self.tree.getroot().findall("IdPpidMapping"):
                if i.get("Name") == idp:
                    return i.get("PID")
            return None

        def getCert(self):
            return self.tree.getroot().find("CertificateFile").text

        def getKey(self):
            return self.tree.getroot().find("KeyFile").text

class Config:
    def __init__(self, file):
        self.parser = ConfigParser(file)
        self.cert = self.parser.getCert()
        self.key = self.parser.getKey()
        self.attributes = self.parser.getAttributes()
        self.setNames = self.parser.getTenantSets()
        self.sets = self.parser.getSetsAndAtts()
        self.mapAtt = {}
        for key in self.sets.keys():
            self.mapAtt[key] = self.parser.getMappedAttributeForSet(key)

    def getMappedAttributes(self):
        return self.mapAtt

    def getCert(self):
        return self.cert

    def getKey(self):
        return self.key

    def getAttributes(self):
        return self.attributes

    def getPID(self,idp):
        return self.parser.getPID(idp)

    def getTenantSets(self):
        return self.setNames

    def getSetsAndAtts(self):
        return self.sets