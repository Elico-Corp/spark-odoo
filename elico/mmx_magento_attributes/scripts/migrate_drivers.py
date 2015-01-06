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


# SERVER = 'http://127.0.0.1:8069'
# DADABASE = 'mmx_trunk7'
# USER = 'admin'
# PASSWORD = 'MMX3licoC0rp'

# MMX Trunk Environment
# SERVER = 'http://106.186.122.175:6172'
# DADABASE = 'trunk_mmx'
# USER = 'admin'
# PASSWORD = 'password'


#MMX Stable Environment
SERVER = 'http://106.186.122.175:6162'
DADABASE = 'stable_mmx'
USER = 'admin'
PASSWORD = 'MMX3licoC0rp'


def update_driver_data(socket, session):
    """
        update product.driver old data to
        bind backend_id, magento attribute
        for product deriver
    """
    backend_ids = socket.search(
        session, 'magento.backend', [])

    attribute_ids = socket.search(
        session, 'magento.product.attribute',
        [('attribute_code', '=', 'x_mmx_driver')])

    # values = {'backend_id': backend_ids[0], 'attribute_id': attribute_ids[0]}
    values = {
        'backend_ids': [(6, 0, backend_ids)],
        'attribute_id': attribute_ids[0]
    }
    ids = socket.search(session, 'product.driver', [])
    socket.write(session, 'product.driver', ids, values)


def _get_driver_data(socket, session):
    result = socket.read(
        session, 'product.driver',
        [], ('surname', 'name', 'fullname', 'backend_ids', 'attribute_id'))

    return result


def _create_magento_attibute_option(socket, session):
    driver_infos = _get_driver_data(socket=socket, session=session)

    for driver_info in driver_infos:
        option_name = driver_info['surname'] + "_" + driver_info['name']
        for backend in driver_info['backend_ids']:
            vals = {
                'name': option_name,
                'backend_id': backend,
                'magento_attribute_id': driver_info['attribute_id'][0],
                'value': driver_info['fullname'],
                'driver_id': driver_info['id'],
            }
            option_ids = socket.search(
                session,
                'magento.attribute.option',
                [('name', '=', option_name),('backend_id', '=', backend)])
            if not option_ids:
                op_id = socket.create(
                    session, 'magento.attribute.option', vals)
                print "Magento Attribute Option: %s with ID: %s , is created" % (
                    option_name, op_id)
            else:
                print "Magento Attribute Option: %s is exist" % (option_name,)


def export_all_product_scale(socket, session):
    """
        After prepare all the scale data in Odoo
        we need to export all the products which set scale
        to magento
    """
    product_ids = socket.search(
        session, 'product.product', [('driver_ids', '!=', False)])

    socket.write(session, 'product.product', product_ids, {})


if __name__ == '__main__':
    socket = ServerProxy(SERVER, DADABASE, USER, PASSWORD)
    session = socket.login()
    # update_driver_data(socket, session)
    # _create_magento_attibute_option(socket, session)
    export_all_product_scale(socket, session)
