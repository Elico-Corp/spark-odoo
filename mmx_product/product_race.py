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


class product_race(osv.osv):
    _name = 'product.race'
    
    _columns = {
        'name':             fields.char('Race', size=32 ,required=True, translate=False),
        'championship_ids': fields.many2many('product.championship', 'race_championship_rel', 'race_id', 'championship_id', 'Championships'),
        'circuit_id':       fields.many2one('product.circuit', 'Circuit', ondelete='restrict'),
        'country_id':       fields.related('circuit_id', 'country_id', type='many2one', relation='res.country', string='Country', readonly=True),
    }

    _sql_constraints=[
        ('name_uniq', 'unique(name)', 'Name cannot be duplicated'),
    ]
    
    def onchange_circuit(self,cr,uid,ids, circuit_id=None,context=None):
        if circuit_id:
            circuit = self.pool.get('product.circuit').browse(cr,uid,circuit_id)
            return {'value':{'country_id':circuit.country_id.id}}
        else:
            return {'value':{'country_id':False}}

product_race()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: