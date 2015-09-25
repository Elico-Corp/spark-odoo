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


class product_archive(osv.osv):
    _name = 'product.archive'
    
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (long, int)):
            ids = [ids]
        if not len(ids):
            return []
        
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res   = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res
    
    
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)    
    
    
    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('SELECT DISTINCT(parent_id) FROM product_archive WHERE id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True
    
    
    _columns = {
        'name':          fields.char('Location', size=16 ,  translate=False),
        'parent_id':     fields.many2one('product.archive', 'Parent', ondelete='restrict'),
        'complete_name': fields.function(_name_get_fnc, type="char",  string='Name'),
        'parent_left':   fields.integer('Left Parent',  select=1),
        'parent_right':  fields.integer('Right Parent', select=1),
    }
    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive archive.', ['parent_id'])
    ]
    
product_archive()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: