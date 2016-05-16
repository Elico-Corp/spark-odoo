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
import openerp.exceptions
import time



class product_product (osv.osv):
    _inherit = 'product.product'
    _name    = 'product.product'
    
    def _get_is_racing(self, cr, uid, ids, fields, arg, context=None):
        """ Return whether the product is a car or not """
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            categ     = product.categ_id
            is_racing = False
            
            while not is_racing and categ:
                if 'racing' in categ.name.lower():
                    is_racing = True
                categ = categ.parent_id or False    
            res[product.id] = is_racing
        return res
    
    
    _columns = {
        # default_code  required = True
        'default_code':         fields.char('Internal Reference',  size=64,    select=True, required=True),
        'brand_id':             fields.many2one('product.brand',   'Brand',    ondelete='restrict'),
        'archive_id':           fields.many2one('product.archive', 'Location', ondelete='restrict'),
        'scale_id':             fields.many2one('product.scale',   'Scale',    ondelete='restrict', required=True),
        
        'model_id':             fields.many2one('product.model', 'Model', ondelete='restrict', required=True),
        'model_year':           fields.char('Model Year', size=4),
        'manufacturer_id':      fields.related('model_id', 'manufacturer_id', type='many2one', relation='product.manufacturer', string='Manufacturer', readonly=True),
        'year':                 fields.integer('Catalogue Year'),
        'race_ed_id':           fields.many2one('product.race.ed', 'Race Edition', required=True),
        
        'classification_id':    fields.many2one('product.classification', 'Car No', domain="[('race_ed_id','=',race_ed_id)]"),
        
        'rank_id':              fields.related('classification_id', 'rank_id',    type='many2one', relation='product.rank',   string='Ranking', readonly=True),  
        'driver_ids':           fields.related('classification_id', 'driver_ids', type='many2many',relation='product.driver', string='Drivers', readonly=True),
        
        'archive_id':           fields.many2one('product.archive', 'Archive Location',  ondelete='restrict'),
        'color_ids':            fields.many2many('product.color',  'product_color_rel', 'product_id', 'color_id', 'Color'),
        'notes':                fields.char('Notes', size=200, help='Other information related to products that will appear in product sales description'),
        
        'is_racing':            fields.function(_get_is_racing, type='boolean', string='Is Racing ?', store=True),
        'dev_status_id':        fields.many2one('product.dev.status', 'Development Status'),
        'dbox_approve':         fields.boolean('Display Box Approved'),
        'catalogue_extra_info': fields.char('Catalogue extra info', size=64),
        
        'hs_code':              fields.char('HS Code',size=32),
        'customs_description':  fields.char('Customs description', size=64),
        'availability_date':    fields.date('Availability Date'), 
        'do_not_allow_checkout': fields.boolean('Not allow to checkout'),
        'create_date': fields.datetime('Creation date', readonly=True),
    }

    def _default_has_default_scale_id(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        try:
            scale_id = ir_model_data.get_object_reference(cr, uid, 'product', 'product_scale_default')[1]
        except ValueError:
            scale_id = False
        return scale_id

    def _default_has_default_model_id(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        try:
            model_id = ir_model_data.get_object_reference(cr, uid, 'product', 'product_model_default')[1]
        except ValueError:
            model_id = False
        return model_id

    def _default_has_default_race_ed_id(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        try:
            race_ed_id = ir_model_data.get_object_reference(cr, uid, 'product', 'product_race_ed_id_default')[1]
        except ValueError:
            race_ed_id = False
        return race_ed_id

    _defaults={
        'year': lambda *a:  None,
        'company_id':lambda *a: None,
        'model_id': _default_has_default_model_id,
        'scale_id': _default_has_default_scale_id,
        'race_ed_id': _default_has_default_race_ed_id,
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        default_code is unique and required, so when copy, 
        set the it to origin default_code + [new product_id]        
        """
        default.update({'default_code': str(time.time()), }) #tmp value str time avoid unique 
        res = super(product_product, self).copy(cr, uid, id, default, context=context)
        
        if res:
            old_product=self.browse(cr,uid,id)
            old_code=old_product.default_code 
            if old_code:
                indx=old_code.find('[')
                if indx > -1:
                    old_code=old_code[:indx]
                new_code=old_code + '[' + str(res) + ']'
            else:
                new_code='[' + str(res) + ']'
            
            self.write(cr,uid,res,{'default_code':new_code })
        return res
    
    # Don't check EAN13 ,   jon.chow<@>elico-corp.com    May 17, 2013 
    def _check_ean_key(self, cr, uid, ids, context=None):
        return True
    
    _constraints     = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]
    
    _sql_constraints = [('default_code_unique', 'unique(default_code)','Reference code to be unique')]
    
    
    def onchange_classification_id(self, cr, uid, ids, classification_id=None):
        if classification_id:
            classification = self.pool.get('product.classification').browse(cr, uid, classification_id)
            driver_ids     = [d.id for d in classification.driver_ids]
            return {'value': {'rank_id':classification.rank_id and classification.rank_id.id, 'driver_ids':driver_ids}}
        else:
            return {'value': {'rank_id':False, 'driver_ids':False}}
    
    
    def generation_sale_description(self, cr, uid, ids, context=None):
        """ Button which Generates the Sales description """
        SP = ' '
        NL = '\n'  
        ES = ''
        
        for product in self.browse(cr, uid, ids, context=context):
            car_no         = product.classification_id and r'#' + str(product.classification_id.name) or ES
            model_fullname = product.model_id   and product.model_id.fullname or ES
            rank           = product.rank_id    and product.rank_id.name or ES
            race_ed        = product.race_ed_id and product.race_ed_id.name or ES
            notes          = product.notes      and NL + product.notes or ES 
            model_year     = product.model_id   and product.model_year or ES
            drivers        = product.driver_ids and NL + SP.join([d.fullname for d in product.driver_ids]) or ES
            colors         = product.color_ids  and SP.join([color.name for color in product.color_ids]) or ES
            
            if product.is_racing:
                description_sale = ''.join([model_fullname, SP, car_no, SP, model_year, SP, rank, SP, race_ed, drivers, notes])
            else:
                description_sale = ''.join([model_fullname, SP, model_year, SP, colors, drivers, notes])
            
            return self.write(cr, uid, ids, {'description_sale': description_sale}, context=context)
    
    
    def onchange_categ_id(self, cr, uid, ids, categ_id):
        #Jon:0411 when change category not car, set some fields relation car to False
        result = {}
        if categ_id:
            categ = self.pool.get('product.category').browse(cr, uid, categ_id)
            if 'racing' not in categ.complete_name.lower():
                result['classification_id'] = False
                #result['model_id']          = False
                result['description_sale']  = False
                result['is_racing']         = False
            else:
                result['is_racing'] = True
            return {'value': result}
        return {}

product_product()



class product_template(osv.osv):
    _inherit = 'product.template'
    _name    = 'product.template'
    
    _defaults = {
        # mmx product default company_id  is None
        # 'company_id':lambda *a: False,
    }

product_template()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: