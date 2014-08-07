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


class product_circuit(osv.osv):
    _name = 'product.circuit'
    
    _columns = {
        'name':       fields.char('Circuit', size=128, required=True, translate=False),
        'lenght':     fields.integer('Length (m)'),
        'city':       fields.char('City', size=64),
        'country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
    }

product_circuit()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: