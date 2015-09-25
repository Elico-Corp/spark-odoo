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

import time
from openerp.report import report_sxw
from openerp import pooler


class delivery_pack(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(delivery_pack, self).__init__(cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'get_tracking': self._get_tracking,
            'get_total_tacking': self._get_total_tacking,
            'get_measurement': self._get_measurement,
            'get_cbm': self._get_cbm,
            'get_product_description': self._get_product_description,
            'get_tatal_no_tracking': self._get_tatal_no_tracking,
            'partner': self._get_partner(cr, uid, context),
        })

    @classmethod
    def get_header_by_partner(cls, cr, uid, ids):
        picking_id = ids[0]
        header_name = 'external portrait'
        picking_obj = pooler.get_pool(cr.dbname).get('stock.picking')
        picking = picking_obj.browse(cr, uid, picking_id)
        return (picking.partner_id.header_id
                and picking.partner_id.header_id.name
                or header_name)

    @classmethod
    def get_webkit_header_by_partner(cls, cr, uid, ids):
        picking_id = ids[0]
        picking_obj = pooler.get_pool(cr.dbname).get('stock.picking')
        picking = picking_obj.browse(cr, uid, picking_id)
        return picking.partner_id.header_webkit or None

    def _get_partner(self, cr, uid, context):
        return self.pool.get('stock.picking.out').browse(
            cr, uid, context.get('active_id', False)).partner_id

    def _get_tracking(self, picking_id):
        res = {}
        picking = self.pool.get('stock.picking').browse(self.cr, self.uid,
                                                        picking_id)

        for move in picking.move_lines:
            tracking = move.tracking_id
            if tracking:
                if tracking.id in res:
                    res[tracking.id]['moves'].append(move)
                else:
                    res.update({tracking.id: {'tracking': tracking,
                                              'moves': [move]}})
            else:
                if False in res:
                    res[tracking.id]['moves'].append(move)
                else:
                    res.update({False: {'tracking': False, 'moves': [move]}})
        return res

    def _get_tatal_no_tracking(self, moves):
        return

    def _get_total_tacking(self, tracking_id):
        tracking = self.pool.get('stock.tracking').browse(
            self.cr, self.uid, tracking_id)
        return sum([line.product_qty for line in tracking.move_ids])

    def _get_measurement(self, tracking_id):
        tracking = self.pool.get('stock.tracking').browse(
            self.cr, self.uid, tracking_id)
        return r'*'.join(
            [str(tracking.pack_h),
             str(tracking.pack_w),
             str(tracking.pack_l)])

    def _get_cbm(self, tracking_id):
        tracking = self.pool.get('stock.tracking').browse(self.cr, self.uid,
                                                          tracking_id)
        cbm = tracking.pack_h * tracking.pack_w * tracking.pack_l
        return cbm and cbm/1000000.0 or 0.0

    def _get_product_description(self, product_id):
        product = self.pool.get('product.product').browse(self.cr, self.uid,
                                                          product_id)
        br_start = r'<br>'
        br_end = r'</br>'

        default_code = (product.default_code and
                        '[' + product.default_code + ']'
                        or '')
        hs_code = (product.hs_code
                   and br_start + 'HS Code:' + product.hs_code + br_end
                   or '')
        customs_description = (product.customs_description
                               and product.customs_description
                               or '')

        return ''.join([default_code, customs_description, hs_code, ])

report_sxw.report_sxw('report.webkit_delivery_pack',
                      'stock.picking.out',
                      'extra_addons/mmx_stock/report/delivery_pack.mako',
                      parser=delivery_pack,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
