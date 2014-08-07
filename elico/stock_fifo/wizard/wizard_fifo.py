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
from openerp.tools.translate import _
from openerp import netsvc
wf_service = netsvc.LocalService('workflow')

class wizard_fifo(osv.osv_memory):
    _name = 'wizard.fifo'
    _columns = {
        'name': fields.char('name', size=32),
        're_check_confirm': fields.boolean('Reset Stock Move to confirm before assign'),
    }
    _defaults = {
        're_check_confirm' :lambda *a:True,
    }
    def action(self, cr, uid, ids, context=None):
        picking_pool = self.pool.get('stock.picking')
        
        move_pool = self.pool.get('stock.move')
        wizard = self.browse(cr,uid, ids[0])
        
        if wizard.re_check_confirm:
            assigned_ids =  move_pool.search(cr, uid, [('state','=','assigned')], context=context)
            move_pool.action_confirm(cr, uid, assigned_ids, context=context)
         
        #order by field "id", so which move first created will first delivery
        confirmed_ids = move_pool.search(cr, uid, [('state','=','confirmed')], order='id', context=context)

        move_pool.action_assign(cr, uid, confirmed_ids)
        return True

 # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
  