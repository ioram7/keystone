'''
Created on 7 Jun 2013

@author: kwss

'''
import urlparse
import base64

from lxml.etree import ElementTree, fromstring

from keystone import exception
class SAML(object):
    
    def validate(self, auth_payload):
            # Get the validation information
            validation = auth_payload.get("validation")
            if not validation:
                raise exception.ValidationError(attribute="validation", target=auth_payload)
            
            unique_attribute = validation.get("identifier_attribute",None)
            
            assertion = auth_payload.get("assertion")
            if not assertion:
                raise exception.ValidationError(attribute="assertion", target=auth_payload)
            
            assertion = self.parse_response(assertion, validation)
            
            atts = {}
            names = []
            for cond in assertion.iter("{urn:oasis:names:tc:SAML:2.0:assertion}Conditions"):
                expires = cond.attrib.get("NotOnOrAfter")
    
            for name in assertion.iter("{urn:oasis:names:tc:SAML:2.0:assertion}NameID"):
                names.append(name.text)
            for att in assertion.iter("{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"):
                ats = []
                for value in att.iter("{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue"):
                    ats.append(value.text)
                atts[att.get("Name")] = ats
            if unique_attribute is not None and atts.get(unique_attribute, None) is not None:
                names = atts.get(unique_attribute)
            return names[0], atts, expires
        
        
    def check_signature(self, assertion, validation):
        return True
    
    def negotiate(self, negotiation):
        raise exception.NotImplemented()
    
    def parse_response(self, assertion, validation):
        resp = urlparse.parse_qsl(assertion)
        k, v = resp[0]
        try:
            resp = ElementTree(fromstring(v))
        except Exception as e:
            print e
            try:
                resp = base64.b64decode(v)
                print resp
                resp = ElementTree(fromstring(resp))
            except Exception:
                resp = base64.b64decode(v.replace(" ", "+"))
                print resp
                resp = ElementTree(fromstring(resp))
        if self.check_signature(assertion, validation):
            return resp
        else:
            raise exception.Unauthorized("The signature of the authentication could not be verified")
        