'''
Created on 5 Jun 2013

@author: kwss
'''
from keystone.common import config
from keystone import exception
from keystone.common import manager


CONF = config.CONF

class Manager(manager.Manager):
    '''
    Default pivot point for the mapping API
    '''


    def __init__(self):
        super(Manager).__init__(CONF.mapping.get("driver"))

    def map(self, attributes):
        # Call the mapping back end
        raise exception.NotImplemented()
