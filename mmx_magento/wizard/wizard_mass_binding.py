# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#     Jon Chow <jon.chow@elico-corp.com>
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

from openerp.osv import fields, osv


class wizard_customs_invoice_report(osv.osv_memory):
    _name = 'wizard.mass.binding'

    def product_type_get(self, cr, uid, context=None):
        return [
            ('simple', 'Simple Product')
        ]

    def _product_type_get(self, cr, uid, context=None):
        return self.product_type_get(cr, uid, context=context)

    _columns = {
        'backend_id': fields.many2one('magento.backend',
                                      string='Backend',
                                      required=True),
        'website_ids': fields.many2many('magento.website',
                                        string='Websites',
                                        required=True),
        'product_type': fields.selection(_product_type_get,
                                         'Magento Product Type',
                                         required=True),
        'attribute_set_id': fields.many2one(
            'magento.attribute.set',
            string='Attribute Set',
            required=True,
            domain="[('backend_id', '=', backend_id)]"),
        'visibility': fields.selection(
            [('1', 'Not Visible Individually'),
             ('2', 'Catalog'),
             ('3', 'Search'),
             ('4', 'Catalog, Search')],
            string='Visibility in Magento',
            required=True),
        'tax_class': fields.selection(
            [('0', 'None'),
             ('2', 'Default'),
             ('3', 'Taxable Goods'),
             ('4', 'Shipping')],
            string='Tax Class in Magento',
        ),
        'status': fields.selection(
            [('1', 'Enabled'),
             ('2', 'Disabled')],
            string='Status in Magento',
            required=True),
        'manage_stock': fields.selection(
            [('use_default', 'Use Default Config'),
             ('no', 'Do Not Manage Stock'),
             ('yes', 'Manage Stock')],
            string='Manage Stock Level',
            required=True),
        'backorders': fields.selection(
            [('use_default', 'Use Default Config'),
             ('no', 'No Sell'),
             ('yes', 'Sell Quantity < 0'),
             ('yes-and-notification',
              'Sell Quantity < 0 and Use Customer Notification')],
            string='Manage Inventory Backorders',
            required=True),
        'magento_qty': fields.float('Computed Quantity',
                                    help="Last computed quantity to send "
                                         "on Magento."),
    }

    _defaults = {
        'product_type': 'simple',
        'manage_stock': 'use_default',
        'backorders': 'use_default',
        'tax_class': '0',
        'status': '1',
        'visibility': '4',
    }

    def assign(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        active_ids = context.get('active_ids', [])
        if not isinstance(active_ids, list):
            active_ids = [active_ids]
        for binding in self.browse(cr, uid, ids, context=context):

            data = {
                'magento_bind_ids': [(0, 0, {
                    'backend_id': binding.backend_id.id,
                    'website_ids': [
                        (4, website_id.id)
                        for website_id in binding.website_ids
                    ],
                    'product_type': binding.product_type,
                    'attribute_set_id': binding.attribute_set_id.id,
                    'visibility': binding.visibility,
                    'tax_class': binding.tax_class,
                    'status': binding.status,
                    'manage_stock': binding.manage_stock,
                    'backorders': binding.backorders
                })]
            }
            self.pool.get('product.product').write(
                cr, uid, active_ids, data, context=context)
