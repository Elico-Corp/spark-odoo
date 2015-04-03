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
from openerp import tools


class ProductLicensorReport(orm.Model):
    _name = 'product.licensor.report'
    _description = "Product Licensor Report"
    _table = 'product_licensor_report'
    _auto = False
    _columns = {
        'licensor_id': fields.many2one('res.partner', 'Licensor'),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_uom': fields.many2one(
            'product.uom', 'Reference Unit of Measure', required=True),
        'purchased_qty': fields.integer('Purchased quantity'),
    }

    # TODO
    _order = 'licensor_id desc'

    def init(self, cr):
        # deal with uom conversion
        tools.sql.drop_view_if_exists(cr, 'product_licensor_report')
        cr.execute("""
            create or replace view product_licensor_report
            as (
                select
                    (concat(l.id, pl.licensor_id))::integer as id,
                    pl.licensor_id as licensor_id,
                    l.product_id as product_id,
                    sum(l.product_qty/u.factor*u2.factor) as purchased_qty,
                    t.uom_id as product_uom
                from purchase_order_line l
                    left join product_licensor_rel pl on (
                        pl.product_id = l.product_id)
                    left join product_template t on (pl.product_id = t.id)
                    left join product_uom u on (u.id = l.product_uom)
                    left join product_uom u2 on (u2.id = t.uom_id)
                where
                    l.product_id in (
                        select distinct product_id from product_licensor_rel)
                group by
                    l.product_id,
                    pl.licensor_id,
                    t.uom_id,
                    l.id,
                    l.product_qty)
            """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
