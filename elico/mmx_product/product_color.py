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

from openerp.osv import fields, osv


class product_color (osv.osv):
    _name = 'product.color'
    
    _columns = {
        'name': fields.char('Color', size=16, required=True, translate=False),
        'code': fields.char('Code',  size=16),
    }
    _sql_constraints=[
        ('name_uniq', 'unique(name)', 'This color is already used, please choose another one.'),
        ('code_uniq', 'unique(code)', 'This code is already used, please choose another one.'),
    ]

product_color()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: