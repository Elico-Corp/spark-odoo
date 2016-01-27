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
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class wizard_sol_split_line(osv.osv_memory):
    _name = 'wizard.sol.split.line'
    _columns = {
        'name': fields.char('name', size=32),
        'wizard_id': fields.many2one('wizard.sol.split', 'Wizard'),
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


class wizard_sol_split(osv.osv_memory):
    _name = 'wizard.sol.split'

    def _get_lines(self, cr, uid, context=None):
        sol_pool = self.pool.get('sale.order.line')
        data = []
        sol_ids = context.get('active_ids', False)
        for sol in sol_pool.browse(cr, uid, sol_ids):
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

    def _get_shipment_id(self, cr, uid, context=None):
        sol_pool = self.pool.get('sale.order.line')
        sol_ids = context.get('active_ids', False)
        if sol_ids:
            for sol in sol_pool.browse(cr, uid, sol_ids):
                if sol.sale_shipment_id:
                    return sol.sale_shipment_id.id
        return False

    _columns = {
        'name': fields.char('Name', required=False, size=32),
        'date': fields.date('Date', required=True),
        'shipment_id': fields.many2one('sale.shipment', "Shipment"),
        'lines': fields.one2many(
            'wizard.sol.split.line', 'wizard_id', 'SO Lines'),
        'confirm_orgin': fields.boolean('Confirm Both'),
    }

    _defaults = {
        'date': fields.date.context_today,
        'lines': lambda self, cr, uid, c: self._get_lines(cr, uid, context=c),
        'shipment_id': lambda self, cr, uid, c: self._get_shipment_id(
            cr, uid, context=c)
    }

    def _check_confirm_all(self, so, wizard_lines):
        sol_dic = {}
        split_dic = {}
        [sol_dic.update({x.id: x.product_uom_qty}) for x in so.order_line]
        [split_dic.update({x.sol_id.id: x.final_qty}) for x in wizard_lines]
        if sol_dic == split_dic:
            return True
        else:
            return False

    def _check_split(self, wizard):
        """
        check qty, product,state
        """
        for line in wizard.lines:
            if line.sol_id.product_id.state != 'order':
                raise osv.except_osv(
                    _('Error!'),
                    _('Split Only SOLine Product state is "Order".'))
                return False
            if line.final_qty <= 0:
                raise osv.except_osv(
                    _('Error!'),
                    _('Final quantity cannot be set to 0'))
                return False
        return True

    def split_sol(self, cr, uid, ids, context=None):
        seq_pool = self.pool.get('ir.sequence')
        so_pool = self.pool.get('sale.order')
        sol_pool = self.pool.get('sale.order.line')
        wizard = self.browse(cr, uid, ids[0], context=context)
        shipment_id = wizard.shipment_id and wizard.shipment_id.id or None,

        self._check_split(wizard)

        new_so_ids = []
        new_soline_ids = []
        dic = {}  # {SO1: [wizard_lines in SO1], order_id_2:...}
        for wizard_line in wizard.lines:
            so = wizard_line.so_id
            if dic.get(so, False):
                dic[so].append(wizard_line)
            else:
                dic.update({so: [wizard_line]})

        for so in dic:
            wizard_lines = dic[so]

            # if want to split SOL,qty == whole SO, directly confirm this SO
            if self._check_confirm_all(so, wizard_lines):
                for soline in so.order_line:
                    sol_pool.write(
                        cr, uid, soline.id,
                        {'final_qty': soline.product_uom_qty,
                         'sale_shipment_id': shipment_id},
                        context=context)
                so_pool.action_button_confirm(cr, uid, [so.id],
                                              context=context)
                continue
            # create new SO
            new_so_data = so_pool.copy_data(
                cr, uid, so.id, default={
                    'name': seq_pool.get(cr, uid, 'sale.order'),
                    'origin': so['name'],
                    'order_line': False,
                    'date_order': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'sale_shipment_id': shipment_id,
                    'purchase_id': None,
                    'sale_shipment_id': shipment_id,
                    'sale_id': None}, context=context)
            new_so_id = so_pool.create(cr, uid, new_so_data, context=context)
            new_so_ids.append(new_so_id)
            for wizard_line in wizard_lines:
                soline = wizard_line.sol_id
                final_qty = wizard_line.final_qty
                res_qty = soline.product_uom_qty - final_qty
                sol_data = sol_pool.copy_data(
                    cr, uid, soline.id,
                    default={'product_uom_qty': final_qty,
                             'final_qty': final_qty,
                             'order_id': new_so_id}, context=context)
                # do not use sol_pool.write
                if res_qty > 0:
                    so_pool.write(
                        cr, uid, so.id,
                        {
                            'order_line':
                                [(1, soline.id,
                                    {
                                        'product_uom_qty': res_qty,
                                        'final_qty': 0
                                    })]},
                            context=context
                    )
                elif res_qty == 0.0:
                    so_pool.write(
                        cr, uid, so.id, {'order_line': [(2, soline.id)]},
                        context=context)
                else:
                    pass
                sol_id = sol_pool.create(cr, uid, sol_data, context=context)
                new_soline_ids.append(sol_id)

                # TODO if Confirm Origin
                # If only reserve one SOL, confirm this SO.
                # else split A another new SO, and

        # confirm new SO
        for so_id in new_so_ids:
            context['sale_shipment_id'] = shipment_id
            so_pool.action_button_confirm(cr, uid, [so_id], context=context)

        # return old + new SOL
        old_soline_ids = [x.sol_id.id for x in wizard.lines]
        return {
            'name': _('Split Sale Order lines'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'sale.order.line',
            'domain': [('id', 'in', new_soline_ids + old_soline_ids)],
            'type': 'ir.actions.act_window',
        }
