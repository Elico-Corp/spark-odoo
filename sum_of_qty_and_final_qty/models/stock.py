# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields


class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _name = 'stock.picking'

    def _stock_picking_line_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for spl in self.browse(cr, uid, ids, context=context):
            res[spl.id] = len(spl.move_lines)
        return res

    _columns = {
        'stock_picking_line_count': fields.function(
            _stock_picking_line_count, string='Internal Move Line Count',
            type='integer')
    }


class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    _name = 'stock.picking.out'

    def _stock_picking_line_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for spl in self.browse(cr, uid, ids, context=context):
            res[spl.id] = len(spl.move_lines)
        return res

    _columns = {
        'stock_picking_line_count': fields.function(
            _stock_picking_line_count, string='Delivery Order Line Count',
            type='integer')
    }


class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'
    _name = 'stock.picking.in'

    def _stock_picking_line_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for spl in self.browse(cr, uid, ids, context=context):
            res[spl.id] = len(spl.move_lines)
        return res

    _columns = {
        'stock_picking_line_count': fields.function(
            _stock_picking_line_count, string='Imcoming Shipments Line Count',
            type='integer')
    }
