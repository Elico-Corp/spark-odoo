# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    LIN Yu <lin.yu@elico-corp.com>
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
    'name':         'Purchase Order Line',
    'version':      '7.0.1.0.2',
    'category':     'Purchase',
    'sequence':     19,
    'summary':      'Purchase Order Line',
    'description':  """ Purchase Order Line Details """,
    'author':       'Elico Corp',
    'website':      'http://www.elico-corp.com',
    'images' :      [],
    'depends':      ['product', 'purchase','mmx_purchase', 'mmx_product_advance'],
    'data':         [
                     'security/ir.model.access.csv',
                     'purchase_view.xml',
                    ],
    'test':         [],
    'demo':         [],
    'installable':  True,
    'auto_install': False,
    'application':  False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: