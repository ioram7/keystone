# Copyright 2014 IBM Corp.
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

import sqlalchemy as sql

from keystone.common import sql as ks_sql
from keystone.contrib.federation.backends import sql as federation_sql

VO_TABLE = 'virtual_org'
VO_REQUEST_TABLE = 'vo_request'
VO_BLACKLIST_TABLE = 'vo_blacklist'


def upgrade(migrate_engine):
    meta = sql.MetaData()
    meta.bind = migrate_engine

    sql.Table('group', meta, autoload=True)
    vo_table = sql.Table(
        VO_TABLE,
        meta,
        sql.Column('id', sql.String(64), primary_key=True),
        sql.Column('vo_name', sql.String(64), nullable=False),
	sql.Column('vo_role', sql.String(64), nullable=False),
        sql.Column('group_id', sql.String(64), sql.ForeignKey('group.id'),
                   nullable=False),
	sql.Column('enabled', sql.Boolean, nullable=False),
	sql.Column('automatic_join', sql.Boolean, nullable=False),
	sql.Column('vo_is_domain', sql.Boolean, nullable=False),
	sql.Column('pin', sql.String(64), nullable=True),
        sql.Column('description', sql.Text),
        sql.Column('extra', ks_sql.JsonBlob.impl),
        mysql_engine='InnoDB',
        mysql_charset='utf8')
    vo_table.create(migrate_engine, checkfirst=True)

    vo_request_table = sql.Table(
        VO_REQUEST_TABLE,
        meta,
        sql.Column('id', sql.String(64), primary_key=True),
        sql.Column('user_id', sql.String(64), nullable=False),
        sql.Column('vo_role_id', sql.String(64), sql.ForeignKey('virtual_org.id'),
                   nullable=False),
        sql.Column('idp', sql.String(64), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8')
    vo_request_table.create(migrate_engine, checkfirst=True)

    vo_blacklist_table = sql.Table(
        VO_BLACKLIST_TABLE,
        meta,
        sql.Column('id', sql.String(64), primary_key=True),
         sql.Column('user_id', sql.String(64), nullable=False),
        sql.Column('vo_role_id', sql.String(64), sql.ForeignKey('virtual_org.id'),
                   nullable=False),
        sql.Column('idp', sql.String(64), nullable=False),
        sql.Column('count', sql.Integer, nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8')
    vo_blacklist_table.create(migrate_engine, checkfirst=True)


def downgrade(migrate_engine):
    meta = sql.MetaData()
    meta.bind = migrate_engine
    vo = sql.Table(VO_TABLE, meta, autoload=True)
    vo.drop(migrate_engine, checkfirst=True)
    vo_request = sql.Table(VO_REQUEST_TABLE, meta, autoload=True)
    vo_request.drop(migrate_engine, checkfirst=True)
    vo_bl = sql.Table(VO_BLACKLIST_TABLE, meta, autoload=True)
    vo_bl.drop(migrate_engine, checkfirst=True)
