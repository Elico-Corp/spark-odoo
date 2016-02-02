# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv


class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _name = 'stock.picking'

    def _stock_move_lines_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = len(line.move_lines)
        return res

    _columns = {
        'stock_move_lines_count': fields.function(
            _stock_move_lines_count, string='Stock Move Line Count',
            type='integer'),
    }


class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    _name = 'stock.picking.out'

    def _stock_move_lines_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = len(line.move_lines)
        return res

    _columns = {
        'stock_move_lines_count': fields.function(
            _stock_move_lines_count, string='Stock Move Line Count',
            type='integer'),
    }


class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'
    _name = 'stock.picking.in'

    def _stock_move_lines_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = len(line.move_lines)
        return res

    _columns = {
        'stock_move_lines_count': fields.function(
            _stock_move_lines_count, string='Stock Move Line Count',
            type='integer'),
    }
