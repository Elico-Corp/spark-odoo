# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Jon Chow <jon.chow@elico-corp.com>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from collections import Counter


class SaleShipment(orm.Model):
    _name = 'sale.shipment'
    _order = 'sequence desc'

    def action_assign_sale_order_lines(self, cr, uid, ids, context=None):
        context = context or None
        model_pool = self.pool['ir.model.data']
        assert len(ids) == 1, 'Should only use for one button;'
        shipment = self.browse(cr, uid, ids[0], context=context)
        product_ids = []
        if shipment.contained_product_info_ids:
            product_ids = [p.product_id.id
                           for p in shipment.contained_product_info_ids]
        context.update({
            'contained_product_ids': product_ids
        })
        dumb, res_id = model_pool.get_object_reference(
            cr, uid, 'sale_shipment', 'view_wizard_shipment_assign_sol')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.shipment.assign.sol',
            'target': 'new',
            'context': context,
            'view_id': res_id
        }

    def _get_seq(self, cr, uid, context=None):
        return self.pool.get('ir.sequence').get(cr, uid, 'sale.shipment')

    def _saleorder_line_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for sol in self.browse(cr, uid, ids, context=context):
            res[sol.id] = len(sol.sol_ids)
        return res

    def _product_line_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for sol in self.browse(cr, uid, ids, context=context):
            res[sol.id] = len(sol.contained_product_info_ids)
        return res

    _columns = {
        'name': fields.text('Name'),
        'sequence': fields.char('Sequence', size=32, select=1),
        'create_date': fields.date('Create Date', readonly=True),
        'saleorder_line_count': fields.function(
            _saleorder_line_count, string='Sale Order Line Count',
            type='integer'),
        'product_line_count': fields.function(
            _product_line_count, string='Product Line Count',
            type='integer'),
        'so_ids': fields.one2many(
            'sale.order',
            'sale_shipment_id',
            'Sale Orders', readonly=True),
        'sol_ids': fields.one2many(
            'sale.order.line',
            'sale_shipment_id',
            'Sale Order Lines', readonly=True),
        'picking_ids': fields.one2many(
            'stock.picking.out',
            'sale_shipment_id',
            'Pickings', readonly=True),
        'stock_move_ids': fields.one2many(
            'stock.move',
            'sale_shipment_id',
            'Stock Moves', readonly=True),
        'state': fields.selection(
            [('draft', 'Draft'),
             ('assigned', ' SOL Assignment'),
             ('confirmed', 'Confirmed'),
             ('done', 'Done')],
            'State'),
        'contained_product_info_ids': fields.one2many(
            'shipment.contained.product.info', 'sale_shipment_id',
            'Contained products', readonly=True,
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly', False)]})
    }
    _defaults = {
        'sequence': _get_seq,
        'state': 'draft'
    }

    def get_shipment_capacity_information(
            self, shipment, product):
        '''Get shipment capacity information:
            - max quantity
            - remaining quantity
           according to the rule defined on the shipment by product.
        @param shipment: browse_record object.
        @param product: browse_record object.
        @param list_of_fields: list.
        @return:
        {'max_qty': value, 'remaining_qty': value, 'assigned_qty': value}'''
        res = {'max_qty': 0.0, 'remaining_qty': 0.0}
        if shipment and shipment.contained_product_info_ids:
            for contained_product in shipment.contained_product_info_ids:
                if product == contained_product.product_id:
                    res.update({
                        'max_qty': contained_product.max_qty,
                        'assigned_qty': contained_product.assigned_qty,
                    })
                    res['remaining_qty'] = res['max_qty'] - res['assigned_qty']
                    break
        return res

    # workflow related functions
    def shipment_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def shipment_assignment(self, cr, uid, ids, context=None):
        return self.write(
            cr,
            uid,
            ids,
            {'state': 'assigned'},
            context=context
        )

    def shipment_confirm(self, cr, uid, ids, context=None):
        '''used in the workflow activity'''
        return self.write(
            cr, uid, ids, {'state': 'confirmed'}, context=context)

    def shipment_close(self, cr, uid, ids, context=None):
        '''used in the workflow activity

        You can only close the shipment without the sol in
        (draft, wishlist).

        This method cannot mass closing the shipments if
        there are exceptions.'''
        if not ids:
            return
        for this in self.browse(cr, uid, ids, context=context):
            if not this.sol_ids:
                continue
            for sol in this.sol_ids:
                if sol.state in ('draft', 'wishlist'):
                    raise orm.except_orm(
                        _('warning'),
                        _('You cannot only close shipment'
                            ' with draft/wishlist sale order line'
                            ' in it!'))
        return self.write(
            cr, uid, ids, {'state': 'done'}, context=context)

    def back2draft(self, cr, uid, ids, context=None):
        '''set back to draft, condition:
            - no sale order line assigned.

            This method cannot be used for massing setting back
        to draft, so this method doesnt raise exception. '''
        if not ids:
            return False
        wf_service = netsvc.LocalService('workflow')
        for this in self.browse(cr, uid, ids, context=context):
            if this.sol_ids:
                raise orm.except_orm(
                    _('warning'),
                    _('You cannot set shipment back to draft'
                        ' if the shipment already has'
                        ' the sale order lines assigned.'))
            wf_service.trg_delete(uid, 'sale.shipment', this.id, cr)
            wf_service.trg_create(uid, 'sale.shipment', this.id, cr)
        return True

    def back2assigned(self, cr, uid, ids, context=None):
        '''set back to assigned, condition:
            - no delivery order line created.

            This method cannot be used for massing setting back
        to draft, so this method doesnt raise exception. '''
        shipment_obj = self.browse(cr, uid, ids, context=context)
        wkf_service = netsvc.LocalService("workflow")
        if not ids:
            return False
        wf_service = netsvc.LocalService('workflow')
        for this in shipment_obj:
            if this.picking_ids:
                raise orm.except_orm(
                    _('warning'),
                    _('You cannot set shipment back to assigned'
                        ' if the delivery order already exists.'))
            wkf_service.trg_validate(
                uid,
                'sale.shipment',
                this.id,
                'signal_shipment_back_to_assigned',
                cr
            )
        return True

class ShipmentContainedProductInfo(orm.Model):
    _name = 'shipment.contained.product.info'

    def _assigned_qty(
            self, cr, uid, ids, field_names, arg=None, context=None):
        '''compute the product quantity already assigned in the shipment'''
        res = {}
        for contain_info in self.browse(
                cr, uid, ids, context=context):

            res[contain_info.id] = 0.0
            if not contain_info.sale_shipment_id:
                continue
            shipment = contain_info.sale_shipment_id

            if shipment.sol_ids:
                for sol in shipment.sol_ids:
                    # TODO you need to move the final_qty from module
                    # (mmx_sale_status) to current module.
                    assert sol.final_qty >= 0, '''Quantity can't'''
                    ''' be negative!'''
                    if contain_info.product_id == sol.product_id:
                        res[contain_info.id] += sol.final_qty
        return res

    def _check_product_id(self, cr, uid, ids, context=None):
        for contained_info in self.browse(
                cr, uid, ids, context=context):
            if not contained_info.sale_shipment_id:
                continue
            shipment = contained_info.sale_shipment_id
            if shipment:
                products = shipment.contained_product_info_ids
                prod_ids = [product.product_id.id for product in products]
                if Counter(prod_ids)[contained_info.product_id.id] > 1:
                    return False
        return True

    _columns = {
        'product_id': fields.many2one(
            'product.product', 'Product'),
        'max_qty': fields.float(
            'Max Quantity',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True),
        'assigned_qty': fields.function(
            _assigned_qty,
            string='Assigned Quantity',
            digits_compute=dp.get_precision('Product Unit of Measure')),
        'sale_shipment_id': fields.many2one(
            'sale.shipment', 'Sale Shipment', required=True),
    }

    _constraints = [
        (
            _check_product_id,
            'Please do not choose a product that already exist',
            ['product_id']
        )
    ]

    def unlink(self, cr, uid, ids, context=None):
        '''cannot be removed when there is already sale order line
        assigned in the shipment'''
        if not ids:
            return False
        for this in self.browse(cr, uid, ids, context=context):
            sol_ids = this.sale_shipment_id.sol_ids
            if not sol_ids:
                continue
            for sol in sol_ids:
                if this.product_id == sol.product_id:
                    raise orm.except_orm(
                        _('Warning'),
                        _('You cannot remove the contained product '
                            'because a related sale order line is '
                            'already assigned.\n Please remove the related'
                            'sale order line first!'))
        return super(ShipmentContainedProductInfo, self).unlink(
            cr, uid, ids, context=context)


class sale_order(orm.Model):
    _inherit = 'sale.order'
    _columns = {
        'sale_shipment_id': fields.many2one(
            'sale.shipment',
            'Shipment',
            ondelete='restrict'),
    }

    def create(self, cr, uid, vals, context=None):
        context = context or {}
        if 'state' in vals:
            context['state'] = vals.get('state')
        return super(sale_order, self).create(cr, uid, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        ''' Don't copy shipment during duplication.'''
        if default is None:
            default = {}
        default.update({'sale_shipment_id': False})
        return super(sale_order, self).copy(
            cr, uid, id, default=default, context=context)

    def _prepare_order_picking(self, cr, uid, order, context=None):
        ''' pass the sale_shipment_id from sale order
        to delivery order model.'''
        res = super(sale_order, self)._prepare_order_picking(
            cr, uid, order, context=context)
        sale_shipment_id = order.sale_shipment_id and \
            order.sale_shipment_id.id or False
        res.update({'sale_shipment_id': sale_shipment_id})
        return res


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def create(self, cr, uid, vals, context=None):
        context = context or {}
        assert vals, 'You need to specify values when creating new order line!'
        if ('state' in context) and ('state' in vals):
            vals['state'] = context['state']
        return super(sale_order_line, self).create(cr, uid, vals, context)

    # alex duan 2014.3.5 <alex.duan@elico-corp.com>
    # super class's state: the selection cannot be function.
    def _get_parent_state_selection(self, cr, uid, context=None):
        _columns = super(sale_order_line, self)._columns
        state_selection = _columns.get('state').selection
        assert not callable(state_selection), _('cannot reuse this method.')
        state_list = state_selection
        state_list.append(('wishlist', 'Wishlist'))
        return state_list

    def _get_sale_order_lines(self, cr, uid, ids, context=None):
        so_pool = self.pool['sale.order']
        res = []
        for so in so_pool.browse(cr, uid, ids, context=context):
            res.extend([line.id for line in so.order_line])
        return res

    def _get_so_state_selection(self, cr, uid, context=None):
        return self.pool['sale.order']._columns.get('state').selection

    _columns = {
        'sale_shipment_id': fields.many2one(
            'sale.shipment', string='Shipment'),
        'state': fields.selection(
            _get_parent_state_selection,
            'State', select=True, readonly=True),

        # TODO, fix the function field, use relation
        # and store and keep the state ==== product_state
        # TODO, copy from module: mmx_sale_status, need to delete the ones.
        'final_qty': fields.float(
            'Final QTY',
            digits_compute=dp.get_precision('Product UoS'),
            readonly=True,
            states={
                'draft': [('readonly', False)],
                'wishlist': [('readonly', False)]}),
        'so_state': fields.related(
            'order_id', 'state', string="SO Status",
            selection=_get_so_state_selection,
            type="selection", store={
                'sale.order': (_get_sale_order_lines, ['state'], 10)
            }),
    }

    def empty_sale_shipment(self, cr, uid, ids, context=None):
        '''remove the sale order line on the sale shipment.
        only allowing draft and wishlist state which doesn't have
        stock pickings created.'''
        if not ids:
            return False
        for this in self.browse(cr, uid, ids, context=context):
            if this.state in ('draft', 'wishlist'):
                # use the write on sale order
                # to be compatible with inter company api
                if this.order_id:
                    this.order_id.write(
                        {'order_line':
                            [(1, this.id, {'sale_shipment_id': False})]},
                        context=context)
                else:
                    this.write({'sale_shipment_id': False}, context=context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        ''' Don't copy shipment during duplication.'''
        if default is None:
            default = {}
        default.update({'sale_shipment_id': False})
        return super(sale_order_line, self).copy(
            cr, uid, id, default=default, context=context)


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def create(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        sale_shipment_id = False

        # get shipment from the related sale order line first.
        sol_id = data.get('sale_line_id')
        if sol_id:
            sol_obj = self.pool['sale.order.line']
            sale_shipment = sol_obj.browse(
                cr, uid,
                sol_id, context=context).sale_shipment_id
            sale_shipment_id = sale_shipment and sale_shipment.id or False
        picking_id = data.get('picking_id')
        # if no shipment on sale order line, get from picking.
        if (not sale_shipment_id) and picking_id:
            picking_obj = self.pool['stock.picking']
            pick = picking_obj.browse(
                cr, uid,
                picking_id, context=context)
            sale_shipment_id = pick.sale_shipment_id and \
                pick.sale_shipment_id.id or False
        data['sale_shipment_id'] = sale_shipment_id
        return super(stock_move, self).create(cr, uid, data, context=context)

    _columns = {
        'sale_shipment_id': fields.many2one(
            'sale.shipment',
            'Shipment',
            ondelete='restrict'),
    }


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'sale_shipment_id': fields.many2one(
            'sale.shipment',
            'Shipment',
            ondelete='restrict'),
    }


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'sale_shipment_id': fields.many2one(
            'sale.shipment',
            'Shipment',
            ondelete='restrict'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        ''' Don't copy the shipment during duplication'''
        if default is None:
            default = {}
        default.update({'sale_shipment_id': False})
        return super(stock_picking_out, self).copy(
            cr, uid, id,
            default, context=context)
