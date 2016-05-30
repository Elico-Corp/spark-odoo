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
from openerp import netsvc


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _name = 'purchase.order.line'

    _columns = {
        'job_number': fields.char('Job Number', size=32,),
    }
    _sql_constraints = [
        ('job_number_uniq', 'unique (job_number)',
         'The Job Number of the PO Line must be unique!'),
    ]

purchase_order_line()


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _name = 'purchase.order'


    def wkf_confirm_order(self, cr, uid, ids, context=None):
        result = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=None)
        product_obj = self.pool.get('product.product')
        pos = self.browse(cr, uid, ids, context=None)
        wkf_service = netsvc.LocalService("workflow")
        for po in pos:
            product_ids = [l.product_id for l in po.order_line]
            for product_id in product_ids:
                if product_id.state == 'preorder':
                    wkf_service.trg_validate(uid, 'product.product',
                                             product_id.id, 'approve', cr)
        return result

purchase_order()


class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'job_number': fields.related('purchase_line_id', 'job_number',
                                     type='char', string='Job Number'),

    }

stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
