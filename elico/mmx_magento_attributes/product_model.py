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
            'magento.product.attribute', 'Magento Attribute', required=True),
        'magento_bind_ids': fields.one2many(
            'magento.attribute.option', 'model_id', 'Magento Option'),
    }

    def create(self, cr, uid, vals, context=None):
        res_id = super(MMXProductModel, self).create(
            cr, uid, vals, context=context)

        for backend_id in vals['backend_ids']:
            attribute_id = vals['attribute_id']
            option_vals = {
                'name': vals['name'],
                'backend_id': backend_id,
                'magento_attribute_id': attribute_id,
                'value': res_id,
                'model_id': res_id,
            }
            self.pool.get('magento.attribute.option').create(
                cr, uid, option_vals, context=context)

        return res_id
