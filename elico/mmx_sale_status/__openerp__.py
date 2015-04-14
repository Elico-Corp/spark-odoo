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
    'name': 'MMX Sale',
    'version': '1.0',
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'summary': '',
    'description': """
    This Module adds to SO the following fields:
    - Is Cart: boolean field to define a SO as cart.
    It will be used as part of the Magento sync system.
    A sql constraint limit the is_cart to one per partner.
    This Module adds to SO Line the following fields:
    - Product State:
        Function field to read the current product state
    - Product_id: domain to limit product state insertion in SOL

    A SO can be confirmed only if all the SOL are on state "order".

    A Wizard (available only if SO is in state draft) will allow user to:
    1-    Move SOL to a new SO
    2-    Move SOL to another existing SO (of the same partner)
    3-    Move SOL back to the SO-0 [Cart] Order

    update on 2015/3/30 alex.duan@elico-corp.com
    Inherit sale.report and add the filter wishlist.
    """,
    'depends': ['mmx_magento', 'sale_order_line',
                'purchase_order_line', 'mmx_product_advance', 'sale_shipment',
                'sale_exceptions', 'base_intercompany', 'sale_stock'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'wizard/wizard_order_split_view.xml',
        'wizard/wizard_sol_split_view.xml',
        'wizard/wizard_assign_shipment_view.xml',
        'sale_view.xml',
        'purchase_view.xml',
        'sale_wkf.xml',
        'security/ir_rule_data.xml',
        'report/sale_report_view.xml'
    ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
