# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaaas@elico-corp.com>
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
#

from osv import osv, fields


class sale_announcement_report_wizard(osv.osv_memory):
    _name = 'sale.announcement.report.wizard'
    _description = 'Sale Announcement Report Wizard'

    def _get_announcements(self, cr, uid, ids, id, arg, context=None):
        datas = {}
        active_ids = context.get('active_ids', [])
        for i in ids:
            datas[i] = str(active_ids)[1:-1]
        return datas

    _columns = {
        'partner_id': fields.many2one(
            'res.partner', 'Partner', required=True),
        'sale_announcement_ids': fields.function(
            _get_announcements, store=True, type='char',
            string='Announcement')
    }

    def print_report(self, cr, uid, ids, context=None):
        datas = {
            'model': 'sale.announcement.report.wizard',
            'ids': ids,
            'form': self.read(cr, uid, ids, context=context),
        }

        return {'type': 'ir.actions.report.xml',
                'report_name': 'sale_announcement_webkit',
                'datas': datas, 'nodestroy': True}
