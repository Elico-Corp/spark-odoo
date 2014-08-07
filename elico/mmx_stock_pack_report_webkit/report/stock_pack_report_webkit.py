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


class stock_pack_report_webkit(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
        super(stock_pack_report_webkit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'get_pack_objs': self._get_pack_objs,
            'get_product_desc': self._get_product_desc,
            'move_pool': self.pool.get('stock.move'),
            'get_pack_move': self._get_pack_move,
            'get_pack_net_weight': self._get_pack_net_weight,
        })

    def _get_pack_net_weight(self, cr, uid, pack):
        if not pack:
            return 0.0
        else:
            return sum([m.product_id.weight_net * m.product_qty for m in pack.move_ids])

    def _get_pack_move(self, cr, uid, pack_obj, picking_id):
        move_pool = self.pool.get('stock.move')
        if pack_obj:
            move_ids = move_pool.search(cr, uid, [('picking_id', '=', picking_id), ('tracking_id', '=', pack_obj.id)])
            return move_pool.browse(cr, uid, move_ids)
        else:
            move_ids = move_pool.search(cr, uid, [('picking_id', '=', picking_id), ('tracking_id', 'in', [None, False])])
            return move_pool.browse(cr, uid, move_ids)
    
    def _get_product_desc(self, move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc

    def _get_pack_objs(self, cr, uid, picking_obj, context=None):
        context = context or {}
        pack_objs = []
        if not picking_obj:
            return pack_objs
        else:
            move_pool = self.pool.get('stock.move')
            pack_pool = self.pool.get('stock.tracking')
  #           res_group: [{'__context': {'group_by': []},
  #           '__domain': [('tracking_id', '=', 6), ('picking_id', '=', 175)],
              # 'tracking_id': (6, u'000086'),
              # 'tracking_id_count': 1L}...]
            res_group = move_pool.read_group(cr, uid, [('picking_id', '=', picking_obj.id)], 
                                           ['tracking_id'], ['tracking_id'], context=context)

            for r in res_group:
                if r.get('tracking_id', None):
                    pack_obj = pack_pool.browse(cr, uid, r.get('tracking_id')[0], context=context)
                    pack_objs.append(pack_obj)
                else:
                    if None not in pack_objs:
                        pack_objs.append(None)
            return pack_objs

report_sxw.report_sxw(
    'report.stock.pack.report.webkit',
    'stock.picking.out',
    'addons/mmx_stock_pack_report_webkit/report/stock_pack_report_webkit.mako',
    parser=stock_pack_report_webkit)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
