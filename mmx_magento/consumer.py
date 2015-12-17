# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Yu Lin <yu.lin@actinpacific.com>
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

from openerp.addons.magentoerpconnect.unit.export_synchronizer import(
    export_record)
from openerp.addons.connector.event import (on_record_write,
                                            on_record_create,
                                            on_record_unlink
                                            )
import openerp.addons.magentoerpconnect.consumer as magentoerpconnect


@on_record_write(model_names=['sale.order'])
def delay_export_so(session, model_name, record_id, fields=[]):
    order_pool = session.pool.get(model_name)
    order = order_pool.browse(session.cr, session.uid, record_id, context=session.context)
    if order.state != 'reservation':
        return False

    try:
        mag_id = order.magento_wishlist_bind_ids[0].id
        magentoerpconnect.delay_export(session, 'magento.sale.wishlist', mag_id, fields=fields)
    except Exception as e:
        pass
    return True


@on_record_unlink(model_names=['magento.sale.wishlist'])
def delay_unlink(session, model_name, record_id):
    magentoerpconnect.delay_unlink(session, model_name, record_id)


@on_record_create(model_names=['magento.product.pricelist', 'magento.stock.move'])
@on_record_write(model_names=['magento.product.pricelist',
                              'magento.res.partner'])
def delay_export(session, model_name, record_id, fields=None):
    magentoerpconnect.delay_export(session, model_name,
                                   record_id, fields=fields)


@on_record_write(model_names=['product.pricelist', 'res.partner', 'stock.move'])
def delay_export_all_bindings(session, model_name, record_id, fields=None):
    if model_name == 'stock.move':
        stock = session.pool.get(model_name).read(session.cr, session.uid, record_id, ['product_id'])
        session.pool.get('product.product').write(session.cr, session.uid, stock['product_id'][0], {})
        return
    magentoerpconnect.delay_export_all_bindings(session, model_name,
                                                record_id, fields=fields)


@on_record_unlink(model_names=['magento.product.pricelist'])
def delay_unlink(session, model_name, record_id):
    magentoerpconnect.delay_unlink(session, model_name, record_id)
