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

from openerp.osv import fields, orm, osv


class sale_shipment(orm.Model):
    _name = 'sale.shipment'
    _order = 'sequence'

    def _get_seq(self, cr, uid, context=None):
        return self.pool.get('ir.sequence').get(cr, uid, 'sale.shipment')

    _columns = {
        'name': fields.char('Name', size=32),
        'sequence': fields.char('Sequence', size=32, select=1),
        'create_date': fields.date('Create Date', readonly=True),
        'so_ids': fields.one2many(
            'sale.order',
            'sale_shipment_id',
            'Sale Orders'),
        'picking_ids': fields.one2many(
            'stock.picking.out',
            'sale_shipment_id',
            'Pickings'),
        'stock_move_ids': fields.one2many(
            'stock.move',
            'sale_shipment_id',
            'Stock Moves')
    }
    _defaults = {
        'sequence': _get_seq,
    }


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
        ''' pass the sale_shipment_id onto delivery order model.'''
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
        if callable(state_selection):
            osv.except_osv('in sale_shipment.py, method:_get_parent_state_selection.\n \
                the problem is you cannot reuse this method.')
        state_list = state_selection
        state_list.append(('wishlist', 'Wishlist'))
        return state_list

    _columns = {
        'sale_shipment_id': fields.many2one(
            'sale.shipment', string='Shipment'),
        'state': fields.selection(
            _get_parent_state_selection,
            'State', select=True, readonly=True)
    }

    # def copy(self, cr, uid, id, default=None, context=None):
    #     ''' Don't copy shipment during duplication.'''
    #     if default is None:
    #         default = {}
    #     default.update({'sale_shipment_id': False})
    #     return super(sale_order_line, self).copy(
    #         cr, uid, id, default=default, context=context)


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
