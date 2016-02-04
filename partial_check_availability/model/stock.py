# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields


class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _name = 'stock.picking'

    def _get_picking_status_all_available(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids):
            for line in pick.move_lines:
                if line.state != "assigned":
                    res[pick.id] = False
                    break
                res[pick.id] = True
        return res
    _columns = {
        'picking_status_all_available': fields.function(_get_picking_status_all_available, type='boolean', string='Pack Operation Exists?', help='technical field for attrs in view'),
    }


class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    _name = 'stock.picking.out'

    def _get_picking_status_all_available(self, cr, uid, ids, field_name, arg, context=None):

        res = {}
        for pick in self.browse(cr, uid, ids):
            for line in pick.move_lines:
                if line.state != "assigned":
                    res[pick.id] = False
                    break
            res[pick.id] = True
        return res
    _columns = {
        'picking_status_all_available': fields.function(_get_picking_status_all_available, type='boolean', string='Pack Operation Exists?', help='technical field for attrs in view'),     

    }


class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'
    _name = 'stock.picking.in'

    def _get_picking_status_all_available(self, cr, uid, ids, field_name, arg, context=None):

        res = {}
        for pick in self.browse(cr, uid, ids):
            for line in pick.move_lines:
                if line.state != "assigned":
                    res[pick.id] = False
                    break
            res[pick.id] = True
        return res
    _columns = {
        'picking_status_all_available': fields.function(_get_picking_status_all_available, type='boolean', string='Pack Operation Exists?', help='technical field for attrs in view'),     

    }
