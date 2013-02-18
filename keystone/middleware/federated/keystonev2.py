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
Created on 1 Feb 2013

@author: Kristy Siu
'''

import logging
import urlparse
import sys
import uuid
sys.path.insert(0, '../')
import dm.xmlsec.binding as xmlsec
xmlsec.initialize()
from os.path import dirname, basename
from lxml.etree import parse,tostring,fromstring,ElementTree
from time import localtime, strftime, gmtime
import urllib
import webbrowser
import urllib2
import zlib
import base64
import webob.dec
import webob.exc
import json

from keystone import mapping
from keystone import catalog
from keystone import exception
LOG = logging.getLogger(__name__)

class RequestIssuingService(object):
    def __init__(self):
        self.tmplReq = '{"auth":{"passwordCredentials": {"username":"", "password":""}}}'

    def getIdPRequest(self,key, issuer, endpoint):
        LOG.info('IssueRequest')
        resp = {}
        resp['idpRequest'] = self.tmplReq
        resp['idpEndpoint'] = endpoint
        return valid_Response(resp)

    def __call__(self):
        return None


class CredentialValidator(object):
    
    def __init__(self):
        self.org_mapping_api = mapping.controllers.OrgMappingController()
        self.mapping_api = mapping.controllers.AttributeMappingController()
    
    def __call__(self):
        return None
        
    def validate(self, response, realm_id):
        catalog_api = catalog.controllers.EndpointV3()
        context = {}
        context['is_admin'] = True
        context['query_string'] = {}
        context['query_string']['service_id'] = realm_id
        context['interface'] = 'adminurl'
        endpoints = catalog_api.list_endpoints(context)
        for e in endpoints['endpoints']:
            if e['interface'] == 'admin':
                endpoint = e['url']+'/tokens/'
            if e['interface'] == 'public':
                post_endpoint = e['url']+'/tokens'
        token_id = response['access']['token']['id']
        # TODO acquire admin token to retrieve token verification
        auth_req = {"auth":{}}
        auth_req["auth"]["tenantName"] = "admin"
        auth_req['auth']['passwordCredentials'] = {"username": "federated-server", "password": "KEYSTONE"}
        auth_token = self.request(post_endpoint, data=auth_req, method="POST")
        header = {"X-Auth-Token": auth_token['access']['token']['id']}
        #header = {"X-Auth-Token": "ADMIN"}
        print header
        validatedResponse = self.request(keystoneEndpoint=endpoint, data=token_id, method="GET", header=header)
        validatedAttributes = {}
        for r in validatedResponse['access']['user']['roles']:
            if validatedAttributes.get('role') is None:
                validatedAttributes['role'] = []
        validatedAttributes['role'].append(r['name'])
        validatedAttributes['project'] = [validatedResponse['access']['token']['tenant']['name']]
        username = validatedResponse['access']['user']['name']
        expires = validatedResponse['access']['token']['expires']
        return username, expires, self.check_issuers(validatedAttributes, realm_id)

    ## Send a request that will be process by the V2 Keystone
    def request(self, keystoneEndpoint=None, data={}, method="GET", header={}):
        headers = header
        if method == "GET":
            req = urllib2.Request(keystoneEndpoint + data, headers = header)
            response = urllib2.urlopen(req)
        elif method == "POST":
            data = json.dumps(data)
            headers['Content-Type'] = 'application/json'
            req = urllib2.Request(keystoneEndpoint, data, header)
            response = urllib2.urlopen(req)
        return json.loads(response.read())

    def check_issuers(self, atts, realm_id):
        context = {"is_admin": True}
        valid_atts = {}
        for att in atts:
           for val in atts[att]:
               org_atts = self.org_mapping_api.list_org_attributes(context)['org_attributes']
               LOG.debug("The retrieved Irg Atts are:")
               LOG.debug(org_atts)
               for org_att in org_atts:
                   if org_att['type'] == att:
                       if org_att['value'] == val or att['value'] is None:
                           print org_att['id']
                           print org_att
                           print att+"  "+val
                           try:
                               self.org_mapping_api.check_attribute_can_be_issued(context, service_id=realm_id, org_attribute_id=org_att['id'])
                               if valid_atts.get(att) is None:
                                   valid_atts[att] = [val]
                               else:
                                   valid_atts[att].append(val)
                           except exception.NotFound:
                               pass
        return valid_atts

def valid_Response(response):
    resp = webob.Response(content_type='application/json')
    resp.body = json.dumps(response)
    return resp
        
def inflate(data):
        decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
        )
        inflated = decompress.decompress(data)
        inflated += decompress.flush()
        return inflated
