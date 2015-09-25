# -*- coding: utf-8 -*-
#
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
#
from openerp.osv import fields, osv


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _default_location_destination(self, cr, uid, context=None):
        """Gets default address of partner for destination location
        @return: Address id or False
        """
        location_id = False
        if context is None:
            context = {}
        if context.get('move_line', []):
            if context['move_line'][0]:
                if isinstance(context['move_line'][0], (tuple, list)):
                    location_id = context['move_line'][0][2] and context[
                        'move_line'][0][2].get('location_dest_id', False)
                else:
                    move_list = self.pool.get('stock.move').read(
                        cr, uid, context['move_line'][0], ['location_dest_id'])
                    location_id = move_list and move_list[
                        'location_dest_id'][0] or False
        elif context.get('address_out_id', False):
            property_out = self.pool.get('res.partner').browse(
                cr, uid, context['address_out_id'], context).property_stock_customer
            location_id = property_out and property_out.id or False

        return location_id

    def _default_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        location_id = False
        if context is None:
            context = {}
        if context.get('move_line', []):
            try:
                location_id = context['move_line'][0][2]['location_id']
            except:
                pass
        elif context.get('address_in_id', False):
            part_obj_add = self.pool.get('res.partner').browse(
                cr, uid, context['address_in_id'], context=context)
            if part_obj_add:
                location_id = part_obj_add.property_stock_supplier.id

        return location_id

    _columns = {
        # string  Source location ->  From location
        'location_id': fields.many2one(
            'stock.location',
            'From Location',
            required=True,
            select=True,
            states={'done': [('readonly', True)]},
            help="""Sets a location if you produce at a fixed location
            This can be a partner location if you subcontract
            the manufacturing operations."""),
    }

    _defaults = {
        'location_id': lambda self, cr, uid, c: self._default_location_source(cr, uid,  context=c),
        'location_dest_id': lambda self, cr, uid, c: self._default_location_destination(cr, uid,  context=c),
    }

    def onchange_move_type(self, cr, uid, ids, type, context=None):
        return {}
stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
