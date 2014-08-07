
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#     Jon Chow <jon.chow@elico-corp.com>
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
from openerp import SUPERUSER_ID
from openerp.osv import fields,osv
import time

class wkf_tracking_product(osv.osv):
    _name     = 'wkf.tracking.product'
    _inherits = {'wkf.tracking': 'tracking_id'}
    
    def _get_product_id(self, cr, uid, ids, fields, arg=None, context=None):
        res = {}
        for data in self.read(cr, uid, ids, ['res_id']):
            res[data['id']] = data['res_id']
        return res
    
    _columns={
        'tracking_id': fields.many2one('wkf.tracking',"Tracking",),
        'product_id':  fields.function(_get_product_id, type='many2one', store=True, relation='product.product', string="Product"),
    }

wkf_tracking_product()



class product_product(osv.osv):
    _inherit = 'product.product'
    _name    = 'product.product'
    
    _columns={
        'wkf_tracking_ids': fields.one2many('wkf.tracking.product', 'product_id', 'Status Record'),
    }
    
    
    def write(self, cr, uid, ids, vals, context=None):
        track_pool = self.pool.get('wkf.tracking.product')
        dic        = dict(self._columns['state'].selection)
        to_state   = vals.get('state', False)
        to_state   = to_state and dic[to_state] or False
        now        = time.strftime('%Y-%m-%d %H:%M:%S')
        
        if to_state:
            for p in self.browse(cr, uid, ids):
                from_state = dic[p.state]
                if from_state != to_state:
                    name = p.code and '[%s] %s' % (p.code, p.name) or p.name
                    track_pool.create(cr, SUPERUSER_ID, {
                        'name':     name,
                        'res_type': 'product.product',
                        'res_id':   p.id,
                        'act_from': from_state,
                        'act_to':   to_state,
                        'act_time': now,  
                        'user_id':  uid,
                    })
        return super(product_product, self).write(cr, uid, ids, vals, context=context)

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
