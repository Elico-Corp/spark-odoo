# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Qing Wang <wang.qing@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import erppeek


class ServerProxy:

    def __init__(self, server, database, user, password):
        self.server = server
        self.database = database
        self.user = user
        self.password = password

    def login(self):
        client = erppeek.Client(
            self.server, self.database, self.user, self.password)
        return client

    def browse(self, session, model_name, domain):
        """
            The argument domain accepts a single integer id
            , a list of ids or a search domain.
        """
        model_instance = session.model(model_name)
        record_list = model_instance.browse(domain)
        return record_list

    def search(self, session, model_name, domain):
        ids = session.search(model_name, domain)
        return ids

    def read(self, session, model_name, domain, fields=None, offset=0,
             limit=None, order=None, context=None):
        return \
            session.read(model_name, domain, fields=fields, offset=offset,
                         limit=limit, order=order, context=context)

    def write(self, session, model_name, ids, values, context=None):
        return session.write(model_name, ids, values, context=context)

    def create(self, session, model_name, values, context=None):
        return session.create(model_name, values, context=context)
