# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
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
    'name': 'MMX Quotation mass import',
    'version': '1.0',
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'summary': '',
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

MMX Quotation Mass import
========================

This module depends on the module: mmx_sale_status, allow user
mass importing the quotation on specific rule.

**csv file header**:
    partner_id (char, linked to the reference in the partner form)
    address_id (char, linked to the reference in the partner form)
    product_id (char, linked to the internal reference in the product form)
    quantity (float)

In the wizard, the following selection should be available:
date: to be used for the SO date
shop: to be used for the SO shop

**Import process**
Note: here we only talk about the quotations with checkbox(is_imported) checked
-------------------------------------------------------------------------------
Import all information from the Excel into
SO of type quotation (specific status)

If a partner reference or product reference is not found, skip the line,
continue the process and display a window with error message
and the information not found
eg: partner P00001, Product LM18SM2, Product LM18SM3, Partner P0005 etc.

partner_id and invoice address in SO
address_id => delivery address in SO
product_id => product_id in SOL
quantity => product_qty in SOL
UoM is the default product UoM.

Prices in SOL should be updated based on the pricelist from the ERP
associated to the partner.
In SO, set all defaults as in the manual process (pricelist, payment terms,
    fiscal position etc.)
In SOL, set all defaults as in the manual process (UoM, VAT)
rules for SO
If SO/Quotation checked doesnot exist,
    one SO/Quotation is to be created per address_id
Do not delete the SO quotation if there is no line inside.

**Rules for SOL**
If the product line exist in the ERP and Excel:
    update the quantity with the quantity in Excel
If product line exists in the ERP, not in Excel, delete the line in the ERP
If product line doesnot exist in the ERP, and yes in Excel,
    create the line in the ERP

Installation
============

You need to have mmx_sale_status installed.

Usage
=====


Contributors
------------

* Alex Duan: alex.duan@elico-corp.com
    """,
    'depends': ['mmx_sale_status'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'wizard/wizard_quotation_mass_import_view.xml',
        'sale_view.xml'
    ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
