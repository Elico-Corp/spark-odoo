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

from openerp.osv import fields, osv


class product_product(osv.osv):
    _inherit = 'product.product'
    _name = 'product.product'

    _state_list = [
        ('draft', 'Draft'),
        ('private', 'Development'),
        ('catalogue', 'Catalogue'),
        ('preorder', 'Announcement'),
        ('order', 'Order'),
        ('solded', 'Sold Out'),
        ('done', 'Done'),
    ]

    _mmx_type_list = [
        ('oem', 'OEM'),
        ('regular', 'Regular'),
        ('limited_edition', 'Limited Edition'),
    ]

    _columns = {
        'state': fields.selection(_state_list, 'Status'),
        'mmx_type': fields.selection(_mmx_type_list, 'MMX Type',
                                     required=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'mmx_type': lambda *a: 'oem',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        default.update({
            'state': 'draft',
        })
        return super(product_product, self).copy(cr, uid, id, default,
                                                 context=context)


product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
