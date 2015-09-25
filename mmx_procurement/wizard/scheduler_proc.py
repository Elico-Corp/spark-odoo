# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Yannick Gouin <yannick.gouin@elico-corp.com>
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
#

from datetime import datetime
from openerp import netsvc, pooler
from openerp.osv import fields, osv
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import (DEFAULT_SERVER_DATETIME_FORMAT)
from openerp.tools.translate import _


class procurement_compute_all(osv.osv_memory):
    _inherit = 'procurement.order.compute.all'
    _name = 'procurement.order.compute.all'

    _columns = {
        'draft_so': fields.boolean(
            'Include "Draft" SO',
            help='Draft Sales Orders are included in the calculation\
            of the stock needed.'),
        'cart_so': fields.boolean(
            'Include "Cart" SO', help='Cart Sales Orders are included\
            in the calculation of the stock needed.'),
        'wishlist_so': fields.boolean(
            'Include "Wishlist" SO', help='Wishlist Sales Orders are included\
            in the calculation of the stock needed.'),
        'reservation_so': fields.boolean(
            'Include "Reservation" SO', help='Reservation Sales Orders are included\
            in the calculation of the stock needed.'),
        'merge_po': fields.boolean(
            'Merge created PO',
            help='Newly created POs will be merged if possible.'),
    }
    _defaults = {
        'automatic': lambda *a: True,
    }

    def _procure_calculation_all(self, cr, uid, ids, context=None):
        """ @param self: The object pointer.
            @param cr: A database cursor
            @param uid: ID of the user currently logged in
            @param ids: List of IDs selected
            @param context: A standard dictionary
        """
        new_cr = pooler.get_db(cr.dbname).cursor()
        (proc, ) = self.browse(new_cr, uid, ids, context=context)
        self.pool.get('procurement.order').run_scheduler(
            new_cr, uid, automatic=proc.automatic,
            use_new_cursor=new_cr.dbname,
            draft_so=proc.draft_so, cart_so=proc.cart_so,
            wishlist_so=proc.wishlist_so, reservation_so=proc.reservation_so,
            merge_po=proc.merge_po,
            context=context)
        new_cr.close()
        return {}

procurement_compute_all()


class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    _name = 'procurement.order'

    def run_scheduler(
            self, cr, uid, automatic=False, use_new_cursor=False,
            draft_so=False, cart_so=False, wishlist_so=False,
            reservation_so=False,
            merge_po=False, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if use_new_cursor:
            use_new_cursor = cr.dbname
        # We delete the previously created PO which are still in draft
        if draft_so or cart_so or wishlist_so or reservation_so:
            po_pool = self.pool.get('purchase.order')
            po_ids = po_pool.search(
                cr, uid,
                [('state', '=', 'draft'),
                 ('origin', 'ilike', '(Including SO)'),
                 ('is_locked', '=', False),
                 ('company_id', '=', user.company_id.id)],
                context=context)
            if po_ids:
                po_pool.unlink(cr, uid, po_ids)
                # Need to commit since later we will probably use a new cursor
                # and this one will be closed
                cr.commit()
        self._procure_confirm(
            cr, uid, use_new_cursor=use_new_cursor, context=context)
        self._procure_orderpoint_confirm(
            cr, uid, automatic=automatic, use_new_cursor=use_new_cursor,
            draft_so=draft_so, cart_so=cart_so, wishlist_so=wishlist_so,
            reservation_so=reservation_so, merge_po=merge_po,
            context=context)

    def _prepare_automatic_op_procurement(
            self, cr, uid, product, warehouse, location_id, context=None):
        context = context or {}
        return {
            'name': _('Automatic OP: %s%s') % (
                context.get('virtual_draft_available', False)
                and '(Including SO) - ' or '', product.name),
            'origin': _('SCHEDULER%s') % (
                context.get('virtual_draft_available', False)
                and ' (Including SO)' or ''),
            'date_planned': datetime.today().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
            'product_id': product.id,
            'product_qty': context.get(
                'virtual_draft_available', product.virtual_available) * -1,
            'product_uom': product.uom_id.id,
            'location_id': location_id,
            'company_id': warehouse.company_id.id,
            'procure_method': 'make_to_order',
        }

    def create_automatic_op(
            self, cr, uid, draft_so=False,
            cart_so=False, wishlist_so=False,
            reservation_so=False, merge_po=False, context=None):
        """ Create procurement of  virtual stock < 0
            @param self: The object pointer
            @param cr: The current row, from the database cursor,
            @param uid: The current user ID for security checks
            @param draft_so: Whether Draft SO quantities are used
            in the calculation or not
            @param cart_so: Whether Cart SO quantities are used
            in the calculation or not
            @param merge_po: Merge PO newly created
            @param context: A standard dictionary for contextual values
            @return:  True
        """
        context = context or {}
        product_obj = self.pool.get('product.product')
        proc_obj = self.pool.get('procurement.order')
        warehouse_obj = self.pool.get('stock.warehouse')
        wf_service = netsvc.LocalService("workflow")
        company_id = self.pool.get(
            'res.users').browse(cr, uid, uid).company_id.id

        warehouse_ids = warehouse_obj.search(
            cr, uid, [('company_id', '=', company_id)], context=context)
        products_ids = product_obj.search(
            cr, uid, [], order='id', context=context)
        processed_pdt = []
        proc_ids = []

        for warehouse in warehouse_obj.browse(
                cr, uid, warehouse_ids, context=context):
            context['warehouse'] = warehouse
            # Here we check products availability.
            # We use the method 'read' for performance reasons, because using
            # the method 'browse' may crash the server.
            for product_read in product_obj.read(
                    cr, uid, products_ids,
                    ['id', 'virtual_available', 'procure_method'],
                    context=context):
                pdt_processing = "%s_%s" % (
                    product_read['id'], warehouse.company_id.id)
                if ((draft_so or cart_so or wishlist_so or reservation_so) and
                        product_read['procure_method'] == 'make_to_stock' and
                        pdt_processing not in processed_pdt):
                    # For MTS product when the option "draft_so" and/or
                    # "cart_so" is True
                    # We'll add to the OP quantity, the Draft/Cart SO
                    # quantities for this product
                    in_states = ['zz']
                    if draft_so:
                        in_states.append('draft')
                    if cart_so:
                        in_states.append('cart')
                    if wishlist_so:
                        in_states.append('wishlist')
                    if reservation_so:
                        in_states.append('reservation')
                    cr.execute("""  SELECT coalesce(
                                    sum(
                                        sol.product_uom_qty *
                                        pu.factor /
                                        pu2.factor)::decimal,
                                        0.0)
                                    as product_qty
                                    FROM sale_order_line sol
                                      LEFT JOIN sale_order so ON
                                          (sol.order_id=so.id)
                                      LEFT JOIN product_product pp ON
                                          (sol.product_id=pp.id)
                                      LEFT JOIN product_template pt ON
                                          (pp.product_tmpl_id=pt.id)
                                      LEFT JOIN product_uom pu ON
                                          (pt.uom_id=pu.id)
                                      LEFT JOIN product_uom pu2 ON
                                          (sol.product_uom=pu2.id)
                                    WHERE so.state IN %s
                                      AND sol.product_id = %s
                                      AND so.company_id = %s""" % (
                               tuple(in_states),
                               product_read['id'],
                               warehouse.company_id.id))

                    draft_so_qty = cr.fetchone()[0] or 0
                    processed_pdt.append(pdt_processing)
                else:
                    draft_so_qty = 0

                virtual_draft_available = product_read[
                    'virtual_available'] - draft_so_qty
                if virtual_draft_available >= 0.0:
                    continue
                product = product_obj.browse(
                    cr, uid, [product_read['id']], context=context)[0]
                if product.supply_method == 'buy':
                    location_id = warehouse.lot_input_id.id
                elif product.supply_method == 'produce':
                    location_id = warehouse.lot_stock_id.id
                else:
                    continue
                if (draft_so or cart_so or wishlist_so or reservation_so) and draft_so_qty:
                    context.update(
                        {'virtual_draft_available': virtual_draft_available})
                else:
                    context.update(
                        {'virtual_draft_available': virtual_draft_available})
                proc_id = proc_obj.create(
                    cr, uid, self._prepare_automatic_op_procurement(
                        cr, uid, product, warehouse, location_id,
                        context=context),
                    context=context)
                if proc_id:
                    proc_ids.append(int(proc_id))
                    wf_service.trg_validate(
                        uid, 'procurement.order', proc_id,
                        'button_confirm', cr)
                    wf_service.trg_validate(
                        uid, 'procurement.order', proc_id,
                        'button_check', cr)
        if proc_ids and merge_po:
            proc_ids.append(0)
            # cr.commit()
            cr.execute(
                """SELECT DISTINCT(purchase_id)
                   FROM procurement_order WHERE id IN
                   %s""", (tuple(proc_ids),))
            po_ids = map(lambda x: x[0], cr.fetchall())
            if po_ids:
                context.update({'del_merged_po': 1})
                self.pool.get('purchase.order').do_merge(
                    cr, uid, po_ids, context=context)

        return True

    def _procure_orderpoint_confirm(
        self, cr, uid, automatic=False, use_new_cursor=False,
        draft_so=False, cart_so=False, wishlist_so=False,
        reservation_so=False, merge_po=False,
            context=None, user_id=False):
        """ Create procurement based on Orderpoint

            @param self: The object pointer
            @param cr: The current row, from the database cursor,
            @param user_id: The current user ID for security checks
            @param context: A standard dictionary for contextual values
            @param use_new_cursor: False or the dbname
            @param automatic: Whether need to create Auto Order Point or not
            @param draft_so: Whether Draft SO qty are used in the calc or not
            @param cart_so: Whether Cart SO qty are used in the calc or not
            @param merge_po: Merge PO newly created
            @return:  Dictionary of values
        """
        if use_new_cursor:
            cr = pooler.get_db(use_new_cursor).cursor()

        context = context or {}
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        procurement_obj = self.pool.get('procurement.order')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")
        offset = 0
        ids = [1]

        procurement_ids = []
        if automatic:
            self.create_automatic_op(
                cr, uid, draft_so=draft_so,
                cart_so=cart_so, wishlist_so=wishlist_so,
                reservation_so=reservation_so, merge_po=merge_po,
                context=context)
            context.update({'del_merged_po': 0})

        while ids:
            ids = orderpoint_obj.search(cr, uid, [], offset=offset, limit=100)
            for op in orderpoint_obj.browse(cr, uid, ids, context=context):
                prods = self._product_virtual_get(cr, uid, op)
                # If automatic, Qty computing already made in
                # create_automatic_op()
                if ((draft_so or cart_so or wishlist_so) and
                    op.product_id.procure_method == 'make_to_stock' and
                        not automatic):
                    # For MTS product when the option "draft_so" and/or
                    # "cart_so" is True
                    # We'll add to the OP quantity, the Draft/Cart SO
                    # quantities for this product
                    in_states = ['zz']
                    if draft_so:
                        in_states.append('draft')
                    if cart_so:
                        in_states.append('cart')
                    if wishlist_so:
                        in_states.append('wishlist')
                    if reservation_so:
                        in_states.append('reservation')
                    cr.execute("""  SELECT
                                    coalesce(
                                        sum(
                                            sol.product_uom_qty *
                                            pu.factor /
                                            pu2.factor)::decimal, 0.0)
                                    as product_qty
                                    FROM sale_order_line sol
                                      LEFT JOIN sale_order so
                                        ON (sol.order_id=so.id)
                                      LEFT JOIN product_product pp
                                        ON (sol.product_id=pp.id)
                                      LEFT JOIN product_template pt
                                        ON (pp.product_tmpl_id=pt.id)
                                      LEFT JOIN product_uom pu
                                        ON (pt.uom_id=pu.id)
                                      LEFT JOIN product_uom pu2
                                        ON (sol.product_uom=pu2.id)
                                    WHERE so.state IN %s
                                      AND sol.product_id = %s
                                      AND so.company_id = %s""" % (
                               tuple(in_states),
                               op.product_id.id,
                               op.company_id.id))

                    draft_so_qty = cr.fetchone()[0] or 0
                    # We compute the SO quantity to OP uom
                    draft_so_qty = uom_obj._compute_qty_obj(
                        cr, uid, op.product_id.uom_id,
                        draft_so_qty, op.product_uom)
                else:
                    draft_so_qty = 0

                if prods is None:
                    continue
                if prods < (op.product_min_qty + draft_so_qty):
                    qty = (max(
                        op.product_min_qty, op.product_max_qty) +
                        draft_so_qty -
                        prods)
                    reste = qty % op.qty_multiple
                    if reste > 0:
                        qty += op.qty_multiple - reste

                    if qty <= 0:
                        continue
                    if op.product_id.type not in ['consu']:
                        if op.procurement_draft_ids:
                            # Check draft procurement related to this order point
                            proc_ids = [
                                x.id for x in op.procurement_draft_ids]
                            procure_datas = procurement_obj.read(
                                cr, uid, proc_ids, ['id', 'product_qty'],
                                context=context)
                            to_generate = qty
                            for proc_data in procure_datas:
                                if to_generate >= proc_data['product_qty']:
                                    wf_service.trg_validate(
                                        uid, 'procurement.order',
                                        proc_data['id'],
                                        'button_confirm', cr)
                                    procurement_obj.write(
                                        cr, uid, [proc_data['id']],
                                        {'origin': op.name}, context=context)
                                    to_generate -= proc_data['product_qty']
                                if not to_generate:
                                    break
                            qty = to_generate

                    if qty:
                        proc_id = procurement_obj.create(
                            cr, uid, self._prepare_orderpoint_procurement(
                                cr, uid, op, qty, context=context),
                            context=context)
                        if proc_id:
                            procurement_ids.append(int(proc_id))
                        wf_service.trg_validate(
                            uid, 'procurement.order', proc_id,
                            'button_confirm', cr)
                        wf_service.trg_validate(
                            uid, 'procurement.order', proc_id,
                            'button_check',   cr)
                        orderpoint_obj.write(
                            cr, uid, [op.id], {'procurement_id': proc_id},
                            context=context)
            offset += len(ids)
            if use_new_cursor:
                cr.commit()

        if procurement_ids and merge_po:
            procurement_ids.append(0)
            cr.commit()
            cr.execute(
                """SELECT DISTINCT(purchase_id)
                   FROM procurement_order
                   WHERE id IN %s""", (tuple(procurement_ids),))
            po_ids = map(lambda x: x[0], cr.fetchall())
            if po_ids:
                context.update({'del_merged_po': 1})
                self.poo.get('purchase.order').do_merge(
                    cr, uid, po_ids, context=context)

        if use_new_cursor:
            cr.commit()
            cr.close()
        return {}

procurement_order()


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _name = 'purchase.order'

    def do_merge(self, cr, uid, ids, context=None):
        """ To merge similar type of purchase orders.
            Orders will only be merged if:
            * Purchase Orders are in draft
            * Purchase Orders belong to the same partner
            * Purchase Orders are have same stock location, same pricelist
            Lines will only be merged if:
            * Order lines are exactly the same except for the quantity and unit

            @param self: The object pointer.
            @param cr: A database cursor
            @param uid: ID of the user currently logged in
            @param ids: the ID or list of IDs
            @param context: A standard dictionary

            @return: new purchase order id
        """
        wf_service = netsvc.LocalService("workflow")

        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if(field in ['product_id',
                             'move_dest_id',
                             'account_analytic_id']):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        # Compute what the new orders should contain
        context = context or {}
        new_orders = {}
        origins = []
        poders = [order for order in
                  self.browse(cr, uid, ids, context=context)
                  if order.state == 'draft']
        for porder in poders:
            order_key = make_key(
                porder, ('partner_id', 'location_id', 'pricelist_id'))
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(porder.id)
            order_infos = new_order[0]
            if not order_infos:
                order_infos.update({
                    'origin':          porder.origin,
                    'date_order':      porder.date_order,
                    'partner_id':      porder.partner_id.id,
                    'dest_address_id': porder.dest_address_id.id,
                    'warehouse_id':    porder.warehouse_id.id,
                    'location_id':     porder.location_id.id,
                    'pricelist_id':    porder.pricelist_id.id,
                    'state':           'draft',
                    'order_line':      {},
                    'notes':           '%s' % (porder.notes or '',),
                    'fiscal_position': (porder.fiscal_position and
                                        porder.fiscal_position.id or False),
                })
                origins.append(porder.origin)
            else:
                if porder.date_order < order_infos['date_order']:
                    order_infos['date_order'] = porder.date_order
                if porder.notes:
                    order_infos['notes'] = (
                        order_infos['notes'] or '') + ('\n%s' % (porder.notes))
                if porder.origin and porder.origin not in origins:
                    order_infos['origin'] = (
                        order_infos['origin'] or '') + ' ' + porder.origin
                    origins.append(porder.origin)

            for order_line in porder.order_line:
                line_key = make_key(
                    order_line, (
                        'name', 'date_planned', 'taxes_id', 'price_unit',
                        'product_id', 'move_dest_id', 'account_analytic_id'))
                o_line = order_infos['order_line'].setdefault(line_key, {})
                if o_line:
                    # merge the line with an existing line
                    o_line['product_qty'] += order_line.product_qty * \
                        order_line.product_uom.factor / o_line['uom_factor']
                else:
                    # append a new "standalone" line
                    for field in ('product_qty', 'product_uom'):
                        field_val = getattr(order_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line[
                        'uom_factor'] = (order_line.product_uom and
                                         order_line.product_uom.factor or
                                         1.0)

        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['order_line'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            order_data['order_line'] = [
                (0, 0, value) for value in
                order_data['order_line'].itervalues()]

            # create the new order
            neworder_id = self.create(cr, uid, order_data)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)

            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                wf_service.trg_redirect(
                    uid, 'purchase.order', old_id, neworder_id, cr)
                wf_service.trg_validate(
                    uid, 'purchase.order', old_id, 'purchase_cancel', cr)

            # Delete the previously canceled POs
            if old_ids and context.get('del_merged_po', False):
                self.unlink(cr, 1, old_ids)
        return orders_info

purchase_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
