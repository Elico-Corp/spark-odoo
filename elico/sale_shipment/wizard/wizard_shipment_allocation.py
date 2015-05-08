# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
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
from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class WizardShipmentAllocationLine(orm.TransientModel):
    _name = 'wizard.shipment.allocation.line'

    def _get_quantities(
            self, cr, uid, ids, field_names, arg=None, context=None):
        ''' used for function fields getting the quantities
                - remaining quantity
                - max quantity
            to display on the shipment allocation wizard for information.'''
        res = {}
        shipment_pool = self.pool['sale.shipment']
        for wizard in self.browse(cr, uid, ids, context=context):
            res[wizard.id] = {'remaining_qty': 0.0, 'max_qty': 0.0}
            shipment = wizard.wizard_id.shipment_id
            if not shipment:
                continue
            res[wizard.id].update(
                shipment_pool.get_shipment_capacity_information(
                    shipment, wizard.product_id))
        return res

    _columns = {
        # Notes: for transient model, related field might not make sense,
        # because for 7, the function/related field is computed when u
        # save this record.
        'name': fields.char('name', size=32),
        'wizard_id': fields.many2one('wizard.shipment.allocation', 'Wizard'),
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
                                        string='Product State', readonly=True),
        'state': fields.related('sol_id', 'state', type='char',
                                string='State', readonly=True),
        'final_qty': fields.float(
            'Final Quantity', digits_compute=dp.get_precision('Product UoM'),),
        'remaining_qty': fields.function(
            _get_quantities,
            string='Remaining qty', type='float', multi="QTY",
            digits_compute=dp.get_precision('Product Unit of Measure')),
        'max_qty': fields.function(
            _get_quantities,
            string='Max qty in shipment', type='float', multi="QTY",
            digits_compute=dp.get_precision('Product Unit of Measure'),),
        'assigned_qty': fields.function(
            _get_quantities,
            string='Assigned qty', type='float', multi="QTY",
            digits_compute=dp.get_precision('Product Unit of Measure'),),
        'partner_id': fields.related(
            'sol_id', 'order_partner_id', type="many2one",
            string="Customer", readonly=True, relation="res.partner")
    }


class WizardShipmentAllocation(orm.TransientModel):
    _name = 'wizard.shipment.allocation'

    def _fore_check_lines_valid(self, wizard):
        '''Check if the lines in the wizard is valid or not:
            - final qty is smaller then the quantity on sol
            - sum of the final qty of one product is smaller than max qty
           This method might Raises Exceptions.

        @param wizard: the browse_record object of the wizard
        @return: True or False'''
        if not wizard or (not wizard.lines):
            return True
        for line in wizard.lines:
            if line.final_qty > line.product_qty or \
                    line.final_qty < 0:
                raise orm.except_orm(
                    _('Warning'),
                    _('Please check product: %s, '
                        'Final qty is current larger '
                        'than the quantity in sale order '
                        'line.\n Or final qty is negative.'
                        '' % (line.product_id.name)))
            # check if the remaining quantity is negative.
            import pdb
            pdb.set_trace()
        return True

    def confirm_final_qty(self, cr, uid, ids, context=None):
        '''This method is used update the final qty on sale order line.'''
        if not ids:
            return False
        for wizard in self.browse(cr, uid, ids, context=context):
            # check before confirm
            if not self._fore_check_lines_valid(wizard):
                return False
            if wizard.lines:
                for l in wizard.lines:
                    l.sol_id.write({'final_qty': l.final_qty}, context=context)
        return True

    def update_remaining_qty(
            self, cr, uid, ids, context=None):
        '''Update the remaining qty in the wizard'''
        if not ids:
            return False
        action_pool = self.pool['ir.actions.act_window']
        model_pool = self.pool['ir.model.data']
        wizard = self.browse(cr, uid, ids, context=context)[0]
        # update the final qty of sale order lines on the wizard.
        wizard.confirm_final_qty()

        # get the action to return
        # the module name is not flexible
        # if we wanna change the module name, then we have to change here.
        dumb, action_id = model_pool.get_object_reference(
            cr, uid, 'sale_shipment',
            'action_shipment_allocation_wizard_qty_assign')
        action = action_pool.read(
            cr, uid, [action_id], context=context)[0]
        action['res_id'] = wizard.id
        return action

    def _get_lines(self, cr, uid, context=None):
        shipment_pool = self.pool.get('sale.shipment')
        data = []
        shipment_ids = context.get('active_ids', False)
        if len(shipment_ids) > 1 or (not shipment_ids):
            raise orm.except_orm(
                _('Warning'),
                _('You should do shipment by shipment.'))
        shipment = shipment_pool.browse(
            cr, uid, shipment_ids, context=context)[0]
        if not shipment.sol_ids:
            return data
        for sol in shipment.sol_ids:
            if sol.product_id.state == 'order' and \
                    sol.state in ('draft', 'wishlist'):
                line_vals = {
                    'product_id': sol.product_id.id,
                    'partner_id': sol.order_partner_id.id,
                    'sol_id': sol.id,
                    'so_id': sol.order_id.id,
                    'product_qty': sol.product_uom_qty,
                    'product_state': sol.product_id.state,
                    'final_qty': sol.final_qty,
                    'state': sol.state
                }

                # get max_qty and remaininng_qty
                # function doesn't auto compute the value
                line_vals.update(
                    shipment_pool.get_shipment_capacity_information(
                        shipment, sol.product_id))
                data.append((0, 0, line_vals))
        return data

    def _get_shipment_id(self, cr, uid, context=None):
        return context.get('active_id', False)

    _columns = {
        'name': fields.char('Name', required=False, size=32),
        'date': fields.date('Date', required=True),
        'shipment_id': fields.many2one(
            'sale.shipment', "Shipment", readonly=True),
        'lines': fields.one2many(
            'wizard.shipment.allocation.line', 'wizard_id', 'SO Lines',
            domain=[('state', 'in', ('draft', 'wishlist'))]),
    }

    _defaults = {
        'date': fields.date.context_today,
        'lines': _get_lines,
        'shipment_id': _get_shipment_id,
    }

    def _check_confirm_all(self, so, wizard_lines):
        '''TODO'''
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
        check the product qty, product, state '
        'before confirm the sale order line.
        """
        for line in wizard.lines:
            if not line.sol_id:
                raise orm.except_orm(
                    _('Error!'),
                    _('Must have one sale order line .'
                        'corresponding to the wizard line'))
            if line.sol_id.product_id.state != 'order':
                raise orm.except_orm(
                    _('Error!'),
                    _('Split Only SOLine Product state is "Order".'))
            if line.final_qty <= 0:
                raise orm.except_orm(
                    _('Error!'),
                    _('Can not confirm if Fianl qty <= 0'))
            if line.final_qty > line.sol_id.product_uom_qty:
                raise orm.except_orm(
                    _('Error!'),
                    _('Can not confirm Fqty > SOL.qty'))
        return True

    def split_sol(self, cr, uid, ids, context=None):
        seq_pool = self.pool['ir.sequence']
        so_pool = self.pool.get('sale.order')
        sol_pool = self.pool.get('sale.order.line')
        wizard = self.browse(cr, uid, ids[0], context=context)
        shipment_id = wizard.shipment_id and wizard.shipment_id.id or None,

        self._check_split(wizard)

        new_so_ids = []
        new_soline_ids = []
        dic = {}
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
                so_pool.action_button_confirm(
                    cr, uid, [so.id], context=context)
                continue
            # create new SO
            new_so_data = so_pool.copy_data(
                cr, uid, so.id, default={
                    'name': seq_pool.get(cr, uid, 'sale.order'),
                    'origin': so['name'],
                    'order_line': False,
                    'date_order': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'sale_shipment_id': False,
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
                             'order_id': new_so_id,
                             'sale_shipment_id': False,
                             'ic_pol_id': None,
                             'ic_sol_id': None}, context=context)
                # do not use sol_pool.write
                if res_qty > 0:
                    so_pool.write(
                        cr, uid, so.id,
                        {'order_line':
                            [(1, soline.id, {
                                'product_uom_qty': res_qty, 'final_qty': 0})]}
                    )
                elif res_qty == 0.0:
                    so_pool.write(
                        cr, uid, so.id, {'order_line': [(2, soline.id)]},
                        context=context)
                else:
                    pass
                sol_id = sol_pool.create(cr, uid, sol_data, context=context)
                new_soline_ids.append(sol_id)

                # TODO if Confirm Orgin
                # If only reserve one SOL, comfirm this SO.
                # else split A another new SO, and

        # confirm new SO
        for so_id in new_so_ids:
            context['sale_shipment_id'] = shipment_id
            so_pool.action_button_confirm(cr, uid, [so_id], context=context)

        # return old+new SOL
        old_soline_ids = [x.sol_id.id for x in wizard.lines]
        return {
            'name': _('Split Sale Order lines'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'sale.order.line',
            'domain': [('id', 'in', new_soline_ids + old_soline_ids)],
            'type': 'ir.actions.act_window',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
