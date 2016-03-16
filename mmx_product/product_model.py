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
import time


class product_model(osv.osv):
    _name = 'product.model'
    
    def _get_fullname(self,cr,uid,ids,fields_name,args=None,context=None):
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            fname     = ''.join([m.manufacturer_id.name, r' ', m.name])
            res[m.id] = fname
        return res
    
    _columns={
        'name':            fields.char('Model', size=256, required=True, translate=False),
        'manufacturer_id': fields.many2one('product.manufacturer', 'Manufacturer', required=True, ondelete='restrict'),
        'fullname':        fields.function(_get_fullname, type='char', size=256, args=None, store=True, string='Full Name'),
    }

    _sql_constraints=[
        ('name_manufacturer_uniq', 'unique(name,manufacturer_id)','name and manufacturer cannot be repeated'),
    ]
    
    def name_get(self, cr, uid, ids, context=None):
        result = []
        if type(ids) != type([]):
            ids = [ids]
        for m in self.browse(cr, uid, ids, context=context):
            result.append((m.id, m.fullname))
        return result
    
    
    #Jon  default search by fullname
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        
        if name:
            ids = self.search(cr, user, [('fullname','ilike',name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        
        return self.name_get(cr, user, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: