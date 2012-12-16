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
Created on 16 Jul 2012

@author: Matteo Casenove
'''

import logging

import webob.dec
import webob.exc

import json as simplejson

from keystone.middleware.federatedAccess.cvm_engine import CVM_Engine
from keystone.middleware.federatedAccess.auth_discover import AuthDiscover
from keystone.middleware.federatedAccess.auth_validator import AuthValidator

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

        self.cvm = CVM_Engine(self.app, self.conf)

        self.disco = AuthDiscover(app, conf)
        self.validator = AuthValidator(app, conf)

        LOG.info('Starting federated middleware wrapper')
        LOG.info('Init FederatedAuthentication!')

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, req):
        LOG.debug('Request intercepted by CVM')
        LOG.debug('--------------------------')
        if not 'HTTP_X_AUTHENTICATION_TYPE' in req.environ:
            return self.app(req)
        if not req.environ['HTTP_X_AUTHENTICATION_TYPE'] in ('federated'):
            return self.app(req)

        body = req.body
        data = simplejson.loads(body)

        if 'idpResponse' in data:
            validatedUserAttributes = self.validator.validate(data)
            return self.cvm.engine(data, validatedUserAttributes)
        else:
            if 'realm' in data:
                return self.disco.discovery(data['realm'])
            return self.disco.getRealmList()


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def auth_filter(app):
        return FederatedAuthentication(app, conf)
    return auth_filter
