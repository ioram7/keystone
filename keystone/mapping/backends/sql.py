from keystone.mapping.org import Driver as OrgDriver
from keystone.common import sql

class Mapping(sql.Base, OrgDriver):
	def __init__(self):
		super(Mapping)
	def create_org_attribute_set(self, context, org_att_id, org_att_ref):
		session = self.get_session()
		with session.begin():
			service = OrgAttributeSet.from_dict(org_att_ref)
			session.add(service)
			session.flush()
		return service.to_dict()


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
