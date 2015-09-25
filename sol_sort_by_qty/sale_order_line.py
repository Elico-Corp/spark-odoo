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

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    #Alex Duan 2014-3-17 sorted by onhand QTY. change field: qty_available to store=True
    _order = 'qty_available desc, sequence desc, order_id desc, id'
    
    def _get_qty_available(self, cr, uid, ids, field_name, args, context=None):
        if not ids:
            return
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        res = {}
        for sol in self.browse(cr, uid, ids, context):
            res[sol.id] = sol.product_id.qty_available or 0.0
        return res
       
    _columns={
            'qty_available': fields.function(_get_qty_available, 
                type="float",
                string='Quantity On Hand',
                store = True
                ),
            # 'qty_available': fields.related('product_id', 'qty_available', 
            #     type='float', string='Quantity On Hand', store=True)
    }

    def _generate_order_by(self, order_spec, query):
        '''
            rewrite the orm method, this can let null last when is desc order,
            and the field is qty_available.
            once the official changes return, this method may crash.
        '''
        function_attrs = super(sale_order_line, self)._columns
        res = super(sale_order_line, self)._generate_order_by(order_spec, query)
        if res.count('qty_available'):
            splited_res = res.split(',')
            for i, r in enumerate(splited_res):
                if r and r.count('desc') and r.count('qty_available'):
                    splited_res[i] = r + ' NULLS LAST '
            res = ','.join(splited_res)
        return res

    

        
        
        
        
        
        
        

 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
  