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


class WizardReplenishmentTransfer(orm.TransientModel):
    _name = 'wizard.replenishment.transfer'

    def _get_shipment_ids(self, cr, uid, ids, fields, arg, context=None):
        '''get shipments from active_ids in context'''
        datas = {}
        active_ids = context.get('active_ids', [])
        for i in ids:
            datas[i] = str(active_ids)[1:-1]
        return datas

    _columns = {
        'src_location_id': fields.many2one(
            'stock.location', 'Source location',
            domain=[('usage', '=', 'internal')]),
        'dest_location_id': fields.many2one(
            'stock.location', 'Destination location',
            ),
        'shipment_ids': fields.function(
            _get_shipment_ids, store=True, type='char',
            string='Shipments')
    }

    def print_report(self, cr, uid, ids, context=None):
        '''Print the replenishment transfer webkit report'''
        assert ids, 'This method need ids!'
        datas = {
            'model': 'wizard.replenishment.transfer',
            'ids': ids,
            'form': self.read(cr, uid, ids, context=context),
        }

        return {'type': 'ir.actions.report.xml',
                'report_name': 'sale_shipment_replenishment_transfer_webkit',
                'datas': datas, 'nodestroy': True}
