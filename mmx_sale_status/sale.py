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
        need_wizard = True

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

    def _get_sale_order_lines(self, cr, uid, ids, context=None):
        so_pool = self.pool['sale.order']
        res = []
        for so in so_pool.browse(cr, uid, ids, context=context):
            res.extend([line.id for line in so.order_line])
        return res

    def _get_so_state_selection(self, cr, uid, context=None):
        return self.pool['sale.order']._columns.get('state').selection

    _columns = {
        # TODO, fix the function field, use relation
        # and store and keep the state ==== product_state
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
                                     'preorder', 'order'])],
            change_default=True),
        'final_qty': fields.float(
            'Final QTY',
            digits_compute=dp.get_precision('Product UoS'),
            readonly=True,
            states={
                'draft': [('readonly', False)],
                'wishlist': [('readonly', False)]}),
        'is_final_confirm': fields.boolean('F QTY Confirmed'),
        'is_process': fields.boolean('Processed'),
        'so_state': fields.related(
            'order_id', 'state', string="SO Status",
            selection=_get_so_state_selection,
            type="selection", store={
                'sale.order': (_get_sale_order_lines, ['state'], 10)
            }),
    }

    _defaults = {
        'so_state': 'draft'
    }
    # remove the final_qty < product_qty constraint in the database
    # keep this constraint aways pass
    _sql_constraints = {
        ('final_qty_valid', 'CHECK (1>0)',
            'Final quantity should not be a negative value!')
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
