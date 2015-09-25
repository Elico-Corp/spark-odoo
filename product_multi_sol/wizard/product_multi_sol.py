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


class wizard_product_multi_sol(osv.osv_memory):
    _name = 'wizard.product.multi.sol'
    _columns = {
        'name': fields.char('name', size=32),
        'so_ids': fields.many2many('sale.order', 'rel_wpms_so', 'wizard_id',
                                   'so_id', 'Sale Orders'),
    }

    def add_to_multi_so(self, cr, uid, ids, context=None):
        pdt_ids = context.get('active_ids', [])
        sol_pool = self.pool.get('sale.order.line')
        pdt_pool = self.pool.get('product.product')

        sale_orders = self.browse(cr, uid, ids[0]).so_ids
        products = pdt_pool.browse(cr, uid, pdt_ids)
        sol_ids = []
        for p in products:
            for so in sale_orders:
                sol_data = {
                    'order_id': so.id,
                    'name': p.name,
                    'product_qty': 0,
                    'product_uom_qty': 0,
                    'product_id': p.id,
                    'price_unit': 0,
                    #'date_planned': date_planned,
                }
                sol_id = sol_pool.create(cr, uid, sol_data)
                sol_ids.append(sol_id)

        return {
            'name': ('New Sale Order Line'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'sale.order.line',
            'domain': [('id', 'in', sol_ids)],
            'type': 'ir.actions.act_window',
        }
wizard_product_multi_sol()






# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
