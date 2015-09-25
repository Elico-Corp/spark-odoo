# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Andy Lu <andy.lu@elico-corp.com>
#            Alex Duan<alex.duan@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it wil    l be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def product_id_change(self, cr, uid, ids, product, location_id,
                          location_dest_id, date_expected, context=None):
        '''This method if only used in the quick internal move creation form
        when the field product_id changes.

        The standard method is not overwritten.
        '''
        context = context or {}
        result = {}
        if product:
            product_obj = self.pool['product.product'].browse(
                cr, uid, product, context=context)
            result = {
                'name': product_obj.name,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'date_expected': date_expected
            }
            if product_obj.uom_id:
                result['product_uom'] = product_obj.uom_id.id
        return {'value': result}


class StockPicking(orm.Model):
    _inherit = 'stock.picking'
    _columns = {
        'min_date': fields.datetime('Min date'),
    }

    _defaults = {
        'min_date': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
