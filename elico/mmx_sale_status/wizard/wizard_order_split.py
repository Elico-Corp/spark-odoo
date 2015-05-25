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
from openerp.addons.mmx_magento.consumer import delay_export_so
from openerp.addons.connector.session import ConnectorSession


class wizard_order_split_line(osv.osv_memory):
    _name = 'wizard.order.split.line'
    _columns = {
        'name': fields.char('name', size=32),
        'wizard_id': fields.many2one('wizard.order.split', 'Wizard'),
        'sol_id': fields.many2one('sale.order.line', 'SO Lines'),
        'product_id': fields.related('sol_id', 'product_id', type='many2one',
                                     string='Product', readonly=True,
                                     relation='product.product'),
        'product_qty': fields.related('sol_id', 'product_uom_qty',
                                      type='float', string='Quantity',
                                      readonly=True),
        'product_state': fields.related('product_id', 'state', type='char',
                                        string='State', readonly=True),
        'final_qty': fields.float(
            'Final Quantity', digits_compute=dp.get_precision('Product UoS'),),
        'active': fields.boolean('Active'),
    }


class wizard_order_split (osv.osv_memory):
    _name = 'wizard.order.split'

    def _get_lines(self, cr, uid, context=None):
        data = []
        so_id = context.get('active_id', False)
        if so_id:
            order = self.pool.get('sale.order').browse(cr, uid, so_id)
            for sol in order.order_line:
                if sol.product_id.state == 'order':
                    data.append((0, 0, {
                        'sol_id': sol.id,
                        'product_id': sol.product_id.id,
                        'product_qty': sol.product_uom_qty,
                        'product_state': sol.product_id.state,
                        'final_qty': sol.final_qty,
                        'active': False,
                    }))
        return data

    def _get_partner(self, cr, uid, context=None):
        so_id = context.get('active_id', False)
        if so_id:
            return self.pool.get('sale.order').browse(
                cr, uid, so_id).partner_id.id
        return False

    _columns = {
        'name': fields.char('name', size=32),
        'so_id': fields.many2one('sale.order', 'Sale Order'),
        'other_order': fields.many2one('sale.order', 'Other Order'),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'lines': fields.one2many('wizard.order.split.line',
                                 'wizard_id', 'SO Lines'),
        'sale_shipment_id': fields.many2one('sale.shipment', 'Sale Shipment'),
        'active_all': fields.boolean('Active'),
    }
    _defaults = {
        'lines': lambda self, cr, uid, c: self._get_lines(cr, uid, context=c),
        'partner_id': lambda self, cr, uid, c: self._get_partner(cr, uid,
                                                                 context=c),
        'so_id': lambda self, cr, uid, c: c.get('active_id', False),
    }

    def onchange_active_all(self, cr, uid, ids, active_all, lines):
        """
        quickly to change all lines active
        """
        for line in lines:
            line[2]['active'] = active_all
        return {'value': {'lines': lines}}

    def _check_confirm_all(self, wizard):
        """
        if confirm all sol and all quantity,
        not need to create new SO,Directly confirm the SO is OK
        @ return boolean
        """
        solines = wizard.so_id.order_line
        split_lines = wizard.lines
        sol_dic = {}
        split_dic = {}
        [sol_dic.update({x.id: x.product_uom_qty}) for x in solines]
        [split_dic.update({x.sol_id.id: x.final_qty}) for x in split_lines]

        if sol_dic == split_dic and all([x.active for x in split_lines]):
            return True
        else:
            return False

    def split_new_order(self, cr, uid, ids, context=None):
        '''
        Split SO Line that product state is order to a new SO.
        '''
        seq_pool = self.pool.get('ir.sequence')
        so_id = context.get('active_id')
        so_pool = self.pool.get('sale.order')
        sol_pool = self.pool.get('sale.order.line')
        so = so_pool.read(cr, uid, so_id, ['name', 'order_line', 'state'])

        wizard = self.browse(cr, uid, ids[0])
        shipment_id = (wizard.sale_shipment_id
                       and wizard.sale_shipment_id.id or False)
        self._check_split(wizard)

        if self._check_confirm_all(wizard) and so['state'] != 'wishlist':
            for line in sol_pool.read(
                    cr, uid, so['order_line'], ['product_uom_qty']):
                sol_pool.write(
                    cr, uid, line['id'],
                    {'final_qty': line['product_uom_qty']},
                    context=context)
            so_pool.action_button_confirm(cr, 1, [so_id], context=context)
            return True

        new_so_id = None

        session = ConnectorSession(cr, uid, context=context)
        for line in wizard.lines:
            if not line.active:
                continue

            if not line.sol_id.order_id:
                continue
            soline_ids = sol_pool.search(
                cr, uid, [('order_id', '=', line.sol_id.order_id.id),
                          ('product_id', '=', line.product_id.id),
                          ('product_uom_qty', '=', line.product_qty)])
            if not soline_ids:
                continue
            soline_id = soline_ids[0]
            soline = sol_pool.browse(cr, uid, soline_id, context=context)
            final_qty = line.final_qty
            res_qty = soline.product_uom_qty - final_qty

            if res_qty > 0:
                so_pool.write(
                    cr, uid, so_id,
                    {'order_line': [(1, soline.id, {'final_qty': final_qty})]})
                delay_export_so(session, 'sale.order', so_id, ['order_line'])
                so_pool.write(
                    cr, uid, so_id,
                    {'order_line': [(
                        1, soline.id,
                        {'product_uom_qty': res_qty, 'final_qty': 0})]})
            else:
                so_pool.write(
                    cr, uid, so_id,
                    {'order_line': [(1, soline.id, {'final_qty': final_qty})]})
                delay_export_so(session, 'sale.order', so_id, ['order_line'])
                so_pool.write(
                    cr, uid, so_id, {'order_line': [(2, soline.id)]},
                    context=context)
            if not new_so_id:
                new_so_data = so_pool.copy_data(
                    cr, uid, so_id, default={
                        'name': seq_pool.get(cr, uid, 'sale.order'),
                        'origin': so['name'],
                        'order_line': [],
                        'date_order': fields.date.context_today(
                            self, cr, uid, context=context),
                        'sale_shipment_id': shipment_id,
                        'purchase_id': None,
                        'sale_id': None}, context=context)
                if so['state'] != 'wishlist':
                    new_so_id = so_pool.create(
                        cr, uid, new_so_data, context=context)
                else:
                    continue
            sol_data = sol_pool.copy_data(
                cr, uid, soline.id,
                default={'product_uom_qty': final_qty,
                         'final_qty': final_qty,
                         'order_id': new_so_id,
                         'sale_shipment_id': shipment_id})
            if sol_data:
                sol_pool.create(cr, uid, sol_data, context=context)

        domain = [so_id]
        if new_so_id:
            so_pool.write(cr, uid, [new_so_id], {}, context=context)
            context['sale_shipment_id'] = shipment_id or None
            so_pool.action_button_confirm(
                cr, uid, [new_so_id], context=context)
            domain.append(new_so_id)

        return {
            'name': _('Split Sale Order'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', domain)],
            'type': 'ir.actions.act_window',
        }

    def move_order_line(self, cr, uid, ids, context=None):
        '''
         Move SO Line to another SO
        '''
        wizard = self.browse(cr, uid, ids[0])
        sol_pool = self.pool.get('sale.order.line')
        self._check_move(wizard)

        for line in wizard.lines:
            sol_pool.write(cr, uid, line.sol_id.id,
                           {'order_id': wizard.other_order.id})

        return {
            'name': _('Updated Sale Order'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', [wizard.so_id.id, wizard.other_order.id])],
            'type': 'ir.actions.act_window',
        }

    def _check_split(self, wizard):
        """
        check this SO can be split,
            1: include  SOL product state in
                ('draft', 'Draft'),
                ('private', 'Development'),
                ('catalogue', 'Catalogue'),
                ('preorder', 'Announcement'),
        @ wizard,  wizard-myself
        """
        for line in wizard.lines:
            if line.sol_id.product_id.state != 'order':
                raise osv.except_osv(
                    _('Error!'),
                    _('Split Only SOLine Product state is "Order".'))
                return False
            if line.final_qty == 0:
                raise osv.except_osv(
                    _('Error!'),
                    _('Can not confirm Fqty be Zero'))
                return False

        return True

    def _check_move(self, wizard):
        '''
        Check if can be moved to another SO
        '''
        if not wizard.other_order:
            raise osv.except_osv(
                _('Error!'),
                _('You must select a SO when move to other sale order'))
        else:
            if wizard.other_order.state != 'draft':
                raise osv.except_osv(
                    _('Error!'),
                    _('You can move SOL to a not draft order'))
            elif wizard.other_order.partner_id.id != wizard.partner_id.id:
                raise osv.except_osv(
                    _('Error!'),
                    _('Other order partner must same as this Sale order'))
        return True

wizard_order_split()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
