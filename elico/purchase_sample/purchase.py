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


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns = {
        'is_sample': fields.boolean('Is Sample Order'),
    }

    def onchange_is_sample(self, cr, uid, ids, is_sample,
                           company_id, order_line, context=None):
        """
        TODO: domain need company_id?
        """
        print '>>conhange is sample', is_sample
        res = {'value': {}, }
        location_pool = self.pool.get('stock.location')
        if is_sample:
            domain = [('name', 'ilike', 'sample'), ]
        else:
            domain = [('name', 'ilike', 'stock'), ]

        location_ids = location_pool.search(cr, uid, domain)
        location_id = location_ids and location_ids[0] or False
        res['value'].update({'location_id': location_id})

        return res

purchase_order()


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    def onchange_product_id(
            self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False,
            date_planned=False, name=False, price_unit=False,
            is_sample=False, context=None):
        print 'onchange product is_sample', is_sample
        res = super(purchase_order_line, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            context=context)
        if is_sample:
            name = res['value']['name']
            name = name and name + '-SAMPLE' or name
            res['value'].update({'price_unit': 0.0, 'name': name, })

        return res

    def onchange_product_uom(
            self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False,
            date_planned=False, name=False, price_unit=False,
            is_sample=False, context=None):
        """
        onchange handler of product_uom.
        """
        res = super(purchase_order_line, self).onchange_product_uom(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            context=context)
        if is_sample:
            name = res['value']['name']
            name = name and name + '-SAMPLE' or name
            res['value'].update({'price_unit': 0.0, 'name': name, })
        return res

purchase_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
