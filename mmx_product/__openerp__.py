# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Damiano Falsanisi <damiano.falsanisi@elico-corp.com>, Jon Chow <jon.chow@elico-corp.com>
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
    'name': 'MMX Product',
    'version': '7.0.1.1.5',
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'summary': '',
    'description' : """
    This module contains all modification related to product except product State and MMX_type (MMX Product Advance)
        """,
    'depends': ['base', 'magentoerpconnect', 'product', 'stock', 'purchase'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'data/data.xml',
        'product_menu.xml',
        'product_brand_view.xml',
        'product_archive_view.xml',
        'product_champioship_view.xml',
        'product_driver_view.xml',
        'product_circuit_view.xml',
        'product_race_view.xml',
         'product_race_ed_view.xml',
        
        'product_team_view.xml',
        'product_scale_view.xml',
        'product_brand_view.xml',
        'product_color_view.xml',
        'product_manufacturer_view.xml',
        'product_models_view.xml',
        'product_dev_status_view.xml',
        'product_view.xml',
        'data/product.rank.csv',
        'security/ir.model.access.csv',
        
        
        ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: