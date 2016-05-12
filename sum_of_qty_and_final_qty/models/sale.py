# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, osv


class sale_order(osv.osv):
    _inherit = 'sale.order'
    _name = 'sale.order'

    def _quotation_line_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for sol in self.browse(cr, uid, ids, context=context):
            res[sol.id] = len(sol.order_line)
        return res

    _columns = {
        'quotation_line_count': fields.function(
            _quotation_line_count, string='Quotation Line Count',
            type='integer')
    }
