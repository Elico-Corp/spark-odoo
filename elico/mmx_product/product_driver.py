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
import re

#Jon: only to ondelete='restrict'  for championship_id,  driver_championship_rel  is  m2m for  product_driver.championship_ids
#     m2m fields not 'ondelete' arg, so add it at here.
#===============================================================================
# class  driver_championship_rel(osv.osv):
#   _name = 'driver.championship.rel'
#   
#   _columns = {
#       'championship_id': fields.many2one('product.championship', 'Championship', ondelete='restrict')
#   }
#
# driver_championship_rel()
#===============================================================================



class product_driver(osv.osv):
    _name = 'product.driver'
    
    def _get_fullname(self,cr,uid,ids, fields_name,args=None,context=None):
        res = {}
        for driver in self.browse(cr, uid, ids):
            words = re.split('\s+', driver.name)
            pre   = '. '.join([w[0].upper() for w in words])
            fname = ''.join([pre, r'. ', driver.surname]) 
            res[driver.id] = fname
        return res
    
    _columns = {
        'name':             fields.char('Name',    size=64, required=True, translate=False),
        'surname':          fields.char('Surname', size=64, required=True, translate=False, select=True),
        'country_id':       fields.many2one('res.country', 'Nationality', ondelete='restrict'),
        'championship_ids': fields.many2many('product.championship', 'driver_championship_rel', 'driver_id', 'championship_id', 'Championships'),
        'wtitles':          fields.integer('World Titles'),
        'career_from':      fields.char('Debut',      size=16),
        'career_to':        fields.char('Retirement', size=16),
        'fullname':         fields.function(_get_fullname, type='char', size=32, args=None, store=True, string='Full Name'),
    }
    _sql_constraints=[
        ('title_2_digit', 'CHECK(wtitles  < 100)', 'World Titles must be 2 digits. Eg: "12"'),
    ]
    
    
    def name_get(self, cr, uid, ids, context=None):
        result = []
        if type(ids) != type([]):
            ids = [ids]
        for d in self.browse(cr, uid, ids, context=context):
            result.append((d.id, d.fullname))
        return result
    
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        results = super(product_driver, self).name_search(cr, uid, name, args=args ,operator=operator, context=context, limit=limit)
        ids     = self.search(cr, uid, [('surname', operator, name)], limit=limit, context=context)
        results = list(set(results + self.name_get(cr, uid, ids, context))) # Merge the results
        return results

product_driver()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: