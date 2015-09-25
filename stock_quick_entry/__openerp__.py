# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Andy Lu <andy.lu@elico-corp.com>
#            Alex Duan<alex.duan@elico-corp.com>
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
    'name': 'Quick internal move entry',
    'version': '1.0',
    'category': 'Stock',
    'sequence': 19,
    'summary': 'Quick internal move entry',
    'description': """
 .. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Quick Internal Move Entry
=========================

This module gives you an interface to create internal moves.
    * The source and destinate location is internal type,
    which lower the possibility of user mistake.
    * Added a new field: min date onto model: stock picking

Added a new menu: Quick internal move.
    """,
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'images': [],
    'depends': ['stock'],
    'data': [
        'stock_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
