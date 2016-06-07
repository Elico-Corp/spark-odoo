# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.osv import orm


class report_sale_shipment(orm.Model):
    _inherit = 'sale.shipment'

    # override list in custom module to add/drop columns or change order
    def _report_xls_fields(self, cr, uid, context=None):
        return [
            'product_default_code', 'order_partner_id', 'order_partner_id',
        ]

    # Change/Add Template entries
    def _report_xls_template(self, cr, uid, context=None):
        return {}
