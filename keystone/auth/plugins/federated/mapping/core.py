'''
Created on 5 Jun 2013

@author: kwss
'''
from keystone.common import config
from keystone import exception
from keystone.common import manager


CONF = config.CONF

class Default(object):

    def map(self, attributes):
        # Call the mapping back end
        pass
