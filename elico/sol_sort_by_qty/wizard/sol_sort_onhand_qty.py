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

from openerp.osv import fields, osv
import operator 

class sol_sort_onhand_qty(osv.osv_memory):
    _name = 'sol.sort.onhand_qty'
    _columns = {
        'name': fields.char('name', size=32),
    }
    def action_sort(self, cr, uid, ids, context=None):
        """
        SOL sort by onhand qty, write the int(product qty) to sequence.
        """
        sol_pool = self.pool.get('sale.order.line')
        sol_ids = sol_pool.search(cr,uid,[('order_id.state','in',['draft','sent'])],context=context)
        sols = sol_pool.browse(cr, uid, sol_ids, context=context)
        
        dic = {} #{product_id:  (onhand_qty, [sol_ids])}
        for line in sols:
            if line.product_id.id in dic:
                dic[line.product_id.id][1].append(line.id ) 
            else:
                dic.update({line.product_id.id:(int(line.product_id.qty_available),[line.id,])})
        for pid in dic:
            sol_pool.write(cr, uid, dic[pid][1], {'sequence': dic[pid][0] })
        return True


 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
 