from keystone.mapping import Driver
from keystone.common import sql
from keystone import exception


class Mapping(sql.Base, Driver):

	def __init__(self):
		super(Mapping)
	# Organisational
	#Sets
	def create_org_attribute_set(self, context, org_set_id, org_set_ref):
		session = self.get_session()
		with session.begin():
			orgset = OrgAttributeSet.from_dict(org_set_ref)
			session.add(orgset)
			session.flush()
		return orgset.to_dict()
	def get_org_set(self, set_id):
		session = self.get_session()
		return self._get_org_set(session, set_id).to_dict()
	def _get_org_set(self, session, set_id):
		try:
			return session.query(OrgAttributeSet).filter_by(id=set_id).one()
		except sql.NotFound:
			raise exception.ServiceNotFound(set_id=set_id)
	def list_org_sets(self):
		session = self.get_session()
		sets = session.query(OrgAttributeSet).all()
		return [s.to_dict() for s in list(sets)]
	def delete_org_set(self, set_id):
		session = self.get_session()
		with session.begin():
			ref = self._get_org_set(session, set_id)
			session.delete(ref)
			session.flush()
	# Attributes
	def create_org_attribute(self, context, org_att_id, org_att_ref):
		session = self.get_session()
		with session.begin():
			attribute = OrgAttribute.from_dict(org_att_ref)
			session.add(attribute)
			session.flush()
		return attribute.to_dict()
    
	def get_org_att(self, attribute_id):
		session = self.get_session()
		return self._get_org_att(session, attribute_id).to_dict()
    
	def _get_org_att(self, session, attribute_id):
		try:
			return session.query(OrgAttribute).filter_by(id=attribute_id).one()
		except sql.NotFound:
			raise exception.ServiceNotFound(id=attribute_id)
    
	def list_org_atts(self):
		session = self.get_session()
		attributes = session.query(OrgAttribute).all()
		return [s.to_dict() for s in list(attributes)]
    
	def delete_org_att(self, attribute_id):
		session = self.get_session()
		with session.begin():
			ref = self._get_org_att(session, attribute_id)
			session.delete(ref)
			session.flush()


class OrgAttributeSet(sql.ModelBase, sql.DictBase):
    __tablename__ = 'orgattributeset'
    id = sql.Column(sql.String(64), primary_key=True)
    extra = sql.Column(sql.JsonBlob())

    @classmethod
    def from_dict(cls, service_dict):
        extra = {}
        for k, v in service_dict.copy().iteritems():
            if k not in ['id', 'extra']:
                extra[k] = service_dict.pop(k)

        service_dict['extra'] = extra
        return cls(**service_dict)

    def to_dict(self):
        extra_copy = self.extra.copy()
        extra_copy['id'] = self.id
        return extra_copy

class OrgAttribute(sql.ModelBase, sql.DictBase):
	__tablename__ = 'orgattribute'
	id = sql.Column(sql.String(64), primary_key=True)
	type = sql.Column(sql.String(255))
	value = sql.Column(sql.String(255))
	extra = sql.Column(sql.JsonBlob())

	@classmethod
	def from_dict(cls, service_dict):
		extra = {}
		for k, v in service_dict.copy().iteritems():
			if k not in ['id', 'type', 'value', 'extra']:
				extra[k] = service_dict.pop(k)

		service_dict['extra'] = extra
		return cls(**service_dict)

	def to_dict(self):
		extra_copy = self.extra.copy()
		extra_copy['id'] = self.id
		extra_copy['type'] = self.type
		extra_copy['value'] = self.value
		return extra_copy

class OrgAttributeAssociation(sql.ModelBase, sql.DictBase):
	__tablename__ = 'org_attribute_association'
	id = sql.Column(sql.String(64), primary_key=True)
	org_attribute_id = sql.Column(sql.String(64), sql.ForeignKey('org_attribute.id'))
	org_attribute_set_id = sql.Column(sql.String(64),  sql.ForeignKey('org_attribute_set.id'))

	@classmethod
	def from_dict(cls, service_dict):
		extra = {}
		for k, v in service_dict.copy().iteritems():
			if k not in ['id', 'org_attribute_set_id', 'org_attribute_id', 'extra']:
				extra[k] = service_dict.pop(k)

		service_dict['extra'] = extra
		return cls(**service_dict)

	def to_dict(self):
		extra_copy = self.extra.copy()
		extra_copy['id'] = self.id
		extra_copy['org_attribute_id'] = self.org_attribute_id
		extra_copy['org_attribute_set_id'] = self.org_attribute_set_id
		return extra_copy
