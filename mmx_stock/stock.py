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
from openerp.osv import osv
from openerp.tools.translate import _


class stock_inventory(osv.osv):
    _inherit = 'stock.inventory'
    _name = 'stock.inventory'
    _defaults = {
    }
stock_inventory()


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def onchange_move_type(self, cr, uid, ids, type, context=None):
        """
        the standard OE of this function,the location is come
        from a fixed xml_id, not suit multi company
        """
        user_pool = self.pool.get('res.users')
        location_pool = self.pool.get('stock.location')

        me = user_pool.browse(cr, uid, uid)
        partner = me.company_id.partner_id
        internal_location = location_pool.search(
            cr, uid, [('company_id', '=', me.company_id.id),
                      ('usage', '=', 'internal'),
                      ('name', 'ilike', 'stock'), ])

        location_source_id = False
        location_dest_id = False

        if type == 'in':
            location_source_id = (partner.property_stock_supplier
                                  and partner.property_stock_supplier.id
                                  or False)
            location_dest_id = (internal_location
                                and internal_location[0]
                                or False)
        elif type == 'out':
            location_source_id = (internal_location
                                  and internal_location[0]
                                  or False)
            location_dest_id = (partner.property_stock_customer
                                and partner.property_stock_customer.id
                                or False)

        return {'value': {'location_id': location_source_id,
                          'location_dest_id': location_dest_id}}

    def call_picking_partial(self, cr, uid, ids, type, context=None):

        assert len(ids) == 1
        move_id = ids[0]

        if context is None:
            context = {}

        move = self.browse(cr, uid, move_id, context=context)
        picking_id = move.picking_id

        if (picking_id
                and picking_id.move_lines
                and len(picking_id.move_lines)) == 1:
            context.update({'active_model': 'stock.picking',
                            'active_ids': [picking_id.id, ],
                            'active_id': picking_id.id})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Configure your Company',
                'res_model': 'stock.partial.picking',
                'view_mode': 'form',
                'context': context,
                'target': 'new',
            }
        else:
            raise osv.except_osv(
                _('Error!'),
                _("""
                    The stock move you are trying to process
                    cannot be processed from this menu.
                    Please go to Warehouse/Receive-Deliver
                    by Order and process IS/DO <%s>
                """ % (picking_id.name)))

stock_move()


class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

    def _get_default_location(self, cr, uid, context=None):
        company_id = self.pool.get('res.company')._company_default_get(
            cr, uid, 'stock.inventory', context=context),
        location_pool = self.pool.get('stock.location')
        ids = location_pool.search(
            cr, uid, [('company_id', '=', company_id),
                      ('usage', '=', 'internal'),
                      ('name', 'ilike', 'stock')])
        return ids and ids[0] or False

    _defaults = {
        'location_id': lambda self, cr, uid, c: self._get_default_location(
            cr, uid, context=c)
    }
stock_inventory_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
