# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _name = 'purchase.order'

    def _purchase_order_line_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pol in self.browse(cr, uid, ids, context=context):
            res[pol.id] = len(pol.order_line)
        return res

    _columns = {
        'purchase_order_line_count': fields.function(
            _purchase_order_line_count, string='Purchase Order Line Count',
            type='integer'),
    }
