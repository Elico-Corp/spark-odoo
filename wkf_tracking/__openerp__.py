# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Jon chow <jon.chow@elico-corp.com>
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
    'name':         'Object Status Tracking',
    'version':      '1.0',
    'author':       'Elico Corp',
    'website':      'http://www.elico-corp.com',
    'summary':      '',
    'description' : """This module enables to record a log of the change in the product workflow tracking.
    Objects created:
    - Workflow Tracking
        Name   
        Resource ID
        From (state)
        To (state)
        Action Time
        User
    To access this module you can go to Product/Configuration/Product Status Record
    """,
    'depends':      ['base','product','sale','stock','purchase','mmx_product'],
    'category':     '',
    'sequence':     10,
    'demo':         [],
    'data':         [
                     'wkf_tracking_view.xml',
                     'product_view.xml',
                     'sale_order_view.xml',
                     'purchase_order_view.xml',
                     'security/ir.model.access.csv',
                    ],
    'test':         [],
    'installable':  True,
    'application':  False,
    'auto_install': False,
    'css':          [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: