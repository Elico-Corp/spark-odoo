# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
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
import time
from openerp.report import report_sxw


class sale_shipment(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_shipment, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'move_pool': self.pool.get('stock.move'),
            'so_line_pool': self.pool.get('sale.order.line'),
            'get_sum_of_product_qty': self._get_sum_of_product_qty,
            'int': int
        })

    def _get_sum_of_product_qty(self, cr, uid, group_domain):
        '''
            [param]:group_domain: the domain used in the orm method: read_group
            [return]: the sum of qty of product under the criterions
        '''
        so_line_pool = self.pool.get('sale.order.line')
        sum_of_qty = 0.0
        if group_domain:
            line_ids = so_line_pool.search(cr, uid, group_domain)
            if line_ids:
                for d in so_line_pool.read(
                        cr, uid, line_ids, fields=['product_uom_qty']):
                    sum_of_qty += d.get('product_uom_qty', 0.0)
            return sum_of_qty

report_sxw.report_sxw(
    'report.sale_shipment_webkit',
    'sale.shipment',
    'addons/sale_shipment/report/sale_shipment.mako',
    parser=sale_shipment)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
