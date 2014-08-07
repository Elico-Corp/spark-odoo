# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
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
    'name': 'MMX Magento',
    'version': '1.0.0',
    'category': 'Connector',
    'depends': ['account',
                'magentoerpconnect',
                'sale',
                'sale_menu',
                'mmx_product_advance',
                'stock',],
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'summary': '',
    'description': """
    Custom Magento module
        """,
    'sequence': 10,
    'data': ['magento_model_view.xml',
             'sale_view.xml',
             'magento_view.xml',
             'product_view.xml',
             'pricelist_view.xml',
             'company_view.xml',
             # 'stock_view.xml',
             'security/ir.model.access.csv'],
    'test': [],
    'installable': True,
    'application': False,
}
