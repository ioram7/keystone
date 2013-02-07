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
Created on 30 Jan 2013

@author: Kristy Siu
'''
from keystone import catalog
from keystone.mapping import controllers
import directory

import logging

import webob.dec
import webob.exc

import json as simplejson

LOG = logging.getLogger(__name__)

class Request(webob.Request):
    pass


'''
Supposing the request respect the following specification:
    
    The HTTP heather has:

    X-Authentication-Type:federated
    
'''
        

class FederatedAuthentication(object):
    
    def __init__(self, app, conf):
        '''
        Constructor
        '''
        self.conf = conf
        self.app = app
                
        LOG.info('Starting federated middleware wrapper')
        LOG.info('Init FederatedAuthentication!')
        
        
        
    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self,req):
        
        
        LOG.debug('Request intercepted by CVM')
        LOG.debug('--------------------------')
        if not 'HTTP_X_AUTHENTICATION_TYPE' in req.environ:
            return self.app(req)
        if not req.environ['HTTP_X_AUTHENTICATION_TYPE'] in  ('federated'):
            return self.app(req)
        
        body = req.body 
        data = simplejson.loads(body)
       
        if 'idpResponse' in data:
            username, validatedUserAttributes = self.validate(data)		
            identity_api = identity.controllers.UserV3()
            user_ref = {'name': username} 
            user = identity_api.create_user({'is_admin': True}, user_ref)
            return self.mapAttributes(data, validatedUserAttributes, user)
            

        else:
            if 'realm' in data:
                realm_id = data['realm']
                self.getRequest(realm_id)
            
            return discovery.getRealmList()

    def getRequest(self, realm_id):
        ''' Get an authentication request to return to the client '''
        catalog = catalog.ServiceController()
        service = catalog.getService(context, realm_id)
        type = service["type"].split('.')[1]
        processing_module = load_protocol_module(type)
        ris = processing_module.RequestIssuingService()
        return ris.getIdPRequest(self.conf['requestSigningKey'], self.conf['SPName'])

    def validate(self, data):
        ''' Get the validated attributes '''
        catalog = catalog.ServiceController()
        service = catalog.getService(context, realm_id)
        type = service["type"].split('.')[1]
        processing_module = load_protocol_module(type)
        cred_validator = processing_module.CredentialValidator()
        return cred_validator.validate(data['idpResponse'])

    def mapAttributes(self, data, attributes, user):
        mapper = controllers.AttributeMappingController()
        identity_api = identity.controllers.UserV3()
        context = {'is_admin': True}
        toMap = mapper.map(context, attributes)
        user_id = user['id']
        roles = []
        projects = []
        domains = []
        for k, v in toMap.iteritems():
            if v == 'role':
                roles.append(k)
            if v == 'project':
                projects.append(k)
            if v == 'domain':
                roles.append(k)
        for d in domains:
            for p in projects:
                identity_api.add_user_to_project(context, user_id=user_id, project_id=p)
                for r in roles:
                    identity_api.add_role_to_user(context, user_id=user_id, project_id=p, role_id=r)

        token_api = token.controllers.TokenController()
        token = token_api.create_token(context, user_id)
        return token
                    

def load_protocol_module(self, protocol):
    ''' Dynamically load correct module for processing authentication
        according to identity provider's protocol'''
    return imp.load_source(protocol, protocol+".py")
        

def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def auth_filter(app):
        return FederatedAuthentication(app, conf)
    return auth_filter
