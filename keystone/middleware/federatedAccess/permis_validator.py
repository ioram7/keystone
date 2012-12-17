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
import xml.etree.ElementTree as etree
import urlparse
import urllib
import zlib
import base64
import logging
LOG = logging.getLogger(__name__)


class PermisValidator(object):

    def __init__(self):
        return None

    def __call__(self):
        return None

    def validate(self, data):
        PREFIX = "{urn:oasis:names:tc:SAML:2.0:assertion}"
        resp = urlparse.parse_qsl(data['idpResponse'])
        k, v = resp[0]
        resp = base64.b64decode(v)
        resp = etree.ElementTree(etree.fromstring(resp))
        atts = {}
        names = []
        for name in resp.iter(PREFIX + "NameID"):
            names.append(name.text)
        if(len(names) > 0):
            atts["NameID"] = names
        for att in resp.iter(PREFIX + "Attribute"):
            ats = []
            for value in att.iter(PREFIX + "AttributeValue"):
                ats.append(value.text)
            atts[att.get("Name")] = ats
        return atts


def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


def factory():
    return PermisValidator()
