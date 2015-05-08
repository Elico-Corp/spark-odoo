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
import time
from openerp import netsvc
from openerp.osv import fields, osv
from openerp.addons.mmx_magento.consumer import delay_export
from openerp.addons.connector.session import ConnectorSession
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class wizard_assign_shipment(osv.osv_memory):
    _name = 'wizard.assign.shipment'
    _columns = {
        'name': fields.char('name', size=32),
    }


class wizard_assign_shipment_line(osv.osv_memory):
    _name = 'wizard.assign.shipment.line'
    _columns = {
        'name': fields.char('name', size=32),
        'wizard_id': fields.many2one('wizard.assign.shipment', 'Wizard'),
        'sol_id': fields.many2one('sale.order.line', 'SO Lines'),
        'product_id': fields.related('sol_id', 'product_id', type='many2one',
                                     string='Product', readonly=True,
                                     relation='product.product'),
        'product_qty': fields.related('sol_id', 'product_uom_qty',
                                      type='float', string='Quantity',
                                      readonly=True),
        'so_id': fields.related(
            'sol_id', 'order_id', type='many2one',
            relation='sale.order', string='Sale Order', readonly=True),
        'product_state': fields.related('product_id', 'state', type='char',
                                        string='State', readonly=True),
        'final_qty': fields.float(
            'Final Quantity', digits_compute=dp.get_precision('Product UoS'),),
    }


class wizard_assign_shipment(osv.osv_memory):
    _inherit = 'wizard.assign.shipment'

    def _get_lines(self, cr, uid, context=None):
        sol_pool = self.pool.get('sale.order.line')
        data = []
        active_ids = context.get('active_ids', False)
        if context.get('active_model') == 'sale.order.line':
            for sol in sol_pool.browse(cr, uid, active_ids):
                if sol.product_id.state == 'order':
                    data.append((0, 0, {
                        'product_id': sol.product_id.id,
                        'sol_id': sol.id,
                        'so_id': sol.order_id.id,
                        'product_qty': sol.product_uom_qty,
                        'product_state': sol.product_id.state,
                        'final_qty': sol.final_qty,
                    }))
        return data
    _columns = {
        'date': fields.date('Date', required=True),
        'shipment_id': fields.many2one(
            'sale.shipment', "Shipment", required=True),
        'lines': fields.one2many(
            'wizard.assign.shipment.line', 'wizard_id', 'SO Lines'),
    }
    _defaults = {
        'date': fields.date.context_today,
        'lines': lambda self, cr, uid, c: self._get_lines(cr, uid, context=c),
    }

    def check(self, wizard):
        # ehck final_qty
        return True

    def action(self, cr, uid, ids, context=None):
        sol_pool = self.pool.get('sale.order.line')
        wizard = self.browse(cr, uid, ids[0], context=None)

        if not self.check(wizard):
            return True
        for line in wizard.lines:
            sol_pool.write(cr, uid, line.sol_id.id, {
                'sale_shipment_id': wizard.shipment_id.id,
                'final_qty': line.final_qty,
            })
        return {
            'name': _('Split Sale Order lines'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'sale.order.line',
            'domain': [('id', 'in', [x.sol_id.id for x in wizard.lines])],
            'type': 'ir.actions.act_window',
        }


            
        
        

    

    
    
    