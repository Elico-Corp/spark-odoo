# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
#    Eric Caudal <eric.caudal@elico-corp.com>

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
from openerp.addons.connector.unit.mapper import ExportMapper


class ICOPSExportMapper(ExportMapper):
    def __init__(self, environment):
        """

        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(ICOPSExportMapper, self).__init__(environment)
        self._icops = None
        self._backend_to = None

    def _format_child_rows(self, child_records):
        return [(5, 0)] + [(0, 0, data) for data in child_records]

    def _init_child_mapper(self, model_name):
        mapper = super(ICOPSExportMapper, self)._init_child_mapper(model_name)
        mapper._icops = self._icops
        mapper._backend_to = self._backend_to
        return mapper

    def _get_mapping(self, name, record):
        res = {}
        for method in dir(self):
            if method.startswith('%s_' % name):
                new_dict = getattr(self, method)(record)
                res = dict(res.items() + new_dict.items())
        return res
