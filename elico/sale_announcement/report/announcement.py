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
import time
from openerp.report import report_sxw


class sale_announcement(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_announcement, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time':            time,
            'cr':              cr,
            'uid':             uid,
            'announcement_pool': self.pool.get('sale.announcement'),
            'pricelist_pool': self.pool.get('product.pricelist')
        })


report_sxw.report_sxw(
    'report.sale_announcement_webkit',
    'sale.announcement.report.wizard',
    'extra_addons/sale_announcement/report/sale_announcement.mako',
    parser=sale_announcement,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
