# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Qing Wang <wang.qing@elico-corp.com>
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
from api import ServerProxy


SERVER = 'http://127.0.0.1:8069'
DADABASE = 'mmx_trunk7'
USER = 'admin'
PASSWORD = 'MMX3licoC0rp'

# MMX Trunk Environment
# SERVER = 'http://106.186.122.175:6172'
# DADABASE = 'trunk_mmx'
# USER = 'admin'
# PASSWORD = 'password'


def _create_magento_model_option(socket, session):
    """
        For one product model we need to create one attribute option
        in odoo , and then export the options to magento as attribute options
    """
    result = socket.read(
        session, 'product.model',
        [], ('name', 'backend_ids', 'attribute_id'))

    for obj in result:
        for backend in obj['backend_ids']:
            option_vals = {
                'name': obj['name'],
                'backend_id': backend,
                'magento_attribute_id': obj['attribute_id'][0],
                'value': obj['id'],
                'model_id': obj['id'],
            }

            socket.create(session, 'magento.attribute.option', option_vals)


def export_all_product_model(socket, session):
    """
        After prepare all the model data in Odoo
        we need to export all the products which set scale
        to magento
    """
    model_product_ids = socket.search(
        session, 'product.product', [('model_id', '!=', False)])

    socket.write(session, 'product.product', model_product_ids, {})


def update_model_data(socket, session):
    """
        *   Before do this step, you should create
            mmx_model attribute in odoo,
            and export this attribute to magento
        *   Update All the Old Data to bind new attribute
            and the backend
    """
    _model_name = 'product.model'

    backend_ids = socket.search(
        session, 'magento.backend', [])

    attribute_ids = socket.search(
        session, 'magento.product.attribute',
        [('attribute_code', '=', 'x_mmx_model')])

    values = {
        'backend_ids': [(6, 0, backend_ids)],
        'attribute_id': attribute_ids[0]
    }
    ids = socket.search(session, _model_name, [])
    socket.write(session, _model_name, ids, values)


if __name__ == '__main__':
    socket = ServerProxy(SERVER, DADABASE, USER, PASSWORD)
    session = socket.login()
    #First We should Update all the old data
    # update_model_data(socket, session)
    #Second We need to create one option for one scale data
    _create_magento_model_option(socket, session)
    #Before this step we need to bind the new attribute
    #with attibute set in magento
    # export_all_product_model(socket, session)
