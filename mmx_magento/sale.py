# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaaas@elico-corp.com>
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
import logging
from openerp.osv import fields, orm, osv
import openerp.addons.decimal_precision as dp
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ExportMapper)
from openerp.addons.magentoerpconnect.sale import SaleOrderImportMapper
from .backend import magento_sparkmodel
from openerp.addons.connector_ecommerce.unit.sale_order_onchange import (
    SaleOrderOnChange)
from openerp.addons.magentoerpconnect.unit.backend_adapter import (
    GenericAdapter)
from openerp.addons.magentoerpconnect.unit.import_synchronizer import (
    DelayedBatchImport,
    MagentoImportSynchronizer)
from openerp.addons.magentoerpconnect.sale import (SaleOrderLineImportMapper)
from openerp.addons.connector.queue.job import job

from openerp.addons.magentoerpconnect.unit.delete_synchronizer import (
    MagentoDeleteSynchronizer)
from openerp.addons.magentoerpconnect.unit.export_synchronizer import (
    MagentoExporter)
from openerp.addons.connector.exception import MappingError
from openerp.addons.magentoerpconnect.connector import get_environment
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


class sale_order(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('invoice_except', 'Invoice Exception'),
            ('shipping_except', 'Shipping Exception'),
            ('done', 'Done'),
            ('cart', 'Cart'),
            ('wishlist', 'Wishlist'),
            ('reservation', 'Reservation')
        ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \n\
                  The exception status is automatically set when a cancel\
                  operation occurs the processing of a document linked to\
                  the sales order. \n The 'Waiting Schedule' status is set\
                  when the invoice is confirmed but waiting for the scheduler\
                  to run on the order date.", select=True),
        'magento_cart_bind_ids': fields.one2many('magento.sale.cart',
                                                 'openerp_id',
                                                 string="Magento Bindings"),
        'magento_wishlist_bind_ids': fields.one2many(
            'magento.sale.wishlist', 'openerp_id', string="Magento Bindings"),
        'order_line': fields.one2many(
            'sale.order.line',
            'order_id',
            'Order Lines',
            readonly=True,
            states={
                'draft': [('readonly', False)],
                'sent': [('readonly', False)],
                'cart': [('readonly', False)],
                'wishlist': [('readonly', False)],
                'reservation': [('readonly', False)]
            }),
    }

    def update_reservation_name(self, cr, uid, ids, context=None):
        # sort bad ids
        so_ids = self.search(
            cr, uid, [('id', 'in', ids), ('state', '=', 'reservation')],
            context=context)
        seq_pool = self.pool['ir.sequence']
        # switch to the official SO name sequence for confirmed Reservation
        for so in self.browse(cr, uid, so_ids, context=context):
            name = seq_pool.get(cr, uid, 'sale.order')
            so.write({'name': name, 'magento_bind_ids': [(5,)]},
                     context=context)

    def action_button_confirm(self, cr, uid, ids, context=None):
        self.update_reservation_name(cr, uid, ids, context)
        return super(sale_order, self).action_button_confirm(
            cr, uid, ids, context=context)

    def action_wait(self, cr, uid, ids, context=None):
        self.update_reservation_name(cr, uid, ids, context)
        return super(sale_order, self).action_wait(
            cr, uid, ids, context=context)


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    _columns = {
        'magento_cart_bind_ids': fields.one2many('magento.sale.cart.line',
                                                 'openerp_id',
                                                 string="Magento Bindings"),
        'magento_wishlist_bind_ids': fields.one2many(
            'magento.sale.wishlist.line',
            'openerp_id',
            string="Magento Bindings"),
    }

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, int):
            ids = [ids]
        """Allows to delete sales order lines in draft,cancel states"""
        black_listed = [
            'cart', 'draft', 'wishlist', 'reservation', 'cancel'
        ]
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in black_listed:
                raise osv.except_osv(_('Invalid Action!'),
                                     _('Cannot delete a sales order line which\
                                       is in state \'%s\'.') % (rec.state))
        return super(sale_order_line, self).unlink(cr,
                                                   uid,
                                                   ids,
                                                   context=context)


@magento_sparkmodel
class MagentoSaleCartOnChange(SaleOrderOnChange):
    _model_name = 'magento.sale.cart'

    def play(self, order, order_lines):
        """ Play the onchange of the sale order and it's lines

        :param order: data of the sale order
        :type: dict

        :return: the value of the sale order updated with the onchange result
        :rtype: dict
        """
        sess = self.session
        #  play onchange on sale order
        order = self._play_order_onchange(order)
        #  play onchange on sale order line
        processed_order_lines = []
        line_lists = [order_lines]

        # TODO CHANGE THAT PART
        cart_pool = sess.pool.get('magento.sale.cart')
        search = [('backend_id', '=', self.backend_record.id),
                  ('magento_cart_id', '=', order['magento_cart_id'])]
        cart_ids = cart_pool.search(sess.cr, sess.uid, search)
        sale_order_line_pool = sess.pool.get('sale.order.line')
        if cart_ids:
            cart = cart_pool.browse(sess.cr, sess.uid, cart_ids[0])
            for l in cart.openerp_id.order_line:
                sale_order_line_pool.unlink(sess.cr, sess.uid, [l.id])
        # ######################

        if 'order_line' in order and order['order_line'] is not order_lines:
            # we have both backend-dependent and oerp-native order
            # lines.
            # oerp-native lines can have been added to map
            # shipping fees with an OpenERP Product
            line_lists.append(order['order_line'])
        for line_list in line_lists:
            for idx, line in enumerate(line_list):
                # line_list format:[(0, 0, {...}), (0, 0, {...})]
                old_line_data = line[2]
                new_line_data = self._play_line_onchange(old_line_data,
                                                         processed_order_lines,
                                                         order)

                new_line = (0, 0, new_line_data)
                processed_order_lines.append(new_line)
                # in place modification of the sale order line in the list
                line_list[idx] = new_line
        return order


class magento_sale_cart(orm.Model):
    _name = 'magento.sale.cart'
    _inherit = 'magento.binding'
    _inherits = {'sale.order': 'openerp_id'}

    _columns = {
        'openerp_id': fields.many2one('sale.order',
                                      string='Magento order',
                                      required=True,
                                      ondelete='cascade'),
        'magento_cart_line_ids': fields.one2many('magento.sale.cart.line',
                                                 'magento_cart_id',
                                                 'Magento Cart Lines'),
        'total_amount': fields.float(
            'Total amount',
            digits_compute=dp.get_precision('Account')),
        'total_amount_tax': fields.float(
            'Total amount w. tax',
            digits_compute=dp.get_precision('Account')),
        'magento_cart_id': fields.integer(
            'Magento Cart ID',
            help="Cart identifier field in Magento"),
        # when a sale order is modified, Magento creates a new one, cancels
        # the parent order and link the new one to the canceled parent
        'magento_parent_id': fields.many2one('magento.sale.order',
                                             string='Parent Magento Order'),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A partner tag with same ID on Magento already exists.'),
    ]


class magento_sale_cart_line(orm.Model):
    _name = 'magento.sale.cart.line'
    _inherit = 'magento.binding'
    _inherits = {'sale.order.line': 'openerp_id'}

    def _get_lines_from_order(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('magento.sale.cart.line')
        return line_obj.search(cr, uid,
                               [('magento_cart_id', 'in', ids)],
                               context=context)
    _columns = {
        'magento_cart_id': fields.many2one(
            'magento.sale.cart',
            'Magento Sale Order',
            required=True,
            ondelete='cascade',
            select=True),
        'openerp_id': fields.many2one('sale.order.line',
                                      string='Sale Order Line',
                                      required=True,
                                      ondelete='cascade'),
        'backend_id': fields.related(
            'magento_cart_id', 'backend_id',
            type='many2one',
            relation='magento.backend',
            string='Magento Backend',
            store={
                'magento.sale.cart.line':
                (lambda self, cr, uid, ids, c=None: ids,
                    ['magento_cart_id'], 10),
                'magento.sale.cart':
                (_get_lines_from_order, ['backend_id'], 20)
            },
            readonly=True),
        'tax_rate': fields.float('Tax Rate',
                                 digits_compute=dp.get_precision('Account')),
        'notes': fields.char('Notes'),  # XXX common to all ecom sale orders

    }

    def create(self, cr, uid, vals, context=None):
        magento_cart_id = vals['magento_cart_id']
        info = self.pool['magento.sale.cart'].read(
            cr,
            uid,
            [magento_cart_id],
            ['openerp_id'],
            context=context)
        order_id = info[0]['openerp_id']
        vals['order_id'] = order_id[0]
        return super(magento_sale_cart_line, self).create(
            cr,
            uid,
            vals,
            context=context)


@magento_sparkmodel
class CartBatchImport(DelayedBatchImport):
    """ Delay import of the records """
    _model_name = ['magento.sale.cart']

    def run(self, filters=None):
        """ Run the synchronization """
        if filters is None:
            filters = {}
        magento_store_ids = filters.pop('magento_store_ids')
        record_ids = self.backend_adapter.search(filters,
                                                 magento_store_ids)
        _logger.info('search for magento saleorders %s  returned %s',
                     filters, record_ids)
        for record_id in record_ids:
            self._import_record(record_id)


@magento_sparkmodel
class CartAdapter(GenericAdapter):
    _model_name = 'magento.sale.cart'
    _magento_model = 'ec_cart'

    def search(self, filters=None, magento_store_ids=None):
        """ Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        if filters is None:
            filters = {}
        if magento_store_ids is not None:
            filters['store_id'] = {'in': magento_store_ids}
        arguments = {
            'store_id': magento_store_ids,
        }
        return super(CartAdapter, self).search(arguments)


@magento_sparkmodel
class CartImportMapper(SaleOrderImportMapper):
    _model_name = 'magento.sale.cart'

    direct = [('entity_id', 'magento_id'),
              ('entity_id', 'magento_cart_id'),
              ('grand_total', 'total_amount'),
              ('tax_amount', 'total_amount_tax'),
              ('created_at', 'date_order')
              ]

    children = [('items', 'magento_cart_line_ids', 'magento.sale.cart.line')]

    def _after_mapping(self, result):
        sess = self.session
        # TODO: refactor: do no longer store the transient fields in the
        # result, use a ConnectorUnit to create the lines
        if 'magento_cart_line_ids' not in result:
            result['magento_cart_line_ids'] = []
        result.pop('value')
        result = sess.pool['sale.order']._convert_special_fields(
            sess.cr,
            sess.uid,
            result,
            result['magento_cart_line_ids'],
            sess.context)
        # remove transient fields otherwise OpenERP will raise a warning
        # or even fail to create the record because the fields do not
        # exist

        onchange = self.get_connector_unit_for_model(SaleOrderOnChange)
        return onchange.play(result, result['magento_cart_line_ids'])

    @mapping
    def company(self, record):
        sess = self.session
        binder = self.get_binder_for_model('magento.res.partner')
        partner_id = binder.to_openerp(record['customer_id'], unwrap=True)
        partner = sess.pool.get('res.partner').browse(
            sess.cr, sess.uid, partner_id, context=sess.context)
        if not partner:
            raise MappingError("The store does not exist in magento.\
                You need to import it first")
        return {'company_id': partner.company_id.id}

    @mapping
    def payment(self, record):
        return {'payment_method_id': 1}

    @mapping
    def state(self, record):
        return {'state': 'cart'}

    @mapping
    def name(self, record):
        partner_id = self.customer_id(record)['partner_id']
        name = str(partner_id)
        prefix = self.backend_record.cart_prefix
        if prefix:
            name = prefix + name
        return {'name': name}

    @mapping
    def shipping_method(self, record):
        sess = self.session
        carrier_pool = sess.pool.get('delivery.carrier')
        carrier_ids = carrier_pool.search(sess.cr, sess.uid, [])
        if carrier_ids:
            return {'carrier_id': carrier_ids[0]}
        return {'carrier_id': None}

    def get_terms(self, part):
        sess = self.session
        if not part:
            return {
                'value':
                {
                    'partner_invoice_id': False,
                    'partner_shipping_id': False,
                    'payment_term': False,
                    'fiscal_position': False
                }
            }

        addr = sess.pool.get('res.partner').address_get(
            sess.cr,
            sess.uid,
            [part.id],
            ['delivery', 'invoice', 'contact'])
        pricelist = (part.property_product_pricelist and
                     part.property_product_pricelist.id or False)
        payment_term = (part.property_payment_term and
                        part.property_payment_term.id or False)
        fiscal_position = (part.property_account_position and
                           part.property_account_position.id or False)
        dedicated_salesman = part.user_id and part.user_id.id or sess.uid
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
        }
        if pricelist:
            val['pricelist_id'] = (part.property_product_pricelist and
                                   part.property_product_pricelist.id or False)
        return {'value': val}

    @mapping
    def invoicing_terms(self, record):
        sess = self.session
        binder = self.get_binder_for_model('magento.res.partner')
        partner_id = binder.to_openerp(record['customer_id'], unwrap=True)
        partner = sess.pool.get('res.partner').browse(
            sess.cr,
            sess.uid,
            partner_id,
            context=sess.context)
        if not partner:
            raise MappingError("The partner does not exist in magento.\
                You need to import it first")
        terms = self.get_terms(partner)
        return terms

    @mapping
    def invoice(self, record):
        return {'partner_invoice_id': 1}

    @mapping
    def shipping(self, record):
        return {'partner_shipping_id': 1}


@magento_sparkmodel
class SaleCartImport(MagentoImportSynchronizer):
    _model_name = ['magento.sale.cart']


@job
def sale_cart_import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from Magento """
    if filters is None:
        filters = {}
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(CartBatchImport)
    importer.run(filters)


@magento_sparkmodel
class CartLineImportMapper(SaleOrderLineImportMapper):
    _model_name = 'magento.sale.cart.line'


def _play_order_onchange(self, order):
    """ Play the onchange of the sale order

    :param order: a dictionary of the value of your sale order
    :type: dict

    :return: the value of the sale order updated with the onchange result
    :rtype: dict
    """
    sale_model = self.session.pool.get('sale.order')

    # Play partner_id onchange
    args, kwargs = self._get_shop_id_onchange_param(order)
    res = sale_model.onchange_shop_id(self.session.cr,
                                      self.session.uid,
                                      *args,
                                      **kwargs)
    self.merge_values(order, res)

    args, kwargs = self._get_partner_id_onchange_param(order)
    res = sale_model.onchange_partner_id(self.session.cr,
                                         self.session.uid,
                                         *args,
                                         **kwargs)
    self.merge_values(order, res)

    # apply payment method
    args, kwargs = self._get_payment_method_id_onchange_param(order)
    res = sale_model.onchange_payment_method_id(self.session.cr,
                                                self.session.uid,
                                                *args,
                                                **kwargs)
    self.merge_values(order, res)

    # apply default values from the workflow
    # args, kwargs = self._get_workflow_process_id_onchange_param(order)
    res = sale_model.onchange_workflow_process_id(self.session.cr,
                                                  self.session.uid,
                                                  *args,
                                                  **kwargs)
    self.merge_values(order, res)
    return order

SaleOrderOnChange._play_order_onchange = _play_order_onchange


@magento_sparkmodel
class CartDeleteSynchronizer(MagentoDeleteSynchronizer):
    """ Partner deleter for Magento """
    _model_name = ['magento.sale.cart']


@magento_sparkmodel
class CartExport(MagentoExporter):
    _model_name = ['magento.sale.cart']

    # def _create(self, data):
    #     """ Create the Magento record """
    #     return self.backend_adapter.create('simple',data)

    def _run(self, fields=None):
        """ Flow of the synchronization, implemented in inherited classes"""
        assert self.binding_id
        assert self.binding_record
        if not self.magento_id:
            fields = None  # should be created with all the fields

        if self._has_to_skip():
            return

        # export the missing linked resources
        self._export_dependencies()

        self._map_data(fields=fields)

        if self.magento_id:
            record = self.mapper.data
            if not record:
                return _('Nothing to export.')
            # special check on data before export
            self._validate_data(record)
            self._update(record)
        else:
            record = self.mapper.data_for_create
            if not record:
                return _('Nothing to export.')
            # special check on data before export
            self._validate_data(record)
            self.magento_id = self._create(record)
        _logger.debug(
            'Record exported with ID %s on Magento.', self.magento_id)
        return _('Record exported with ID %s on Magento.') % self.magento_id


@magento_sparkmodel
class CartExportMapper(ExportMapper):
    _model_name = 'magento.sale.cart'

    @mapping
    def item(self, record):
        sess = self.session
        result = {'items': []}
        product_pool = sess.pool.get('magento.product.product')
        for line in record.magento_cart_line_ids:
            product_ids = product_pool.search(
                sess.cr,
                sess.uid,
                [('backend_id', '=', self.backend_record.id),
                 ('openerp_id', '=', line.product_id.id)])
            product = product_pool.browse(sess.cr, sess.uid, product_ids[0])
            result['items'].append(
                {'entity_id': product.magento_id,
                 'removed_quantity': line.final_qty})
        return result


@job
def cart_import_batch(session, model_name, backend_id, filters=None):
    """ Prepare the import of partners modified on Magento """
    if filters is None:
        filters = {}
    assert 'magento_store_ids' in filters, (
           'Missing information about Magento Website')
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(CartBatchImport)
    importer.run(filters=filters)


# Wishlist
@magento_sparkmodel
class SaleWishlistImport(MagentoImportSynchronizer):
    _model_name = ['magento.sale.wishlist']


@magento_sparkmodel
class MagentoSaleWishlistOnChange(SaleOrderOnChange):
    _model_name = 'magento.sale.wishlist'

    def play(self, order, order_lines):
        """ Play the onchange of the sale order and it's lines

        :param order: data of the sale order
        :type: dict

        :return: the value of the sale order updated with the onchange result
        :rtype: dict
        """
        sess = self.session
        # play onchange on sale order
        order = self._play_order_onchange(order)
        # play onchange on sale order line
        processed_order_lines = []
        line_lists = [order_lines]

        # TODO CHANGE THAT PART
        wishlist_pool = sess.pool.get('magento.sale.wishlist')
        search = [('backend_id', '=', self.backend_record.id),
                  ('magento_wishlist_id', '=', order['magento_wishlist_id'])]
        wishlist_ids = wishlist_pool.search(sess.cr, sess.uid, search)

        sale_order_line_pool = sess.pool.get('sale.order.line')
        if wishlist_ids:
            wishlist = wishlist_pool.browse(sess.cr, sess.uid, wishlist_ids[0])
            lines_to_delete = [l.id for l in wishlist.openerp_id.order_line]
            sale_order_line_pool.unlink(sess.cr, sess.uid, lines_to_delete)
        # ######################

        if 'order_line' in order and order['order_line'] is not order_lines:
            # we have both backend-dependent and oerp-native order
            # lines.
            # oerp-native lines can have been added to map
            # shipping fees with an OpenERP Product
            line_lists.append(order['order_line'])
        for line_list in line_lists:
            for idx, line in enumerate(line_list):
                # line_list format:[(0, 0, {...}), (0, 0, {...})]
                old_line_data = line[2]
                new_line_data = self._play_line_onchange(old_line_data,
                                                         processed_order_lines,
                                                         order)

                new_line = (0, 0, new_line_data)
                processed_order_lines.append(new_line)
                # in place modification of the sale order line in the list
                line_list[idx] = new_line
        return order


class magento_sale_wishlist(orm.Model):
    _name = 'magento.sale.wishlist'
    _inherit = 'magento.binding'
    _inherits = {'sale.order': 'openerp_id'}

    _columns = {
        'openerp_id': fields.many2one('sale.order',
                                      string='Magento order',
                                      required=True,
                                      ondelete='cascade'),
        'magento_wishlist_line_ids': fields.one2many(
            'magento.sale.wishlist.line',
            'magento_wishlist_id',
            'Magento Wishlist Lines'),
        'total_amount': fields.float(
            'Total amount',
            digits_compute=dp.get_precision('Account')),
        'total_amount_tax': fields.float(
            'Total amount w. tax',
            digits_compute=dp.get_precision('Account')),
        'magento_wishlist_id': fields.integer(
            'Magento Wishlist ID',
            help="Wishlist identifier field in Magento"),
        # when a sale order is modified, Magento creates a new one, cancels
        # the parent order and link the new one to the canceled parent
        'magento_parent_id': fields.many2one('magento.sale.order',
                                             string='Parent Magento Order'),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A partner tag with same ID on Magento already exists.'),
    ]


class magento_sale_wishlist_line(orm.Model):
    _name = 'magento.sale.wishlist.line'
    _inherit = 'magento.binding'
    _inherits = {'sale.order.line': 'openerp_id'}

    def _get_lines_from_order(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('magento.sale.wishlist.line')
        return line_obj.search(cr, uid,
                               [('magento_wishlist_id', 'in', ids)],
                               context=context)
    _columns = {
        'magento_wishlist_id': fields.many2one(
            'magento.sale.wishlist',
            'Magento Sale Order',
            required=True,
            ondelete='cascade',
            select=True),
        'openerp_id': fields.many2one('sale.order.line',
                                      string='Sale Order Line',
                                      required=True,
                                      ondelete='cascade'),
        'backend_id': fields.related(
            'magento_wishlist_id', 'backend_id',
            type='many2one',
            relation='magento.backend',
            string='Magento Backend',
            store={
                'magento.sale.wishlist.line':
                (lambda self, cr, uid, ids, c=None: ids,
                    ['magento_wishlist_id'], 10),
                'magento.sale.wishlist':
                (_get_lines_from_order, ['backend_id'], 20)
            },
            readonly=True),
        'tax_rate': fields.float('Tax Rate',
                                 digits_compute=dp.get_precision('Account')),
        'notes': fields.char('Notes'),  # XXX common to all ecom sale orders

    }

    def create(self, cr, uid, vals, context=None):
        magento_wishlist_id = vals['magento_wishlist_id']
        info = self.pool['magento.sale.wishlist'].read(
            cr,
            uid,
            [magento_wishlist_id],
            ['openerp_id'],
            context=context)
        order_id = info[0]['openerp_id']
        vals['order_id'] = order_id[0]
        return super(magento_sale_wishlist_line, self).create(
            cr,
            uid,
            vals,
            context=context)


@magento_sparkmodel
class WishlistBatchImport(DelayedBatchImport):
    """ Delay import of the records """
    _model_name = ['magento.sale.wishlist']

    def run(self, filters=None):
        """ Run the synchronization """
        if filters is None:
            filters = {}
        record_ids = self.backend_adapter.search(filters)
        _logger.info('search for magento saleorders %s  returned %s',
                     filters, record_ids)
        for record_id in record_ids:
            self._import_record(record_id)


@magento_sparkmodel
class WishlistAdapter(GenericAdapter):
    _model_name = 'magento.sale.wishlist'
    _magento_model = 'ec_mwishlist'

    def search(self, filters=None, magento_store_ids=None):
        """ Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        if filters is None:
            filters = {}
        arguments = {
            'reservation': filters.get('reservation', False)
        }
        return super(WishlistAdapter, self).search(arguments)


@magento_sparkmodel
class WishlistImportMapper(SaleOrderImportMapper):
    _model_name = 'magento.sale.wishlist'

    direct = [('wishlist_id', 'magento_id'),
              ('wishlist_id', 'magento_wishlist_id'),
              ('created_at', 'date_order'),
              ('date_order', 'date_order')]

    children = [
        ('items', 'magento_wishlist_line_ids', 'magento.sale.wishlist.line')
    ]

    def _after_mapping(self, result):
        sess = self.session
        # TODO: refactor: do no longer store the transient fields in the
        # result, use a ConnectorUnit to create the lines
        if 'magento_wishlist_line_ids' not in result:
            result['magento_wishlist_line_ids'] = []
        result.pop('value')
        result = sess.pool['sale.order']._convert_special_fields(
            sess.cr,
            sess.uid,
            result,
            result['magento_wishlist_line_ids'],
            sess.context)
        # remove transient fields otherwise OpenERP will raise a warning
        # or even fail to create the record because the fields do not
        # exist
        onchange = self.get_connector_unit_for_model(SaleOrderOnChange)
        return onchange.play(result, result['magento_wishlist_line_ids'])

    @mapping
    def company(self, record):
        sess = self.session
        binder = self.get_binder_for_model('magento.res.partner')
        partner_id = binder.to_openerp(record['customer_id'], unwrap=True)
        partner = sess.pool.get('res.partner').browse(
            sess.cr, sess.uid, partner_id, context=sess.context)
        if not partner:
            raise MappingError("The store does not exist in magento.\
                You need to import it first")
        return {'company_id': partner.company_id.id}

    @mapping
    def payment(self, record):
        return {'payment_method_id': 1}

    @mapping
    def state(self, record):
        state = 'wishlist' if record['wishlist'] else 'reservation'
        return {'state': state}

    @mapping
    def name(self, record):
        partner_id = self.customer_id(record)['partner_id']
        name = str(partner_id)
        prefix = self.backend_record.reservation_prefix
        # output is a char equals to either 1 or 0
        if record['wishlist']:
            prefix = self.backend_record.wishlist_prefix
        if prefix:
            name = prefix + name
        return {'name': name}

    @mapping
    def shipping_method(self, record):
        sess = self.session
        carrier_pool = sess.pool.get('delivery.carrier')
        carrier_ids = carrier_pool.search(sess.cr, sess.uid, [])
        if carrier_ids:
            return {'carrier_id': carrier_ids[0]}
        return {'carrier_id': None}

    def get_terms(self, part):
        sess = self.session
        if not part:
            return {
                'value':
                {
                    'partner_invoice_id': False,
                    'partner_shipping_id': False,
                    'payment_term': False,
                    'fiscal_position': False
                }
            }

        addr = sess.pool.get('res.partner').address_get(
            sess.cr,
            sess.uid,
            [part.id],
            ['delivery', 'invoice', 'contact'])
        pricelist = (part.property_product_pricelist and
                     part.property_product_pricelist.id or False)
        payment_term = (part.property_payment_term and
                        part.property_payment_term.id or False)
        fiscal_position = (part.property_account_position and
                           part.property_account_position.id or False)
        dedicated_salesman = part.user_id and part.user_id.id or sess.uid
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
        }
        if pricelist:
            val['pricelist_id'] = (part.property_product_pricelist and
                                   part.property_product_pricelist.id or False)
        return {'value': val}

    @mapping
    def invoicing_terms(self, record):
        sess = self.session
        binder = self.get_binder_for_model('magento.res.partner')
        partner_id = binder.to_openerp(record['customer_id'], unwrap=True)
        partner = sess.pool.get('res.partner').browse(
            sess.cr,
            sess.uid,
            partner_id,
            context=sess.context)
        if not partner:
            raise MappingError("The partner does not exist in magento.\
                You need to import it first")
        terms = self.get_terms(partner)
        return terms

    @mapping
    def invoice(self, record):
        return {'partner_invoice_id': 1}

    @mapping
    def shipping(self, record):
        return {'partner_shipping_id': 1}


@job
def sale_wishlist_import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from Magento """
    if filters is None:
        filters = {}
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(WishlistBatchImport)
    importer.run(filters)


@magento_sparkmodel
class WishlistLineImportMapper(SaleOrderLineImportMapper):
    _model_name = 'magento.sale.wishlist.line'

    direct = [('qty_ordered', 'product_uom_qty'),
              ('item_id', 'magento_id')]

    def _partner(self, record):
        binder = self.get_binder_for_model('magento.res.partner')
        partner_id = binder.to_openerp(record['customer_id'], unwrap=True)
        assert partner_id is not None, \
            ("customer_id %s should have been imported in "
             "SaleOrderImport._import_dependencies" % record['customer_id'])
        sess = self.session
        return sess.pool.get('res.partner').browse(
            sess.cr, sess.uid, partner_id, context=sess.context)

    @mapping
    def name(self, record):
        product_id = self.product_id(record)['product_id']
        assert product_id
        sess = self.session
        product_pool = self.session.pool.get('product.product')
        product = product_pool.browse(
            sess.cr, sess.uid, product_id, context=sess.context)
        return {'name': product.name}

    @mapping
    def price(self, record):
        product_id = self.product_id(record)['product_id']
        assert product_id
        sess = self.session
        partner = self._partner(record)
        pricelist_id = (partner.property_product_pricelist.id
                        if partner.property_product_pricelist
                        else False)
        pricelist_pool = sess.pool.get('product.pricelist')
        price_unit = pricelist_pool.price_get(
            sess.cr, sess.uid, [pricelist_id],
            product_id, float(record['qty_ordered']))
        price = price_unit[int(pricelist_id)]
        return {'price_unit': price}

    @mapping
    def product_options(self, record):
        return {}

    @mapping
    def so_state(self, record):
        return {'so_state': 'draft'}


def _play_order_onchange(self, order):
    """ Play the onchange of the sale order

    :param order: a dictionary of the value of your sale order
    :type: dict

    :return: the value of the sale order updated with the onchange result
    :rtype: dict
    """
    sale_model = self.session.pool.get('sale.order')

    # Play partner_id onchange
    args, kwargs = self._get_shop_id_onchange_param(order)
    res = sale_model.onchange_shop_id(self.session.cr,
                                      self.session.uid,
                                      *args,
                                      **kwargs)
    self.merge_values(order, res)

    args, kwargs = self._get_partner_id_onchange_param(order)
    res = sale_model.onchange_partner_id(self.session.cr,
                                         self.session.uid,
                                         *args,
                                         **kwargs)
    self.merge_values(order, res)

    # apply payment method
    args, kwargs = self._get_payment_method_id_onchange_param(order)
    res = sale_model.onchange_payment_method_id(self.session.cr,
                                                self.session.uid,
                                                *args,
                                                **kwargs)
    self.merge_values(order, res)

    # apply default values from the workflow
    # args, kwargs = self._get_workflow_process_id_onchange_param(order)
    # res = sale_model.onchange_workflow_process_id(self.session.cr,
    #                                               self.session.uid,
    #                                               *args,
    #                                               **kwargs)
    self.merge_values(order, res)
    return order

SaleOrderOnChange._play_order_onchange = _play_order_onchange


@magento_sparkmodel
class WishlistDeleteSynchronizer(MagentoDeleteSynchronizer):
    """ Partner deleter for Magento """
    _model_name = ['magento.sale.wishlist']


@magento_sparkmodel
class WishlistExport(MagentoExporter):
    _model_name = ['magento.sale.wishlist']


@magento_sparkmodel
class WishlistExportMapper(ExportMapper):
    _model_name = 'magento.sale.wishlist'

    @mapping
    def item(self, record):
        sess = self.session
        result = {'items': {}}
        product_pool = sess.pool.get('magento.product.product')
        for line in record.magento_wishlist_line_ids:
            product_ids = product_pool.search(
                sess.cr,
                sess.uid,
                [('backend_id', '=', self.backend_record.id),
                 ('openerp_id', '=', line.product_id.id)])
            product = product_pool.browse(sess.cr, sess.uid, product_ids[0])
            result['items'][product.magento_id] = line.final_qty
        return result

    @mapping
    def customer(self, record):
        sess = self.session
        mag_partner_pool = sess.pool.get('magento.res.partner')
        partner_ids = mag_partner_pool.search(
            sess.cr, sess.uid,
            [('openerp_id', '=', record.partner_id.id),
             ('backend_id', '=', record.backend_id.id)])
        partner = mag_partner_pool.read(
            sess.cr, sess.uid, partner_ids[0], ['magento_id'])
        return {'customer_id': partner['magento_id']}


@job
def wishlist_import_batch(session, model_name, backend_id, filters=None):
    """ Prepare the import of partners modified on Magento """
    if filters is None:
        filters = {}
    assert 'magento_store_ids' in filters, (
           'Missing information about Magento Website')
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(WishlistBatchImport)
    importer.run(filters=filters)
