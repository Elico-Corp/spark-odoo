# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2016 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Liu Lixia
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
from openerp.osv import fields, orm


class MMXProductRace(orm.Model):
    _inherit = 'product.race'

    _columns = {
        'backend_ids': fields.many2many(
            'magento.backend',
            'race_magento_backend_rel',
            'race_id',
            'backend_id',
            'Magento Backend'),
        'attribute_id': fields.many2one(
            'magento.product.attribute', 'Magento Attribute', required=True),
        'magento_bind_ids': fields.one2many(
            'magento.attribute.option', 'race_id', 'Magento Option'),
    }

    def create(self, cr, uid, vals, context=None):
        res_id = super(MMXProductRace, self).create(
            cr, uid, vals, context=context)

        race_obj = self.browse(cr, uid, res_id, context=context)

        backend_ids = self.resolve_2many_commands(
            cr, uid, 'backend_ids', vals['backend_ids'], ['id'], context)

        for backend_id in backend_ids:
            attribute_id = vals['attribute_id']
            option_vals = {
                'name': vals['name'],
                'backend_id': backend_id.get('id'),
                'magento_attribute_id': attribute_id,
                'value': race_obj.name,
                'race_id': res_id,
            }
            self.pool.get('magento.attribute.option').create(
                cr, uid, option_vals, context=context)

        return res_id

    def _get_all_backends(self, cr, uid, context=None):
        '''return all the backends'''
        backend_pool = self.pool['magento.backend']
        ids = backend_pool.search(cr, uid, [], context=context)
        return ids

    _defaults = {
        'backend_ids': _get_all_backends
    }
