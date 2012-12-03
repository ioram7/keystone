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
LOG = logging.getLogger(__name__)

class ExampleDS(object):
    
    def __init__(self):
	self.confReader = DiscoveryConfigParser()
        return None
        
    def discover(self, realm):
	LOG.info('Discovering '+realm['name'])
        info = self.confReader.getIdpInfo(realm['name'])
	if info == None:
		LOG.error("The realm was not discovered in the metadata: Please check your directory service configuration is correct")
	else:
		LOG.info("Realm: "+realm['name']+" found:")
		LOG.info(info)
	handler = MetadataHandler()
	endpoint=handler.getEndpointForEntityById(info['EntityID'], info["Location"])
	endpoint+="?"
	return endpoint   	

    def getIdPList(self):
	return self.confReader.getIdpList() 
    def __call__(self):
        return None

import xml.etree.ElementTree as ET

# Class for parsing the discovery config
class DiscoveryConfigParser(object):
	def __init__(self):
		etree = ET.parse("Config.xml")
		self.idps = {}
		for idp in etree.getroot().findall("IdentityProvider"):
			for n in idp.findall("Name"):
				name = n
			for e in  idp.findall("EntityID"):
				id = e
			for l in idp.findall("MetadataLocation"):
				location = l
			self.idps[name.text] = {"EntityID":id.text, "Location":location.text}
	def getIdpList(self):
		list = []
                for idp in self.idps.keys():
                        list.append({'name':idp})
                return {'realms':list}
			

	def getIdpInfo(self, name):
		return self.idps[name]	   
    
class MetadataHandler(object):
	def __init__(self):
		self.elem = None
	def getEndpointForEntityById(self, entityId, metadataLocation, binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"):
		self.elem = None
		etree = ET.parse(metadataLocation)
		for elem in etree.getroot().iter("{urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor"):
			if elem.attrib.get('entityID') == entityId:
				self.elem = elem
		if self.elem == None:
			print "Not found"
			return "Not found in metadata"
		else:
			for child in self.elem.iter("{urn:oasis:names:tc:SAML:2.0:metadata}SingleSignOnService"):
				if child.tag == '{urn:oasis:names:tc:SAML:2.0:metadata}SingleSignOnService':
					if child.attrib.get("Binding") == binding:
						return child.attrib.get("Location")
				else:
					return "Endpoint Not Found"
	
	def getCertificateData(self, entityId, metadataLocation):
		self.elem = None
                etree = ET.parse(metadataLocation)
                for elem in etree.getroot().iter("{urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor"):
                        if elem.attrib.get('entityID') == entityId:
                                self.elem = elem
		for item in self.elem.iter("{http://www.w3.org/2000/09/xmldsig#}X509Certificate"):
			return item.text.strip()    
    
