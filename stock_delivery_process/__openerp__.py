# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2014 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>

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

{'name': 'Stock Delivery Process',
 'version': '7.0.1.4.0',
 'category': 'Generic Modules',
 'depends': ['stock'],
 'author': 'Elico Corp',
 'license': 'AGPL-3',
 'website': 'https://www.elico-corp.com',
 'description': """
Stock Delivery Process
======================

This module is mainly for improving the process of delivery.

Adding two new check box: (on_hold, qc_approved)
Adding new fields on the responsible user and modify date.

Installation
============

Normal installation.

Configuration
=============

There are two groups introduced by this module:
- QC Approve manager
- On hold manager


Usage
=====
1- Only user who belongs to group: "On Hold Manager" can have right to modify
on_hold field both on stock picking and move level;

Only user who belongs to group: "QC approved manager" can have right to
modify qc_approved field both on stock picking and move level;

2- When you set the on hold on stock picking level, all the related
stock moves will be updated at the same time.

When you set the on hold on stock move level:
    - if on hold of all the related stock moves are False, then update the
    related picking to False.

    - if on hold of at least one of the related stock moves is True, then
    update the related picking to True.

3- When you set the QC approved on stock picking level, all the related
stock moves will be updated at the same time;

When you set the QC approved on stock move level:

    - if qc_approved of at least one of the related stock moves is False,
    then update the related picking to False.

    - if qc_approved of all the related stock moves are True, then update
    the related picking to True.

4- New filters on delivery order list view and stock move list view: "On Hold"
'QC approved'


Contributors
------------

* Alex Duan: alex.duan@elico-corp.com

""",
 'images': [],
 'demo': [],
 'data': [
     'security/security.xml',
     'stock_view.xml'
 ],
 'installable': True,
 'application': False,
 }
