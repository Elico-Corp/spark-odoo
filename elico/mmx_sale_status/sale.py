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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class sale_order(osv.osv):
    _inherit = 'sale.order'
    _name = 'sale.order'

    def confirm_check(self, cr, uid, ids, context=None):
        """
            1:Only if product is order state, can be confirmed sale order.
            2:SO-0  cart SO can not be confirm
        """
        for order in self.browse(cr, uid, ids):
            if order.state in ('cart'):
                raise osv.except_osv(_('Error!'),
                                     _('You can not confirm a %s SO' % order.state))

            for line in order.order_line:
                if line.product_id.state != 'order':
                    raise osv.except_osv(
                        _('Error!'),
                        _('You can not confirm a Sales Order with\
                        a product for which the state is not Order'))
                    return False
        return True

    def action_button_confirm_extend(self, cr, uid, ids, context=None):
        """
        open wizard, split the order,
        in the wizard,you can split order and comfirm
        """
        #sale_order = self.browse(cr, uid, ids[0])
        #states = [line.product_id.state for line in sale_order.order_line]
        need_wizard = True
        # alwansy pop the wizard

        if need_wizard:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sales Order'),
                'res_model': 'wizard.order.split',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'nodestroy': True,
            }
        #else:
        #    return self.action_button_confirm(cr, uid, ids, context=context)

sale_order()


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _name = 'sale.order.line'

    def _get_product_state(self, cr, uid, ids, fields,
                           arg=None, context=None):
        res = {}
        dic = dict(self.pool.get(
            'product.product')._columns['state'].selection)
        for sol in self.browse(cr, uid, ids):
            if sol.product_id.state in dic:
                res[sol.id] = dic[sol.product_id.state]
            else:
                res[sol.id] = 'N/A'
        return res

    def _get_sol_by_product(self, cr, uid, ids, context=None):
        return self.pool.get('sale.order.line').search(
            cr, uid, [('product_id', 'in', ids)])

    _columns = {
         #TODO, fix the function field, use relation and store and keep the state ==== product_state
        'product_state': fields.function(
            _get_product_state,
            arg=None,
            type='char',
            string='Product State',
            readonly=True,
            store={'product.product': (_get_sol_by_product, ['state', ], 20),
                   'sale.order.line': (lambda self, cr, uid, ids, ctx:
                                       ids, ['product_id'], 20),
                   }),
        'product_id': fields.many2one(
            'product.product',
            'Product',
            domain=[('sale_ok', '=', True),
                    ('state', 'in', ['private', 'catalogue',
                                     'preorder', 'order',])],
            change_default=True),
        'final_qty': fields.float(
            'Final QTY',
            digits_compute=dp.get_precision('Product UoS'),
            readonly=True,
            states={'draft': [('readonly', False)]}),
        'is_final_confirm': fields.boolean('F QTY Confirmed'),
        'is_process': fields.boolean('Processed'),
        'so_state': fields.selection([
            ('draft', 'Draft'),
            ('wishlist', 'Wishlist'),
            ], 'SO Status', track_visibility='onchange',
            help="", select=True),
    }

    _defaults = {
        'so_state': 'draft'
    }

    # def _auto_init(self, cr, context=None):
    #     super(sale_order_line, self)._auto_init(cr, context)
    #     # init product_state for old record
    #     sol_ids = self.search(cr, 1, [])
    #     dic = self._get_product_state(cr, 1, sol_ids, 'product_state')
    #     for sol_id in dic:
    #         cr.execute("""
    #         UPDATE sale_order_line SET product_state='%s' WHERE id=%s
    #         """ % (dic[sol_id], sol_id))

sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
