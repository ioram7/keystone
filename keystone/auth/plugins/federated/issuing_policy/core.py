'''
Created on 5 Jun 2013

@author: kwss
'''
from keystone import exception
from keystone.common import config

CONF = config.CONF

    
class Default(object):
    
    
    def check_issuers(self, attributes, provider):
        pass