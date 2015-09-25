    # -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Damiano Falsanisi <damiano.falsanisi@elico-corp.com>, Jon Chow <jon.chow@elico-corp.com>
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
import logging
logger = logging.getLogger(__name__)


class product_rank(osv.osv):
    _name = 'product.rank'
    
    _columns = {
        'name': fields.char('Ranking', size=32, required=True),
        'rank': fields.integer('Position',      required=True),
    }
    _sql_constraints=[
        ('rank_uniq', 'unique(rank)','This Position is already used, please choose another one.'),
        ('name_uniq', 'unique(name)','This Ranking is already used, please choose another one.'),
    ]

product_rank()



class product_race_ed (osv.osv):
    _name = 'product.race.ed' 
    
    def _get_race_ed_name(self, cr, uid, ids, fields_name, args=None, context=None):
        res = {}
        for ed in self.browse(cr, uid, ids, context=context):
            race_name  = ed.race_id.name
            year       = ed.year and str(ed.year) or ''
            fname      = ''.join([race_name, r' ', year])
            res[ed.id] = fname
        return res
    
    #===========================================================================
    # def name_get(self, cr, uid, ids, context=None):
    #     if not ids:
    #         return []
    #     res = []
    #     for record in self.browse(cr, uid, ids, context=context):
    #         res.append((record.id, record.fullname))
    #     return res
    #===========================================================================
    
    _columns = {
        'name':    fields.function(_get_race_ed_name, type='char',size=40, args=None, store=True, string='Race Edition'),
        'race_id': fields.many2one('product.race', 'Race', required=True, ondelete='restrict'),
        'year':    fields.integer('Year'),
    } 
    
product_race_ed()



class product_classification(osv.osv):
    _name  = 'product.classification'
    _order = 'rank_id'
    
    _columns = {
        # Jon , this obj  name filed is not required
        #'name':       fields.char('Name', size=3, required=False),  
        'rank_id':    fields.many2one('product.rank',  'Ranking', ondelete='restrict'),
        'model_id':   fields.many2one('product.model', 'Model',   ondelete='restrict'),
        'name':       fields.char('Car No', size=3, required=True),  # 3 digit
        'driver_ids': fields.many2many('product.driver', 'classification_driver_rel', 'classification_id', 'driver_id', 'Drivers', context={'full_name':True}),
        'race_ed_id': fields.many2one('product.race.ed', 'Race edition', ondelete='restrict'),
    }
    _defaults={
        #'name' : lambda self,cr,uid,context : self.pool.get('ir.sequence').get(cr, uid, 'product.classification')       
    }
    _sql_constraints=[
        ('carn_three_digit', 'CHECK(name < 1000)' ,'Car No must contain 3 digits. Eg: "456"'),
    ]
    
    
    def create(self, cr, uid, args=None, context=None):
        # if args has no model_id and race_id, we get its from context
        arg        = args or {}
        context    = context or {}
        race_ed_id = args.get('race_ed_id', context.get('race_ed_id', False))
        model_id   = args.get('model_id',   context.get('model_id',   False))
                
        args.update({'model_id':model_id, 'race_ed_id':race_ed_id })
        logger.debug("ARGS : %s"%(args))
        return super(product_classification, self).create(cr, uid, args, context=context)
    
    
#==============================================================================
#   #Jon  default search by fullname
#   def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
#       if not args:
#           args = []
#
#       if name:
#           ids = self.search(cr, user, [('name','ilike',name)] + args, limit=limit, context=context)
#       else:
#           ids = self.search(cr, user, args, limit=limit, context=context)
#
#       return self.name_get(cr, user, ids, context=context)
#==============================================================================

product_classification()  



class product_race_ed (osv.osv):
    _inherit = 'product.race.ed'
    _name    = 'product.race.ed'
    
    _columns = {
        'classification_ids': fields.one2many('product.classification', 'race_ed_id', 'Classifications'),
    }  

product_race_ed()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: