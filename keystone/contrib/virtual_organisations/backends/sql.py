# Copyright 2014 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from keystone.common import sql
from keystone.contrib.virtual_organisations import core
from keystone import exception
from keystone.openstack.common import jsonutils


class VirtualOrganisationRoleModel(sql.ModelBase, sql.DictBase):
    __tablename__ = 'virtual_org'
    attributes = ['id', 'name', 'vo_role', 'group_id', 'pin',
        'automatic_join', 'enabled', 'description', 'vo_is_domain']
    mutable_attributes = frozenset(['pin'])

    id = sql.Column(sql.String(64), primary_key=True)
    group_id = sql.Column(sql.String(64), sql.ForeignKey('group.id'))
    name = sql.Column(sql.String(64), nullable=False)
    description = sql.Column(sql.Text, nullable=True)
    vo_role = sql.Column(sql.String(64), nullable=False)
    pin = sql.Column(sql.String(64), nullable=True)
    enabled = sql.Column(sql.Boolean, nullable=False)
    automatic_join = sql.Column(sql.Boolean, nullable=False)
    vo_is_domain = sql.Column(sql.Boolean, nullable=False)

    @classmethod
    def from_dict(cls, dictionary):
        new_dictionary = dictionary.copy()
        return cls(**new_dictionary)

    def to_dict(self):
        """Return a dictionary with model's attributes."""
        d = dict()
        for attr in self.__class__.attributes:
            d[attr] = getattr(self, attr)
        return d

class VirtualOrganisationRequestModel(sql.ModelBase, sql.DictBase):
    __tablename__ = 'vo_request'
    attributes = ['id', 'vo_role_id', 'idp', 'user_id']
    mutable_attributes = frozenset([])

    id = sql.Column(sql.String(64), primary_key=True)
    vo_role_id = sql.Column(sql.String(64), sql.ForeignKey('virtual_org.id',
                        ondelete='CASCADE'))
    user_id = sql.Column(sql.String(64), nullable=False)
    idp = sql.Column(sql.String(64), nullable=False)
    

    @classmethod
    def from_dict(cls, dictionary):
        new_dictionary = dictionary.copy()
        return cls(**new_dictionary)

    def to_dict(self):
        """Return a dictionary with model's attributes."""
        d = dict()
        for attr in self.__class__.attributes:
            d[attr] = getattr(self, attr)
        return d

class VirtualOrganisationBlackListModel(sql.ModelBase, sql.DictBase):
    __tablename__ = 'vo_blacklist'
    attributes = ['id', 'vo_role_id', 'idp', 'user_id', 'count']
    mutable_attributes = frozenset(['count'])

    id = sql.Column(sql.String(64), primary_key=True)
    vo_role_id = sql.Column(sql.String(64), sql.ForeignKey('virtual_org.id',
                        ondelete='CASCADE'))
    user_id = sql.Column(sql.String(64), nullable=False)
    idp = sql.Column(sql.String(64), nullable=False)
    count = sql.Column(sql.Integer, nullable=False)

    @classmethod
    def from_dict(cls, dictionary):
        new_dictionary = dictionary.copy()
        return cls(**new_dictionary)

    def to_dict(self):
        """Return a dictionary with model's attributes."""
        d = dict()
        for attr in self.__class__.attributes:
            d[attr] = getattr(self, attr)
        return d

class VirtualOrganisation(core.Driver):

    # Virtual organisation CRUD
    @sql.handle_conflicts(conflict_type='vo_role')
    def create_vo_role(self, vo_role_id, vo_role):
        session = sql.get_session()
        with session.begin():
            vo_role['id'] = vo_role_id
            vo_role_ref = VirtualOrganisationRoleModel.from_dict(vo_role)
            session.add(vo_role_ref)
        return vo_role_ref.to_dict()

    def delete_vo_role(self, vo_role_id):
        session = sql.get_session()
        with session.begin():
            vo_role_ref = self._get_vo_role(session, vo_role_id)
            q = session.query(VirtualOrganisationRoleModel)
            q = q.filter_by(id=vo_role_id)
            q.delete(synchronize_session=False)
            session.delete(vo_role_ref)

    def _get_vo_role(self, session, vo_role_id):
        vo_role_ref = session.query(VirtualOrganisationRoleModel).get(vo_role_id)
        if not vo_role_ref:
            raise exception.VirtualOrganisationRoleNotFound(vo_role_id=vo_role_id)
        return vo_role_ref

    def list_vo_roles(self):
        session = sql.get_session()
        with session.begin():
            vo_roles = session.query(VirtualOrganisationRoleModel)
        vo_roles_list = [vo_role.to_dict() for vo_role in vo_roles]
        return vo_roles_list

    def get_vo_role(self, vo_role_id):
        session = sql.get_session()
        vo_role_ref = self._get_vo_role(session, vo_role_id)
        return vo_role_ref.to_dict()
    
    def get_vo_role_by_name_and_role(self, vo_name, vo_role):
        session = sql.get_session()
        q = session.query(VirtualOrganisationRoleModel)
        q = q.filter_by(name=vo_name, vo_role=vo_role)
        vo_role_ref = q.first()
        return vo_role_ref.to_dict()


    def update_vo_role(self, vo_role_id, vo_role):
        session = sql.get_session()
        with session.begin():
            vo_role_ref = self._get_vo_role(session, vo_role_id)
            old_vo_role = vo_role_ref.to_dict()
            old_vo_role.update(vo_role)
            new_vo_role = VirtualOrganisationRoleModel.from_dict(old_vo_role)
            for attr in VirtualOrganisationRoleModel.mutable_attributes:
                setattr(vo_role_ref, attr, getattr(new_vo_role, attr))
        return vo_role_ref.to_dict()

    # Virtual organisation request CRUD
    @sql.handle_conflicts(conflict_type='vo_request')
    def create_vo_request(self, vo_request_id, vo_request):
        session = sql.get_session()
        with session.begin():
            vo_request['id'] = vo_request_id
            vo_request_ref = VirtualOrganisationRequestModel.from_dict(vo_request)
            session.add(vo_request_ref)
        return vo_request_ref.to_dict()

    def delete_vo_request(self, vo_request_id):
        session = sql.get_session()
        with session.begin():
            vo_request_ref = self._get_vo_request(session, vo_request_id)
            q = session.query(VirtualOrganisationRequestModel)
            q = q.filter_by(id=vo_request_id)
            q.delete(synchronize_session=False)
            session.delete(vo_request_ref)

    def _get_vo_request(self, session, vo_request_id):
        vo_request_ref = session.query(VirtualOrganisationRequestModel).get(vo_request_id)
        if not vo_request_ref:
            raise exception.VirtualOrganisationRequestNotFound(vo_request_id=vo_request_id)
        return vo_request_ref

    def list_vo_requests(self, vo_role_id):
        session = sql.get_session()
        with session.begin():
            vo_requests = session.query(VirtualOrganisationRequestModel).filter_by(vo_role_id=vo_role_id)
        vo_requests_list = [vo_request.to_dict() for vo_request in vo_requests]
        return vo_requests_list

    def get_vo_request(self, vo_request_id):
        session = sql.get_session()
        vo_request_ref = self._get_vo_request(session, vo_request_id)
        return vo_request_ref.to_dict()

    def update_vo_request(self, vo_request_id, vo_request):
        session = sql.get_session()
        with session.begin():
            vo_request_ref = self._get_vo_request(session, vo_request_id)
            old_vo_request = vo_request_ref.to_dict()
            old_vo_request.update(vo_request)
            new_vo_request = VirtualOrganisationRequestModel.from_dict(old_vo_request)
            for attr in VirtualOrganisationRequestModel.mutable_attributes:
                setattr(vo_request_ref, attr, getattr(new_vo_request, attr))
        return vo_request_ref.to_dict()

    def get_request_for_user(self, user_id, vo_role_id):
        session = sql.get_session()
        with session.begin():
            vo_requests = session.query(VirtualOrganisationRequestModel).filter_by(user_id=user_id, vo_role_id=vo_role_id)
        vo_requests_list = [vo_request.to_dict() for vo_request in vo_requests]
        print len(vo_requests_list)
        if len(vo_requests_list) == 0:
            return
        return vo_requests_list.pop()


    # Virtual organisation request CRUD
    @sql.handle_conflicts(conflict_type='vo_blacklist')
    def create_vo_blacklist(self, vo_blacklist_id, vo_blacklist):
        session = sql.get_session()
        with session.begin():
            vo_blacklist['id'] = vo_blacklist_id
            vo_blacklist_ref = VirtualOrganisationBlackListModel.from_dict(vo_blacklist)
            session.add(vo_blacklist_ref)
        return vo_blacklist_ref.to_dict()

    def delete_vo_blacklist(self, vo_blacklist_id):
        session = sql.get_session()
        with session.begin():
            vo_blacklist_ref = self._get_vo_blacklist(session, vo_blacklist_id)
            q = session.query(VirtualOrganisationBlackListModel)
            q = q.filter_by(id=vo_blacklist_id)
            q.delete(synchronize_session=False)
            session.delete(vo_blacklist_ref)

    def _get_vo_blacklist(self, session, vo_blacklist_id):
        vo_blacklist_ref = session.query(VirtualOrganisationBlackListModel).get(vo_blacklist_id)
        if not vo_blacklist_ref:
            raise exception.VirtualOrganisationBlackListNotFound(vo_blacklist_id=vo_blacklist_id)
        return vo_blacklist_ref

    def list_vo_blacklists(self):
        session = sql.get_session()
        with session.begin():
            vo_blacklists = session.query(VirtualOrganisationBlackListModel).filter_by(count > 3)
        vo_blacklists_list = [vo_blacklist.to_dict() for vo_blacklist in vo_blacklists]
        return vo_blacklists_list
    
    def list_vo_blacklists_for_vo(self, vo_role_id):
        session = sql.get_session()
        with session.begin():
            vo_blacklists = session.query(VirtualOrganisationBlackListModel).filter(VirtualOrganisationBlackListModel.count > 2)
        vo_blacklists_list = [vo_blacklist.to_dict() for vo_blacklist in vo_blacklists]
        return vo_blacklists_list

    def get_vo_blacklist_for_user(self, user_id, vo_role_id, idp):
        session = sql.get_session()
        with session.begin():
            vo_blacklists = session.query(VirtualOrganisationBlackListModel).filter_by(user_id=user_id, vo_role_id=vo_role_id, idp=idp)
        vo_blacklists_list = [vo_blacklist.to_dict() for vo_blacklist in vo_blacklists]
        print len(vo_blacklists_list)
        if len(vo_blacklists_list) == 0:
            return
        return vo_blacklists_list.pop()

    def get_vo_blacklist(self, vo_blacklist_id):
        session = sql.get_session()
        vo_blacklist_ref = self._get_vo_blacklist(session, vo_blacklist_id)
        return vo_blacklist_ref.to_dict()

    def update_vo_blacklist(self, vo_blacklist_id, vo_blacklist):
        session = sql.get_session()
        with session.begin():
            vo_blacklist_ref = self._get_vo_blacklist(session, vo_blacklist_id)
            old_vo_blacklist = vo_blacklist_ref.to_dict()
            old_vo_blacklist.update(vo_blacklist)
            new_vo_blacklist = VirtualOrganisationBlackListModel.from_dict(old_vo_blacklist)
            for attr in VirtualOrganisationBlackListModel.mutable_attributes:
                setattr(vo_blacklist_ref, attr, getattr(new_vo_blacklist, attr))
        return vo_blacklist_ref.to_dict()
