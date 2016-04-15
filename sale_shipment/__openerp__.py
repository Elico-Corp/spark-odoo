# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#    Rona Lin <rona.lin@elico-corp.com>
#    Victor M. Martin <victor.martin@elico-corp.com>
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

{
    'name': 'Sale Shipment',
    'version': '7.0.1.0.6',
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'summary': '',
    'description': """
    TODO: complete this description
    and ask Yaxi to provide the related documentation.
    TODO: replace mmx related information in data.xml
    """,
    'depends': ['stock', 'sale_order_line', 'sale_menu', 'sale_announcement'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'wizard/wizard_shipment_allocation_view.xml',
        'wizard/wizard_shipment_assign_sol_view.xml',
        'sale_shipment_max_qty_user_readonly.xml',
        'sale_shipment_report.xml',
        'sale_shipment_view.xml',
        'security/ir.model.access.csv',
        'sale_shipment_data.xml',
        'wizard/replenishment_transfer_view.xml',
        'sale_shipment_wkf.xml'
    ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
