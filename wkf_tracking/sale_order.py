
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

class wkf_tracking_sale(osv.osv):
    _name     = 'wkf.tracking.sale'
    _inherits = {'wkf.tracking': 'tracking_id'}
    
    def _get_SO_id(self, cr, uid, ids, fields, arg=None, context=None):
        res = {}
        for data in self.read(cr, uid, ids, ['res_id']):
            res[data['id']] = data['res_id']
        return res
    
    _columns={
        'tracking_id': fields.many2one('wkf.tracking',"Tracking",),
        'so_id':  fields.function(_get_SO_id, type='many2one', store=True, relation='sale.order', string="Sale Order"),
    }
wkf_tracking_sale()

class sale_order(osv.osv):
    _inherit='sale.order'
    _name='sale.order'
    _columns={
        'wkf_tracking_ids': fields.one2many('wkf.tracking.sale', 'so_id', 'Status Record'),
    }
    def write(self, cr, uid, ids, vals, context=None):
        track_pool = self.pool.get('wkf.tracking.sale')
        dic        = dict(self._columns['state'].selection)
        to_state   = vals.get('state', False)
        to_state   = to_state and dic[to_state] or False
        now        = time.strftime('%Y-%m-%d %H:%M:%S')
        
        if to_state:
            for so in self.browse(cr, uid, ids):
                from_state = dic[so.state]
                if from_state != to_state:
                    track_pool.create(cr, SUPERUSER_ID, {
                        'name':     so.name,
                        'res_type': sale_order._name,
                        'res_id':   so.id,
                        'act_from': from_state,
                        'act_to':   to_state,
                        'act_time': now,  
                        'user_id':  uid,
                    })
        return super(sale_order, self).write(cr, uid, ids, vals, context=context)
    
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: