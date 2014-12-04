# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Author: LIN Yu <lin.yu@elico-corp.com>
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
from openerp.addons.magentoerpconnect.unit.import_synchronizer import (
    import_batch)
from .product_attribute import product_attribute_import_batch
from openerp.addons.connector.session import ConnectorSession


class magento_backend(orm.Model):
    _inherit = 'magento.backend'

    def import_attributes_sets_attrs_options(self, cr, uid, ids, context=None):
        """ Available versions
        olcatalog_product_attribute.info does not work
        catalog_product_attribute.info will not return set id,
            but the params need one.
        Thus, standard connector function can not be reused.
        A new customized function is created here.

        Can be inherited to add custom versions.
        """
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)
        for backend_id in ids:
            product_attribute_import_batch.delay(session, 'magento.product.attribute', backend_id)

        return True

    def import_product_attribute_set(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        self.check_magento_structure(cr, uid, ids, context=context)
        session = ConnectorSession(cr, uid, context=context)
        for backend_id in ids:
            import_batch(session, 'magento.attribute.set',
                               backend_id)
        return True

