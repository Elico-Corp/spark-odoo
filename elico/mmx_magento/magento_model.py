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
from openerp.osv import fields, orm
from openerp.addons.connector.session import ConnectorSession
from .sale import cart_import_batch
from .sale import wishlist_import_batch
from openerp.addons.magentoerpconnect.partner import partner_import_batch


class magento_backend(orm.Model):
    _inherit = 'magento.backend'

    def _select_versions(self, cr, uid, context=None):
        """ Available versions

        Can be inherited to add custom versions.
        """
        versions = super(magento_backend, self)._select_versions(
            cr, uid, context=context)
        versions.append(('1.7-sparkmodel', '1.7 - Sparkmodel'))
        return versions

    _columns = {
        'version': fields.selection(
            _select_versions, string='Version', required=True),
        'import_carts_from_date': fields.datetime('Import carts from date'),
        'import_wishlists_from_date': fields.datetime('Import wishlists from date'),
        'wishlist_prefix': fields.char(
            'Wishlist Prefix',
            help="A prefix put before the name of imported wishlist.\n"
                 "For instance, if the prefix is 'mag-', the wishlist "
                 "100000692 in Magento, will be named 'wishlist-100000692' "
                 "in OpenERP."),
        'cart_prefix': fields.char(
            'Cart Prefix',
            help="A prefix put before the name of imported cart.\n"
                 "For instance, if the prefix is 'mag-', the cart "
                 "100000692 in Magento, will be named 'cart-100000692' "
                 "in OpenERP."),
    }

    def import_cart(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        self.check_magento_structure(cr, uid, ids, context=context)
        for backend in self.browse(cr, uid, ids, context=context):
            for website in backend.website_ids:
                website.import_carts()
        return True

    def import_wishlist(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        self.check_magento_structure(cr, uid, ids, context=context)
        for backend in self.browse(cr, uid, ids, context=context):
            for website in backend.website_ids:
                website.import_wishlists()
        return True


class magento_website(orm.Model):
    _inherit = 'magento.website'

    def _authorized_company(
            self, cr, uid, website_id, company_id, context=None):
        website = self.browse(cr, uid, website_id)
        if not website.store_ids:
            return False
        store = website.store_ids[0].openerp_id
        if not store.company_id:
            return False
        if store.company_id.id != company_id:
            return False
        return True

    def import_partners(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for website in self.browse(cr, uid, ids, context=context):
            if(not self._authorized_company(
                    cr,
                    uid,
                    website.id,
                    user.company_id.id,
                    context=context)
                    or website.code == 'admin'):
                continue
            backend_id = website.backend_id.id
            from_date = None
            partner_import_batch.delay(
                session, 'magento.res.partner', backend_id,
                {'magento_website_id': website.magento_id,
                 'from_date': from_date})
        return True

    def import_carts(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for website in self.browse(cr, uid, ids, context=context):
            if(not self._authorized_company(
                    cr,
                    uid,
                    website.id,
                    user.company_id.id,
                    context=context)
                    or website.code == 'admin'):
                continue
            # store_ids = [ store.magento_id for store in website.store_ids]
            store_ids = []
            for store in website.store_ids:
                if store.magento_id:
                    v_ids = store.storeview_ids
                    store_ids.append([v.magento_id for v in v_ids])
            backend_id = website.backend_id.id
            cart_import_batch(
                session, 'magento.sale.cart', backend_id,
                {'magento_store_ids': store_ids})
        return True

    def import_wishlists(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for website in self.browse(cr, uid, ids, context=context):
            if(not self._authorized_company(
                    cr,
                    uid,
                    website.id,
                    user.company_id.id,
                    context=context)
                    or website.code == 'admin'):
                continue
            # store_ids = [ store.magento_id for store in website.store_ids]
            store_ids = []
            for store in website.store_ids:
                if store.magento_id:
                    v_ids = store.storeview_ids
                    store_ids.append([v.magento_id for v in v_ids])
            backend_id = website.backend_id.id
            wishlist_import_batch(
                session, 'magento.sale.wishlist', backend_id,
                {'magento_store_ids': store_ids})
        return True
magento_backend()
