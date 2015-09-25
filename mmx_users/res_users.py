##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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


class res_users(osv.osv):
    _inherit = 'res.users'
    _name    = 'res.users'
    
    #Jon when create a user,  the res.partner.company_id  is the same as the res.user.comany_id  and user_id =False
    def create(self, cr, uid, values, context=None):
        user_id      = super(res_users, self).create(cr, uid, values, context=context)
        user         = self.browse(cr, uid, user_id, context=None)
        user_company = user.company_id and user.company_id.id or False
        
        self.pool.get('res.partner').write(cr, uid, user.partner_id.id, {'company_id':user_company ,'user_id':False})
        return user_id

res_users()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: