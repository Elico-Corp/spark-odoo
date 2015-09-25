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

from openerp.osv import fields,osv


class  purchase_order_line(osv.osv):
    _inherit='purchase.order.line'
    def _get_pdt_mmx_type(self,cr,uid,ids,field,arg=None,context=None):
        res={}
        dic=dict(self.pool.get('product.product')._columns['mmx_type'].selection)
        
        for line in self.browse(cr,uid,ids):
            res[line.id]=dic[ line.product_id.mmx_type ]
        return res 
    _columns={
        'product_mmx_type':fields.function(_get_pdt_mmx_type,arg=None, string='Product Type', type='char',size=32,readonly=True,store=True),
    }
    def link_to_order(self,cr,uid,ids,context=None):
        pol=self.browse(cr,uid,ids[0])
        po_id=pol.order_id.id
        return {
              'name': 'Purchase Order',
              'target':"new",
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'purchase.order',
              'res_id': po_id,
              'type': 'ir.actions.act_window',
        }
purchase_order_line()


    

