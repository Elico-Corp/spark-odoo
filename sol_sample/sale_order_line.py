# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Jon.Chow <jon.chow@elico-corp.com>
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
from openerp.osv import osv, fields
from openerp.addons.sale_stock.sale_stock import sale_order as SO


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'is_sample': fields.boolean(
            'Sample ?',
            help='If set to True,This SOL only a sample,not really SOL.'),
    }

sale_order_line()


def new_prepare_order_line_move(self, cr, uid, order, line, picking_id,
                                date_planned, context=None):
    """
    if is a sample,location_is select sample location
    """
    location_id = order.shop_id.warehouse_id.lot_stock_id.id
    output_id = order.shop_id.warehouse_id.lot_output_id.id

    if line.is_sample:
        location_pool = self.pool.get('stock.location')
        sample_locations = location_pool.search(
            cr, uid, [('company_id', '=', line.company_id.id),
                      ('usage', '=', 'internal'),
                      ('name', 'ilike', 'sample')])
        location_id = sample_locations and sample_locations[0] or location_id
    return {
        'name': line.name,
        'picking_id': picking_id,
        'product_id': line.product_id.id,
        'date': date_planned,
        'date_expected': date_planned,
        'product_qty': line.product_uom_qty,
        'product_uom': line.product_uom.id,
        'product_uos_qty': ((line.product_uos
                             and line.product_uos_qty)
                            or line.product_uom_qty),
        'product_uos': ((line.product_uos
                         and line.product_uos.id)
                        or line.product_uom.id),
        'product_packaging': line.product_packaging.id,
        'partner_id': (line.address_allotment_id.id
                       or order.partner_shipping_id.id),
        'location_id': location_id,
        'location_dest_id': output_id,
        'sale_line_id': line.id,
        'tracking_id': False,
        'state': 'draft',
        #'state': 'waiting',
        'company_id': order.company_id.id,
        'price_unit': line.product_id.standard_price or 0.0
    }
SO._prepare_order_line_move = new_prepare_order_line_move

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
