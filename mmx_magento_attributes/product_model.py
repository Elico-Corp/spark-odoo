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
from openerp.osv import orm, fields
from openerp.osv.osv import except_osv


class MMXProductModel(orm.Model):
    _inherit = 'product.model'

    _columns = {
        'backend_ids': fields.many2many(
            'magento.backend',
            'model_magento_backend_rel',
            'model_id',
            'backend_id',
            'Magento Backend'),
        'attribute_id': fields.many2one(
            'magento.product.attribute', 'Magento Attribute', required=False),
        'magento_bind_ids': fields.one2many(
            'magento.attribute.option', 'model_id', 'Magento Option'),
    }

    def create(self, cr, uid, vals, context=None):
        res_id = super(MMXProductModel, self).create(
            cr, uid, vals, context=context)
        pro_model = self.pool.get('product.model')
        pro_model_obj = pro_model.browse(cr, uid, res_id, context=context)

        backend_ids = self.resolve_2many_commands(
            cr, uid, 'backend_ids', vals['backend_ids'], ['id'], context)

        default_attribute_ids = self.pool.get(
            'magento.product.attribute').search(
            cr, uid, [('attribute_code', '=', 'x_mmx_model')])

        if default_attribute_ids:
            default_attribute_id = default_attribute_ids[0]

            for backend_id in backend_ids:
                attribute_id = default_attribute_id
                option_vals = {
                    'name': ''.join([pro_model_obj.manufacturer_id.name, r'_', pro_model_obj.name]),
                    'backend_id': backend_id.get('id'),
                    'magento_attribute_id': attribute_id,
                    'value': vals['name'],
                    'model_id': res_id,
                }
                self.pool.get('magento.attribute.option').create(
                    cr, uid, option_vals, context=context)
        else:
            msg = "You have not created magento attribute 'x_mmx_model' yet !\n \
            Please create one first."
            raise except_osv(('Warning !'), (msg))

        return res_id

    def _get_default_attribute_id(self, cr, uid, context=None):
        """Get the x_mmx_race_edition(MMX)attribute_id as default value."""
        res = False
        attribute_id = self.pool.get(
            'magento.product.attribute').search(
            cr, uid, [
                ('attribute_code', '=', 'x_mmx_race_edition'),
                ('backend_id', '=', 'MMX')
            ])
        if attribute_id:
            res = attribute_id[0]
        return res

    def _get_all_backends(self, cr, uid, context=None):
        '''return all the backends'''
        backend_pool = self.pool['magento.backend']
        ids = backend_pool.search(cr, uid, [], context=context)
        return ids

    _defaults = {
        'backend_ids': _get_all_backends,
        'attribute_id': _get_default_attribute_id,
    }
