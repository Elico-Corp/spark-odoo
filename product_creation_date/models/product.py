# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp.osv import orm, fields


class product_product(orm.Model):
    _name = "product.product"
    _inherit = 'product.product'
    _columns = {
        'create_date': fields.datetime('Created date', readonly=True),
    }
