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
    'name': 'MMX Purchase',
    'version': '1.0',
    'author': 'Elico Corp',
    'website': 'http://www.elico-corp.com',
    'summary': '',
    'description' : """
    The aim of the module is to give user a tool to manage allocation quantities.
    
    This module adds to PO Line the following fields:
    - Allocated qty
    - Notes
    To Confirm a PO, all PO lines must meet the condition: Qty = Alloc_qty
    
    A webkit report in Purchase Order Line Tree View will display QTY vs Allocated QTY for the selected PO Lines
    
    ***TO DO***
    Once the webkit report is finalized, it is necessary to have another report with only PO Lines Allocated quantity to send to the factory.
     
    """,
    'depends': ['base','purchase','purchase_order_line', 'report_webkit', 'elico_report_webkit'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'purchase_view.xml',
        'purchase_report.xml'
        # 'security/ir.model.access.csv',
        ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: