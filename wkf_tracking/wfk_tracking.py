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
from openerp import SUPERUSER_ID
from openerp.osv import fields,osv
import time

class wkf_tracking(osv.osv):
    ''' Reorder of OE object work follow info 
    '''
    _name = 'wkf.tracking'
    _columns={
        'name'     : fields.char('Name',  size=32),
        'res_type' : fields.char('Model', size=32,  required=True, select=1),
        'res_id'   : fields.integer('Resource ID',  required=True),
        'act_from' : fields.char('From',  size=32,  required=True),
        'act_to'   : fields.char('To',    size=32,  required=True),
        'act_time' : fields.datetime('Action Time', required=True),
        'user_id'  : fields.many2one('res.users', 'User', select=1, required=True),
    }
    
    def create(self, cr, uid, values, context=None):
        # wkf.tracking record is create by  system manager, not really user
        return super(wkf_tracking, self).create(cr, SUPERUSER_ID, values, context=context)

wkf_tracking()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: