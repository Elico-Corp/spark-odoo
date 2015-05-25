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

    @property
    def data(self):
        """ Returns a dict for a record processed by
        :py:meth:`~_convert` """
        if self._data is None:
            raise ValueError('Mapper.convert should be called before '
                             'accessing the data')
        result = self._data.copy()
        for attr, mappers in self._data_children.iteritems():
            child_data = [mapper.data for mapper in mappers]
            if child_data:
                result[attr] = self._format_child_rows(child_data, attr)
        return self._after_mapping(result)

    @property
    def data_for_create(self):
        """ Returns a dict for a record processed by
        :py:meth:`~_convert` to use only for creation of the record. """
        if self._data is None:
            raise ValueError('Mapper.convert should be called before '
                             'accessing the data')
        result = self._data.copy()
        result.update(self._data_for_create)
        for attr, mappers in self._data_children.iteritems():
            child_data = [mapper.data_for_create for mapper in mappers]
            if child_data:
                result[attr] = self._format_child_rows(child_data, attr)
        return self._after_mapping(result)

    def _get_children_model(self, model, attr):
        # get the children field model
        sess = self.session
        model_pool = sess.pool.get('ir.model')
        model_ids = model_pool.search(
            sess.cr, sess.uid, [('model', '=', model)], context=sess.context)
        fields_pool = sess.pool.get('ir.model.fields')
        field_ids = fields_pool.search(
            sess.cr, sess.uid,
            [('model_id', '=', model_ids[0]), ('name', '=', attr)],
            context=sess.context
        )
        field = fields_pool.browse(
            sess.cr, sess.uid, field_ids[0], context=sess.context)
        return field.relation

    def _format_child_rows(self, child_records, attr):
        backend = self._backend_to
        ic_uid = backend.icops_uid.id
        sess = self.session
        pool = sess.pool.get(
            self._get_children_model(self._icops.model_dest, attr))
        res = []
        # stock the list of child ids present in the main object
        # it will be used later to know what to remove in the icops object
        new_ids = []
        for record in child_records:
            import pdb
            pdb.set_trace()
            new_ids.append(record['icops_id'])
            domain = [
                ('icops_id', '=', record['icops_id']),
                ('order_id.icops_id', '=', self._data['icops_id']),
                ('order_id.icops_model', '=', self._data['icops_model'])
            ]
            ids = pool.search(sess.cr, ic_uid, domain, context=sess.context)
            # update old line
            if ids:
                res.append((1, ids[0], record))
            # write new line
            else:
                res.append((0, 0, record))
        # search for the lines that need to be deleted
        if not res:
            return [(5, 0)]
        domain = [
            ('icops_id', 'not in', new_ids),
            ('order_id.icops_id', '=', self._data['icops_id']),
            ('order_id.icops_model', '=', self._data['icops_model'])
        ]
        unlink_ids = pool.search(sess.cr, ic_uid, domain, context=sess.context)
        res += [(2, unlink_id) for unlink_id in unlink_ids]

        return res

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
