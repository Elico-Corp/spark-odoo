# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
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


class sale_shipment_move_available_done(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
        super(sale_shipment_move_available_done, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time':            time,
            'cr':              cr,
            'uid':             uid,
            'sm_pool': self.pool.get('stock.move'),
            'int': int,
            'get_res_list': self._get_res_list,
            'get_unique_list_of_partner': self._get_unique_list_of_partner,
            'filter_partner_moves': self._filter_partner_moves
        })

    def merge_dict(self, list_of_dicts, to_merge_field='product_qty', filter_states=['done']):
        '''
            merging two dict with specify field. And filter the list depending on filter_states,
                 The dicts must has the same structure.

            [params]: list_of_dicts: the dicts to merge.
            [params]: to_merge_field: the field to be merged.
            [params]: filter_states: the state of the record to filter.
            [return]: a new list with dicts merged.
        '''
        #TODO check if the dicts have the same structure.
        #But normally it is the same
        length = len(list_of_dicts)
        res = []
        import pdb
        #can it be any better?
        for i in range(0, length):
            # pdb.set_trace()
            #filter the state
            if list_of_dicts[i].get('state') not in filter_states:
                list_of_dicts[i]['marked'] = True
                continue            
            #check if merged. Default is False
            if list_of_dicts[i].get('marked', False):
                continue

            for j in range(i+1, length):
                if list_of_dicts[j].get('state') not in filter_states:
                    list_of_dicts[j]['marked'] = True
                    continue   
                #can you feel the my pain?
                if list_of_dicts[i].get('product_name') == list_of_dicts[j].get('product_name') \
                    and list_of_dicts[i].get('partner_name') == list_of_dicts[j].get('partner_name'):
                    list_of_dicts[j]['marked'] = True #mark this dict, once is marked, it is repealed.
                    #merge the field
                    list_of_dicts[i][to_merge_field] += list_of_dicts[j].get(to_merge_field)
            res.append(list_of_dicts[i])
        return res

    def _get_res_list(self, cr, uid, move_ids, filter_states=['done'], context=None):
        '''
            [params]: move_ids: the move line obj of current shipment.
            [params]: filter_states: list of states used to be filter moves
            [return]: list of result needed in the report, sorted.
        '''
        raw_res = []
        qty_merged_res = []
        for move in move_ids:
            record = {}
            record['partner_name'] = move.picking_id and move.picking_id.sale_id \
                    and move.picking_id.sale_id.partner_id \
                    and move.picking_id.sale_id.partner_id.name or 'No Partner Name'
            record['product_qty'] = move.product_qty or 0
            record['product_id'] = move.product_id and move.product_id.id
            record['product_name'] = move.product_id and move.product_id.name or 'No Product Name'
            record['state'] = move.state
            raw_res.append(record)
        qty_merged_res = self.merge_dict(raw_res, filter_states=filter_states)
        # res = sorted(qty_merged_res, key=lambda k: k['partner_name'])
        return qty_merged_res

    def _get_unique_list_of_partner(self, list_of_dicts):
        '''
            [params]: list_of_dicts: pass
            [return]: return a list of partner_name
        '''
        partner_set = set([a.get('partner_name') for a in list_of_dicts])
        return list(partner_set)

    def _filter_partner_moves(self, list_of_dicts, partner_name):
        res = []
        for l in list_of_dicts:
            if l.get('partner_name') == partner_name:
                res.append(l)
        return res

report_sxw.report_sxw(
    'report.sale_shipment_move_done_webkit',
    'sale.shipment',
    'extra_addons/sale_shipment/report/sale_shipment_move_done.mako',
    parser=sale_shipment_move_available_done)

report_sxw.report_sxw(
    'report.sale_shipment_move_available_webkit',
    'sale.shipment',
    'extra_addons/sale_shipment/report/sale_shipment_move_available.mako',
    parser=sale_shipment_move_available_done)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
