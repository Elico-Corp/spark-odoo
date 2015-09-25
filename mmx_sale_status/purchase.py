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


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _name = 'purchase.order.line'

    def _get_product_state(self, cr, uid, ids, fields, arg=None, context=None):
        res = {}
        dic = dict(self.pool.get(
            'product.product')._columns['state'].selection)

        for sol in self.browse(cr, uid, ids):
            if sol.product_id.state in dic:
                res[sol.id] = dic[sol.product_id.state]
            else:
                res[sol.id] = 'N/A'
        return res

    def _get_pol_by_product(self, cr, uid, ids, context=None):
        return self.pool.get('purchase.order.line').search(
            cr, uid, [('product_id', 'in', ids)])

    _columns = {
        'product_state': fields.function(
            _get_product_state,
            arg=None,
            type='char',
            string='Product State',
            readonly=True,
            store={'product.product': (_get_pol_by_product,
                                       ['state', ], 20),
                   'purchase.order.line': (lambda self, cr, uid, ids, ctx:
                                           ids, ['product_id'], 20),
                   }),
    }

purchase_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
