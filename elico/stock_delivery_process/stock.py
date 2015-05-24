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
from openerp.osv import orm, fields
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'on_hold': fields.boolean(
            'On Hold', write=["stock_delivery_process.on_hold_group"]),
        'on_hold_modify_id': fields.many2one(
            'res.users', 'On Hold Last modified by', readonly=True),
        'on_hold_modify_date': fields.datetime(
            "Time of updating On Hold", readonly=True),

        'qc_approved': fields.boolean(
            'QC Approved', write=["stock_delivery_process.qc_approve_group"]),
        'qc_approve_modify_id': fields.many2one(
            'res.users', 'QC Approved Last modified by', readonly=True),
        'qc_approve_modify_date': fields.datetime(
            "Time of updating QC Approved", readonly=True),
    }

    _defaults = {
        'on_hold': False,
        'qc_approved': False
    }

    def _check_if_process(self, picking):
        '''before process the order, check the on_hold and qc_approved'''
        if picking.on_hold:
            raise orm.except_orm(
                _('Warning'),
                _('This delivery order is on hold!'))
        if not picking.qc_approved:
            raise orm.except_orm(
                _('Warning'),
                _('This delivery order have been QC Approved!'))

    # check before confirm & delivery
    def draft_validate(self, cr, uid, ids, context=None):
        """ Validates picking directly from draft state.
        @return: True
        """
        if not ids:
            return False
        for picking in self.browse(cr, uid, ids, context=context):
            self._check_if_process(picking)
        return super(stock_picking, self).draft_validate(
            cr, uid, ids, context=context)

    # check before delivery the order
    def action_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return False
        for picking in self.browse(cr, uid, ids, context=context):
            self._check_if_process(picking)
        return super(stock_picking, self).action_process(
            cr, uid, ids, context=context)


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'on_hold': fields.boolean(
            'On Hold', write=["stock_delivery_process.on_hold_group"]),
        'on_hold_modify_id': fields.many2one(
            'res.users', 'On Hold Last modified by', readonly=True),
        'on_hold_modify_date': fields.datetime(
            "Time of updating On Hold", readonly=True),

        'qc_approved': fields.boolean(
            'QC Approved', write=["stock_delivery_process.qc_approve_group"]),
        'qc_approve_modify_id': fields.many2one(
            'res.users', 'QC Approved Last modified by', readonly=True),
        'qc_approve_modify_date': fields.datetime(
            "Time of updating QC Approved", readonly=True),
    }

    def write(self, cr, uid, ids, vals, context=None):
        '''when we change the on_hold or qc_approved, we `force` change the
        related stock moves, responsible user and modify date as well.'''
        if not ids:
            return False
        context = context or {}
        move_pool = self.pool['stock.move']
        pickings = self.browse(cr, uid, ids, context=context)
        now = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        def _update_field(
                cr, uid, vals,
                field_name, res_user_field_name, date_field_name):
            '''
            - update the field in the related stock moves
            - update the responsible user and date'''
            ctx = context.copy().update({'from_picking_modification': True})
            if field_name in vals:
                # update the on_hold on stock picking
                for picking in pickings:
                    move_ids = [m.id for m in picking.move_lines]
                    if move_ids:
                        # update the on_hold picking by picking
                        move_pool.write(
                            cr, uid, move_ids,
                            {field_name: vals[field_name]}, context=ctx)
            # update the responsible user and modify date.
            vals.update(
                {res_user_field_name: uid,
                 date_field_name: now})
        # the modification is from move level.
        if 'from_move_modification' in context:
            del context['from_move_modification']
            return super(stock_picking_out, self).write(
                cr, uid, ids, vals=vals, context=context)
        # the modification is from picking itself.
        else:
            _update_field(
                cr, uid, vals,
                'on_hold', 'on_hold_modify_id', 'on_hold_modify_date')
            _update_field(
                cr, uid, vals,
                'qc_approved', 'qc_approve_modify_id',
                'qc_approve_modify_date')
            return super(stock_picking_out, self).write(
                cr, uid, ids, vals=vals, context=context)

    _defaults = {
        'on_hold': False,
        'qc_approved': False
    }


class stock_move(orm.Model):
    _inherit = 'stock.move'
    _columns = {
        'on_hold': fields.boolean(
            'On Hold', write=["stock_delivery_process.on_hold_group"]),
        'qc_approved': fields.boolean(
            'QC Approved', write=["stock_delivery_process.qc_approve_group"]),
    }

    def _check_if_process(self, move):
        '''before process the stock moves, check the on_hold and qc_approved'''
        if not move.picking_id:
            if move.on_hold:
                raise orm.except_orm(
                    _('Warning'),
                    _('This stock move is on hold!'))
            if not move.qc_approved:
                raise orm.except_orm(
                    _('Warning'),
                    _('This stock move have not been QC Approved!'))
        else:
            picking = move.picking_id
            if picking.on_hold:
                raise orm.except_orm(
                    _('Warning'),
                    _('The delivery order is on hold!'))
            if not picking.qc_approved:
                raise orm.except_orm(
                    _('Warning'),
                    _('The delivery order have been QC Approved!'))

    # check before user clicks the button 'process entirely'
    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.

        check before confirm the stock move entirely.
        """
        for move in self.browse(cr, uid, ids, context=context):
            self._check_if_process(move)
        return super(stock_move, self).action_done(
            cr, uid, ids, context=context)

    _defaults = {
        'on_hold': False,
        'qc_approved': False
    }

    def write(self, cr, uid, ids, vals, context=None):
        '''when modify the two fields: on_hold and qc_approved on stock move,
        For on_hold:
            - if one of the stock moves is True, then the related
                picking should be True as well, the related picking
                can only be False when all its moves are all False.
        For qc_approved:
            - if one of the stock moves is False, then the related
                picking should be False as well, the related picking
                can only be True when all its moves are all True.'''
        if not ids:
            return False
        context = context or {}
        if ('on_hold' not in vals) and ('qc_approved' not in vals):
            return super(stock_move, self).write(
                cr, uid, ids, vals, context=context)
        # if the modification is from picking, force change the state.
        if 'from_picking_modification' in context:
            # remove the context.
            del context['from_picking_modification']
            return super(stock_move, self).write(
                cr, uid, ids, vals, context=context)
        # if the modification is from move level, influencing the related
        # picking back.
        else:
            ctx = context.copy().update({'from_move_modification': True})
            now = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            for move in self.browse(cr, uid, ids, context=context):
                picking = move.picking_id
                if picking:
                    if 'on_hold' in vals:
                        # on_hold rules
                        on_hold_list = [
                            m.on_hold for m in picking.move_lines if m != move]
                        on_hold_list.append(vals['on_hold'])
                        # if at least one of them is True and on_hold on
                        # picking is False, then set the picking as True
                        if any(on_hold_list) and (not picking.on_hold):
                            picking.write(
                                {'on_hold': True,
                                 'on_hold_modify_id': uid,
                                 'on_hold_modify_date': now}, context=ctx)
                        # if on_hold on all moves are False and on_hold on
                        # picking is True, then set the picking as False.
                        elif not any(on_hold_list) and (picking.on_hold):
                            picking.write(
                                {'on_hold': False,
                                 'on_hold_modify_id': uid,
                                 'on_hold_modify_date': now}, context=ctx)

                    if 'qc_approved' in vals:
                        # QC approved rules
                        qc_approved_list = [
                            m.qc_approved for m in picking.move_lines
                            if m != move]
                        qc_approved_list.append(vals['qc_approved'])
                        # if at least one of them is False and qc_approved on
                        # picking is True, then set the picking as False
                        if not all(qc_approved_list) and (picking.qc_approved):
                            picking.write(
                                {'qc_approved': False,
                                 'qc_approve_modify_id': uid,
                                 'qc_approve_modify_date': now}, context=ctx)
                        # if qc_approved on all moves are True and
                        # qc_approve on picking is False, then set the picking
                        # as True
                        elif all(qc_approved_list) and not picking.qc_approved:
                            picking.write(
                                {'qc_approved': True,
                                 'qc_approve_modify_id': uid,
                                 'qc_approve_modify_date': now}, context=ctx)
            return super(stock_move, self).write(
                cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        ''' get the value of on_hold and qc_approved when creating
        the stock move from related picking.'''
        if vals.get('picking_id'):
            picking_pool = self.pool['stock.picking']
            picking = picking_pool.browse(
                cr, uid, vals['picking_id'], context=context)
            vals.update({
                'on_hold': picking.on_hold,
                'qc_approved': picking.qc_approved
            })
        return super(stock_move, self).create(
            cr, uid, vals, context=context)


class stock_partial_move(orm.TransientModel):
    _inherit = "stock.partial.move"

    # check before user clicks the button 'process partially'
    def do_partial(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Partial move processing '
        'may only be done one form at a time.'
        partial = self.browse(cr, uid, ids[0], context=context)
        move_pool = self.pool['stock.move']
        for move in partial.move_ids:
            move_pool._check_if_process(move)
        return super(stock_partial_move, self).do_partial(
            cr, uid, ids, context=context)
