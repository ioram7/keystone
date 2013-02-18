import time
import uuid

from keystone import identity
from keystone import exception
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
        try:
            user = self.identity_api.create_user({'is_admin': True}, user=user_ref)['user']
        except exception.Conflict:
            users = self.identity_api.list_users({"is_admin": True, "query_string":{}})
            for u in users["users"]:
                if username == u["name"]:
                    user = u
                    user.pop('expires')
                    user['password'] = tempPass
                    self.identity_api.update_user({"is_admin": True}, user_id=user['id'], user=user) 
		# Return user
        return user, tempPass


    def cleanup(self):
        expired_users = self.identity_api.get_expired_users(context={"is_admin": True})
        for u in expired_users["users"]:
            self.identity_api.delete_user({"is_admin": True},user_id=u["id"]) 
