import time
import uuid

from keystone import identity
from keystone.openstack.common import timeutils


class UserManager(object):

    def __init__(self):
       self.identity_api = identity.controllers.UserV3()

    def manage(self, username, expires):
		# Clean up old users
        self.cleanup()
		# Create User
        tempPass = uuid.uuid4().hex
        user_ref = {'name': username, 'password': tempPass, 'expires': expires}
        user = self.identity_api.create_user({'is_admin': True}, user=user_ref)['user']
		# Return user
        return user, tempPass


    def cleanup(self):
        expired_users = self.identity_api.get_expired_users(context={"is_admin": True})
        for u in expired_users:
            print "delete this"
            print u
