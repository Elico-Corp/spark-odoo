# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
#    Eric Caudal <eric.caudal@elico-corp.com>

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
from openerp.addons.base_intercompany.backend import icops
from openerp.addons.base_intercompany.unit.export_synchronizer import (
    ICOPSExporter)
from openerp.addons.base_intercompany.unit.mapper import ICOPSExportMapper
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.connector.exception import MappingError
from openerp.addons.base_intercompany.unit.backend_adapter import ICOPSAdapter
from openerp import netsvc


class sale_order(orm.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'icops.model']

    _columns = {
        'openerp_id': fields.many2one('sale.order',
                                      string='Sale Order',
                                      ondelete='cascade'),
        'icops_id': fields.integer(string='ICOPS ID'),
        'icops_model': fields.char(string='ICOPS Model'),
        'icops_bind_ids': fields.one2many(
            'icops.sale.order', 'openerp_id',
            string="ICOPS Bindings"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['icops_bind_ids'] = False
        return super(sale_order, self).copy_data(cr, uid, id,
                                                 default=default,
                                                 context=context)

    def create(self, cr, uid, data, context=None):
        if not context:
            context = {}
        data['icops_bind_ids'] = self.pool.get(
            'icops.backend').prepare_binding(cr, uid, data, context)
        res = super(sale_order, self).create(cr, uid, data, context)
        # Could not find another way to support cascading.
        if context.get('icops'):
            self.write(cr, uid, res, {'order_line': []}, context=context)
        return res

    def write(self, cr, uid, ids, data, context=None):
        if not context:
            context = {}
        self._check_icops(cr, uid, ids, context=context)
        res = super(sale_order, self).write(cr, uid, ids, data, context)
        # Could not find another way to support cascading.
        if context.get('icops') or context.get('connector_no_export'):
            if context.get('written'):
                context['written'] = False
            else:
                context['written'] = True
                self.write(cr, uid, ids, {'order_line': []}, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        self._check_icops(cr, uid, ids, context=context)
        return super(sale_order, self).unlink(cr, uid, ids, context)

    #def action_button_confirm(self, cr, uid, ids, context=None):
    #    for so in self.browse(cr, uid, ids, context=context):
    #        if so.locked:
    #            # do not use the normal way of confirming them
    #            del ids[ids.index(so.id)]
    #            parent = so._get_icops_parent(context=context)
    #            parent.action_button_confirm(context=context)
    #    # do not super if nothing to confirm
    #    if ids:
    #        return super(sale_order, self).action_button_confirm(
    #            cr, uid, ids, context=context)


class icops_sale_order(orm.Model):
    _name = 'icops.sale.order'
    _inherit = 'icops.binding'
    _inherits = {'sale.order': 'openerp_id'}
    _description = 'ICOPS Sale Order'

    _columns = {
        'openerp_id': fields.many2one('sale.order',
                                      string='SaleOrder',
                                      required=True,
                                      ondelete='cascade'),
        'backend_id': fields.many2one('icops.backend',
                                      string='ICOPS Backend'),
        'icops_order_line_ids': fields.one2many('icops.sale.order.line',
                                                'icops_order_id',
                                                'ICOPS Order Lines'),

    }


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    _columns = {
        'icops_bind_ids': fields.one2many(
            'icops.sale.order.line', 'openerp_id',
            string="ICOPS Bindings"),
        'icops_id': fields.integer('ICOPS ID')
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['icops_bind_ids'] = False
        return super(sale_order_line, self).copy_data(cr, uid, id,
                                                      default=default,
                                                      context=context)


class icops_sale_order_line(orm.Model):
    _name = 'icops.sale.order.line'
    _inherit = 'icops.binding'
    _description = 'ICOPS Sale Order Line'
    _inherits = {'sale.order.line': 'openerp_id'}

    def _get_lines_from_order(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('icops.sale.order.line')
        return line_obj.search(cr, uid,
                               [('icops_order_id', 'in', ids)],
                               context=context)
    _columns = {
        'icops_order_id': fields.many2one('icops.sale.order',
                                          'ICOPS Sale Order',
                                          required=True,
                                          ondelete='cascade',
                                          select=True),
        'openerp_id': fields.many2one('sale.order.line',
                                      string='Sale Order Line',
                                      required=True,
                                      ondelete='cascade'),
        'backend_id': fields.related(
            'icops_order_id', 'backend_id',
            type='many2one',
            relation='icops.backend',
            string='ICOPS Backend',
            store={'icops.sale.order.line':
                   (lambda self, cr, uid, ids, c=None: ids,
                    ['icops_order_id'],
                    10),
                   'icops.sale.order':
                   (_get_lines_from_order, ['backend_id'], 20),
                   },
            readonly=True)
    }

    def create(self, cr, uid, vals, context=None):
        icops_order_id = vals['icops_order_id']
        info = self.pool['icops.sale.order'].read(
            cr, uid,
            [icops_order_id],
            ['openerp_id'],
            context=context)
        order_id = info[0]['openerp_id']
        vals['order_id'] = order_id[0]
        return super(icops_sale_order_line, self).create(cr, uid, vals,
                                                         context=context)


@icops
class SaleOrderAdapter(ICOPSAdapter):
    _model_name = 'icops.sale.order'

    def _get_pool(self):
        sess = self.session
        name = ('purchase.order'
                if self._icops.concept == 'so2po' else 'sale.order')
        return sess.pool.get(name)

    def confirm(self, id):
        sess = self.session
        pool = self._get_pool()
        context = sess.context
        context = {'icops': True}
        uid = self._backend_to.icops_uid.id
        obj = pool.browse(sess.cr, uid, id, context=context)
        if obj.state not in ('draft', 'sent') or not obj.order_line:
            return
        if 'backward' in self.session.context:
            context.update({'backward': True})
        if hasattr(pool, 'wkf_confirm_order'):
            pool.wkf_confirm_order(
                sess.cr, uid, [id],
                context=context)
            pool.action_picking_create(
                sess.cr, uid, [id], context=context)
        else:
            pool.action_wait(
                sess.cr, uid, [id],
                context=context)
            pool.action_button_confirm(
                sess.cr, uid, [id],
                context=context)

    def cancel(self, id):
        sess = self.session
        pool = self._get_pool()
        context = sess.context
        context = {'icops': True}
        uid = self._backend_to.icops_uid.id
        obj = pool.browse(sess.cr, uid, id, context=context)
        if obj.state == 'cancel':
            return
        if 'backward' in self.session.context:
            context.update({'backward': True})
        pool.action_cancel(
            sess.cr, self._backend_to.icops_uid.id, [id],
            context=context)


@icops
class SaleOrderExport(ICOPSExporter):
    _model_name = ['icops.sale.order']
    _concepts = ['so2po', 'so2so']

    def _custom_routing(self, id, record, fields=None):
        if 'state' in fields:
            state = record.pop('state')
            if state == 'cancel':
                self._cancel(id)
            elif state in ('approved', 'progress', 'manual'):
                self._confirm(id)
        else:
            self._write(id, record)


@icops
class SaleOrderExportMapper(ICOPSExportMapper):
    _model_name = 'icops.sale.order'

    children = [
        ('order_line', 'order_line', 'icops.sale.order.line')
    ]

    @mapping
    def icops(self, record):
        return {
            'icops_id': record.id,
            'icops_model': record._name,
        }

    def _partner(self, record, is_po=False):
        # do not change partner for backward update
        if self._backward:
            return {}
        res = {}
        sess = self.session
        backend = self._backend_to
        ic_uid = backend.icops_uid.id
        partner_pool = sess.pool.get('res.partner')
        partner_id = record.company_id.partner_id.id
        partner = partner_pool.browse(sess.cr, ic_uid, partner_id)
        pricelist_id = None
        payment_term_id = None
        if is_po:
            pricelist_id = (partner.property_product_pricelist_purchase.id
                            if partner.property_product_pricelist_purchase
                            else False)
            payment_term_id = (partner.property_supplier_payment_term.id
                               if partner.property_supplier_payment_term
                               else False)
            res.update({'payment_term_id': payment_term_id})
        else:
            pricelist_id = (partner.property_product_pricelist.id
                            if partner.property_product_pricelist
                            else False)
            payment_term_id = (partner.property_payment_term.id
                               if partner.property_payment_term
                               else False)
            res.update({'payment_term': payment_term_id})

        fiscal_position_id = (partner.property_account_position.id
                              if partner.property_account_position
                              else False)
        res.update({'partner_id': partner.id,
                    'pricelist_id': pricelist_id,
                    'fiscal_position': fiscal_position_id})
        return res

    @mapping
    def origin(self, record):
        # you don't wanna to write the origin for backward
        if self._backward:
            return {}
        name = record.name
        if record.origin:
            name = '%s:%s' % (record.origin.replace('IC:', ''), name)
        return {'origin': 'IC:%s' % name}

    @mapping
    def map_all(self, record):
        assert self._icops
        return self._get_mapping(self._icops.concept, record)

    def so2so_icops(self, record):
        if self._backward:
            return {}
        if not self._backend_to:
            raise MappingError("Could not find an ICOPS backend")
        backend = self._backend_to
        icops_uid = backend.icops_uid.id
        company = backend.company_id
        partner = company.partner_id
        pricelist = partner.property_product_pricelist
        fiscal_position = partner.property_account_position
        payment_term = partner.property_payment_term
        shop = self._backend_to.icops_shop_id

        return {
            'company_id': company.id,
            'partner_id': partner.id,
            'pricelist_id': pricelist.id,
            'fiscal_position': fiscal_position.id,
            'payment_term': payment_term.id,
            'user_id': icops_uid,
            'shop_id': shop.id
        }

    def so2so_date(self, record):
        return {'date_order': record.date_order}

    def so2so_partner(self, record):
        return self._partner(record)

    def so2so_address(self, record):
        if self._backward:
            return {}
        sess = self.session
        partner = record.company_id.partner_id
        partner_pool = sess.pool.get('res.partner')
        addr = partner_pool.address_get(sess.cr, sess.uid, [partner.id],
                                        ['delivery', 'invoice', 'contact'])
        return {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery']
        }

    def so2so_policy(self, record):
        return {'order_policy': record.order_policy}

    def so2so_state(self, record):
        state = record.state
        #if state in ['reservation', 'wishlist']:
        #    state = 'draft'
        return {'state': state}

    def so2po_partner(self, record):
        return self._partner(record, True)

    def so2po_icops(self, record):
        if self._backward:
            return {}
        if not self._backend_to:
            raise MappingError("Could not find an ICOPS backend")
        backend = self._backend_to
        company = backend.company_id
        shop = backend.icops_shop_id
        warehouse = shop.warehouse_id
        location = warehouse.lot_stock_id

        if company.partner_id.id != record.partner_id.id:
            raise MappingError("Wrong partner")
        return {
            'company_id': company.id,
            'location_id': location.id
        }

    def so2po_state(self, record):
        state = record.state
        if record.state in ('progress', 'manual'):
            state = 'approved'
        if record.state in ['wishlist', 'reservation']:
            state = 'draft'
        return {'state': state}

    def so2so_sale_shipment(self, record):
        res = {}
        if record.sale_shipment_id:
            res['sale_shipment_id'] = record.sale_shipment_id.id
        return res

@icops
class SaleOrderLineExportMapper(ICOPSExportMapper):
    _model_name = 'icops.sale.order.line'

    direct = [('name', 'name')]

    def _price(self, record, is_po=False):
        if not record.product_id:
            return {'price_unit': 0}
        sess = self.session
        backend = self._backend_to
        ic_uid = sess.uid if self._backward else backend.icops_uid.id
        partner_pool = sess.pool.get('res.partner')
        partner_id = record.order_id.company_id.partner_id.id
        partner = partner_pool.browse(sess.cr, ic_uid, partner_id)
        pricelist_id = None
        if is_po:
            pricelist_id = (partner.property_product_pricelist_purchase.id
                            if partner.property_product_pricelist_purchase
                            else False)
        else:
            pricelist_id = (partner.property_product_pricelist.id
                            if partner.property_product_pricelist
                            else False)
        pricelist_pool = sess.pool.get('product.pricelist')
        price_unit = pricelist_pool.price_get(
            sess.cr, ic_uid, [pricelist_id],
            record.product_id.id, record.product_uom_qty)
        price = price_unit[int(pricelist_id)]
        return {'price_unit': price}

    @mapping
    def map_all(self, record):
        assert self._icops
        return self._get_mapping(self._icops.concept, record)

    @mapping
    def icops_id(self, record):
        return {'icops_id': record.id}

    def so2so_price(self, record):
        return self._price(record)

    def so2so_product(self, record):
        return {
            'product_id': record.product_id.id,
            'product_uom': record.product_uom.id,
            'product_uom_qty': record.product_uom_qty,
            'final_qty': record.final_qty
        }

    def so2po_price(self, record):
        return self._price(record, True)

    def so2po_product(self, record):
        return {
            'product_id': record.product_id.id,
            'product_uom': record.product_uom.id,
            'product_qty': record.product_uom_qty
        }

    def so2so_sale_shipment(self, record):
        """
        When split the sol, the old sol should not relate to the shipment_id.
        """
        res = {}
        if record.sale_shipment_id:
            res['sale_shipment_id'] = record.sale_shipment_id.id
        else:
            res['sale_shipment_id'] = False
        return res

    def so2so_comment(self, record):
        res = {}
        if record.comment:
            res['comment'] = record.comment
        return res

    def so2po_date_planned(self, record):
        sess = self.session
        order = record.order_id
        order_pool = sess.pool.get(order._name)
        date_planned = order_pool._get_date_planned(
            sess.cr, sess.uid, order, record, order.date_order)
        return {'date_planned': date_planned}
