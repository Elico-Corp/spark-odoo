# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Chen Rong <chen.rong@elico-corp.com>
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
from openerp.osv import orm, fields, osv


class product_base_price(orm.Model):
    _inherit = 'product.template'

    def _check_permissions(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            if not i:
                continue
            group_obj = self.pool.get('res.groups')
            manager_ids = group_obj.search(cr, uid,
                                           [('name', '=', 'Purchase - Base price')])
            if not manager_ids:
                raise osv.expect_osv(
                    _('Warning'),
                    _("Can't find group: 'Purchase - Base price', maybe is deleted, Please contact administrator."))
            user_obj = self.pool.get('res.users')
            user = user_obj.browse(cr, uid, uid, context=context)
            group_ids = []
            for grp in user.groups_id:
                group_ids.append(grp.id)

            if manager_ids[0] in group_ids:
                res[i] = 'In'
            else:
                res[i] = 'No'

            return res

    _columns = {'base_price1': fields.float('Base Price 1 (USD)', digits=(12, 6)),
                'base_price2': fields.float('Base Price 2 (USD)', digits=(12, 6)),
                'user_permission': fields.function(_check_permissions,
                                                   type='char', readonly=True)
                }
