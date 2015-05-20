# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
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
from openerp.osv import orm, fields


class WizardShipmentAssignSOL(orm.TransientModel):
    _name = 'wizard.shipment.assign.sol'
    _description = 'Fill in the sale order lines for the shipments.'

    _columns = {
        'sol_ids': fields.many2many(
            'sale.order.line', 'sale_order_line_group_rel',
            'wizard_id', 'sol_id', 'Sale order lines',
            domain=[
                ('product_id.state', '=', 'order'),
                ('so_state', 'in', ('wishlist', 'draft')),
                ('sale_shipment_id', '=', False)]),
    }

    def fields_get(self, cr, uid, fields=None, context=None):
        '''creating dynamic domain

        You can have active_id and active_model only when the act_window
        is created/returned by function.
        Please check the button related method.

        only display the sale order lines:
            - shipment is False,
            - so state is draft or wishlist
            - product state is order
            - the product is in the pre defined contained products
            of the shipment
        '''

        res = super(WizardShipmentAssignSOL, self).fields_get(
            cr, uid, fields, context)
        domain, product_ids, sol_ids = [], [], []
        # only apply on the specific model: sale shipment to be safe.
        if context.get('active_id') and \
                context.get('active_model') == 'sale.shipment':
            shipment_pool = self.pool['sale.shipment']
            shipment = shipment_pool.browse(
                cr, uid, context.get('active_id'), context=context)
            product_ids = [p.product_id.id
                           for p in shipment.contained_product_info_ids]
            sol_ids = [sol.id for sol in shipment.sol_ids]

            # empty the domain defining the product_id and sol_ids
            # because it's possible of duplication.
            domain = filter(lambda i: i[0] not in ('product_id', 'id'), domain)

            domain.append(('product_id', 'in', tuple(product_ids)))
            if sol_ids:
                domain.append(('id', 'not in', tuple(sol_ids)))
        if domain:
            res['sol_ids']['domain'].extend(domain)
        return res

    def shipment_assign_sol(self, cr, uid, ids, context=None):
        '''This method is used to assign the sale order lines to
        the sale shipment. It's used in the wizard'''
        assert ids, 'You should at least select one record.'
        wizard = self.browse(cr, uid, ids, context=context)[0]
        context = context or {}
        active_id = context.get('active_id', False)
        if not active_id:
            return False
        for sol in wizard.sol_ids:
            sol.write({
                'sale_shipment_id': active_id,
            }, context=context)
