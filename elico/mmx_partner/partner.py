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

from openerp.osv import osv, fields
from openerp.tools.translate import _


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'is_company': fields.boolean(
            'Is a Company',
            help="Check if the contact is a company,"
            " otherwise it is a person"),
        'invoice_message': fields.text(
            'Invoice message',
            help="Type in the message that will appear"
            " for this partner in all invoices"),
        'customer_account_number': fields.char(
            size=125,
            string='Customer Account Number')
    }
    _defaults = {
        'is_company': lambda *a: True,
    }

res_partner()
"""
Improve the invoice with Partner message:
    In partner model and form: Add a field "Invoice message" below internal notes (same type as internal note). 
    Name: "Invoice message"
    Help: "Type in the message that will appear for this partner in all invoices".
    Not Mandatory

In the invoice sxw/rml file, add the field below the comment field.
"""
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
