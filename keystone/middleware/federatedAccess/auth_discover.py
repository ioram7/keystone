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
Created on 18 Jul 2012

@author: Matteo Casenove
'''

import logging

import webob.dec
import webob.exc
import json

from time import localtime, strftime

from keystone import config
CONF = config.CONF

from keystone.common import manager

LOG = logging.getLogger(__name__)

class Request(webob.Request):
    pass

class MyManager(manager.Manager):
    """Default pivot point for the Identity backend.

    See :mod:`keystone.common.manager.Manager` for more details on how this
    dynamically calls the backend.

    """

    def __init__(self,driver):
        super(MyManager, self).__init__(driver)

class AuthDiscover():
    
    def __init__(self, app, conf):
        '''
        Constructor
        '''
        self.conf = conf
        self.app = app
        self.discover = None
        if 'discoverClass' in self.conf:
            self.discover = self.conf['discoverClass']
            self.discover = MyManager(self.discover)
       	self.ris = None
	if 'requestIssuingClass' in self.conf: 
	    self.ris = self.conf['requestIssuingClass']
	    self.ris = MyManager(self.ris)
            
    def create_IdpRequest(self,realm):
        return self.ris.getIdPRequest(self.ris, self.conf['requestSigningKey'], self.conf['SPName']) 
    
    def getEndpoint(self,realm):
	if type(realm) is str:
	    realm = {'name':realm}
        return self.discover.discover(self.discover, realm) 
    
    def discovery(self,realm):
        request = self.create_IdpRequest(realm)
        endPoint = self.getEndpoint(realm)
        response = {'idpRequest':request,'idpEndpoint':endPoint}
        return self.valid_Response(response)
    
    def getRealmList(self):
        response = self.discover.getRealmList(self.discover)
        return self.valid_Response(response)
    
    
    def response_Error(self):
        resp = webob.Response(content_type='application/json')
        response = {'Error':{'code':'667','message':'The discover service is not implemented yet'}}
        resp.body = json.dumps(response)
        return resp
    
    def valid_Response(self,response):
        resp = webob.Response(content_type='application/json')
        resp.body = json.dumps(response)
        return resp    
    
    
    
    
    
