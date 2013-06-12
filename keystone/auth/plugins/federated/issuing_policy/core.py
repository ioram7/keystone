'''
Created on 5 Jun 2013

@author: kwss
'''
from keystone import exception
from keystone.common import config
from keystone.common import manager

CONF = config.CONF


class Manager(manager.Manager):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super(Manager).__init__(CONF.auth.get("issuing_policy"))

    
class DefaultIssuingPolicy(object):
    
    
    def check_attributes(self, attributes):
        raise exception.NotImplemented()