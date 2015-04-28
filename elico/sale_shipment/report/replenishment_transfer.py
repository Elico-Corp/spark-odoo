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
import time
from openerp.report import report_sxw


class ReplenishmentTransferReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReplenishmentTransferReport, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'move_pool': self.pool['stock.move'],
            'shipment_pool': self.pool['sale.shipment'],
            'get_res': self._get_res,
            'get_sale_shipments': self._get_sale_shipments
        })

    def _get_sale_shipments(self, cr, uid, context=None):
        '''get shipments from active_ids in context'''
        shipments = []
        shipment_pool = self.pool['sale.shipment']
        wizard_pool = self.pool['wizard.replenishment.transfer']
        wizard_ids = context.get('active_ids')
        assert wizard_ids, 'Must select a record!'
        wizard = wizard_pool.browse(cr, uid, wizard_ids[0], context=context)
        shipment_ids = [int(shipment_id)
                        for shipment_id in wizard.shipment_ids.split(',')]
        shipments = shipment_pool.browse(
            cr, uid, shipment_ids, context=context)
        return shipments

    def _get_res(
            self, cr, uid, src_location_id, dest_location_id,
            shipment_id, context=None):
        '''Return (grouped product, grouped qty) from stock moves
        in one shipment.

        @param shipment_id: the id of the shipment to which the stock
            moves belong.'''
        move_pool = self.pool['stock.move']
        # only filter out the internal stock moves
        domain = [('location_id.usage', '=', 'internal'),
                  ('location_dest_id.usage', '=', 'internal'),
                  ('sale_shipment_id', '=', shipment_id)]
        if src_location_id:
            domain.append(('location_id', '=', src_location_id.id))
        if dest_location_id:
            domain.append(('location_dest_id', '=', dest_location_id.id))
        product_group = move_pool.read_group(
            cr, uid,
            domain,
            ['product_id', 'product_qty'], ['product_id'])
        return product_group

report_sxw.report_sxw(
    'report.sale_shipment_replenishment_transfer_webkit',
    'wizard.replenishment.transfer',
    'addons/sale_shipment/report/replenishment_transfer.mako',
    parser=ReplenishmentTransferReport,
    header=None)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
