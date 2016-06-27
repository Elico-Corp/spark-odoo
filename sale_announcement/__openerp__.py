# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Jon chow <jon.chow@elico-corp.com>
#    Author: Rona Lin <rona.lin@elico-corp.com>
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
    'name': 'Sale Announcement',
    'version': '7.0.1.2.0',
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'summary': '',
    'description': """
         Sales Announcement
    """,
    'depends': ['base', 'sale', 'product', 'report_webkit', 'sale_menu',
                'mmx_product_advance', 'sale_order_line', 'connector'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'sale_announcement_view.xml',
        'sale_announcement_wkf.xml',
        'sale_announcement_report.xml',
        'data/data.xml',
        'wizard/sale_announcement_report_view.xml',
        'security/ir.model.access.csv'],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
