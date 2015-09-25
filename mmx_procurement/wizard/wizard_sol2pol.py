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

import threading, time
from openerp.osv import fields,osv
from openerp import pooler
from openerp.tools.translate import _
from openerp import netsvc
import logging
logger = logging.getLogger(__name__)



class  wizard_sol2pol(osv.osv_memory):
    _name = 'wizard.sol2pol'
    
    _columns = {
        'name':         fields.char('name', size=32),
        'company_id':   fields.many2one('res.company', 'Company'),
        'so_ids':       fields.many2many('sale.order', 'rel_wizard_so', 'wizard_id', 'so_id', 'Sale Orders'),
        'filter_model': fields.selection([('nothing','None'),('select','Select SOL'),('order','By Orders'),('company','Companies')], string='Filter Model'),
    }
    _defaults = {
        'filter_model':lambda *a: 'nothing',
    }
    
    
    def change_filter_model(cr, uid, ids, filter_model):
        res = {}
        return 
        
    
    def  _run_mmx_schedule(self, cr, uid, ids, use_new_cursor=False, context=None):
        """ For new thread copy the cursor """
        try:
            if use_new_cursor:
                cr = pooler.get_db(use_new_cursor).cursor()
            
            #company_obj = self.pool.get('res.company')
            #company_ids = company_obj.search(cr, uid, [], order='sequence_mmx_schedule')
            #for company_id in company_ids:
            company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            self.schedule_company(cr, uid, company_id=company_id, context=context)
            if use_new_cursor:
                cr.commit()
        
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
    
    
    def run_mmx_schedule(self, cr, uid, ids, context=None):
        """ Fork a thread to run MMX scheduler """
        use_new_cursor       = cr.dbname
        threaded_calculation = threading.Thread(target=self._run_mmx_schedule, args=(cr, uid, ids, use_new_cursor, context))
        threaded_calculation.start()
        return {}
    
    
    def schedule_company(self,cr, uid,  company_id=None, context=None):
        """ company_id: res.company id
            according the POL, group by Product,  Create the Procurement 
        """
        new_procurement_ids = []
        wkf_service      = netsvc.LocalService("workflow")
        so_pool          = self.pool.get('sale.order')
        sol_pool         = self.pool.get('sale.order.line')
        po_pool          = self.pool.get('purchase.order')
        pol_pool         = self.pool.get('purchase.order.line')
        partner_pool     = self.pool.get('res.partner')
        product_pool     = self.pool.get('product.product')
        uom_pool         = self.pool.get('product.uom')
        pricelist_pool   = self.pool.get('product.pricelist')
        procurement_pool = self.pool.get('procurement.order')
        location_pool    = self.pool.get('stock.location')
        stock_move_pool  = self.pool.get('stock.move')
        today            = time.strftime('%Y-%-m-%d')
        user             = self.pool.get('res.users').browse(cr, 1, uid)
        
        # step 1  Search SO lines with no procurement, then linked them to an exist procurement or create new procurements
        # sol_ids = sol_pool.search(cr, uid, [('procurement_id','=',False),('company_id','=',company_id),('state','!=','cancel')],)
        # if only for Cart  AND so.state = 'cart';
        cr.execute(""" SELECT sol.id 
                       FROM sale_order_line AS sol
                       WHERE sol.procurement_id IS NULL
                         AND sol.company_id = %s
                         AND sol.state != 'cancel'; """,( company_id,))
        
        sol_ids    = [x[0] for x in cr.fetchall()]
        sale_lines = sol_pool.browse(cr, uid, sol_ids)
        dict_sol   = {} #{ptd_id: [all_qt, [sol records]]}
        for line in sale_lines:
            if line.product_id.id in dict_sol:
                dict_sol[line.product_id.id][0] += uom_pool._compute_qty_obj(cr, uid, line.product_uom, line.product_uom_qty, line.product_id.uom_id) # We compute the SO line quantity to Product uom
                dict_sol[line.product_id.id][1].append(line)
            else:
                dict_sol.update({line.product_id.id: [uom_pool._compute_qty_obj(cr, uid, line.product_uom, line.product_uom_qty, line.product_id.uom_id), [line,] ]})
        
        #procurement_ids = procurement_pool.search(cr, uid, [('company_id','=',company_id),('type','=','mmx'),'|',('po_state','in',['draft',]),('po_state','=','')])
        cr.execute(""" SELECT proc.id
                       FROM procurement_order AS proc
                         LEFT JOIN purchase_order AS po ON (proc.purchase_id = po.id)
                       WHERE proc.company_id = %s 
                         AND proc.type = 'mmx'
                         AND proc.state != 'done'
                         AND (proc.purchase_id IS NULL OR po.state='draft'); """, (company_id,))
        procurement_ids =[x[0] for x in cr.fetchall()]
        logger.debug('>>>>>sprocurment_ids %s'%(procurement_ids))
        
        procurements     = procurement_pool.browse(cr, uid, procurement_ids)
        dict_procurement = {} #{pid:  borwse_record}
        for proc in procurements:
            if proc.product_id.id in dict_procurement:
                dict_procurement[proc.product_id.id][0] += uom_pool._compute_qty_obj(cr, uid, proc.product_uom, proc.product_qty, proc.product_id.uom_id)
                dict_procurement[proc.product_id.id][1].append(proc)
            else:
                dict_procurement.update({proc.product_id.id: [uom_pool._compute_qty_obj(cr, uid, proc.product_uom, proc.product_qty, proc.product_id.uom_id), [proc,] ]})
        
        # Process 
        for product_id in dict_sol:
            sale_lines = dict_sol[product_id][1]
            product    = sale_lines[0].product_id
            qty        = dict_sol[product_id][0]
            uom_id     = product.uom_id.id
            
            if product_id in dict_procurement.keys():
                procurement_id = dict_procurement[product_id][1][0].id
                for sol in sale_lines:
                    sol_pool.write(cr, uid, sol.id,{'procurement_id':procurement_id})
            
            else:
                location_id    = location_pool.search(cr, uid, [('name','=','Stock'),('usage','=','internal'),('company_id','=',company_id)])[0]
                procurement_id = procurement_pool.create(cr, uid, {
                    'name':        product.name,
                    'origin':      'Internal Scheduler',
                    'product_id':  product_id,
                    'product_qty': qty,
                    'product_uom': uom_id,
                    'location_id': location_id,    
                    'company_id':  company_id,
                    'type':        'mmx',
                })
                new_procurement_ids.append(procurement_id)
                
                for sol in sale_lines:
                    sol_pool.write(cr, uid, sol.id, {'procurement_id':procurement_id})
                
                # Trigger the procurement wkf, create PO
                try:
                    procurement = procurement_pool.browse(cr, uid, procurement_id)
                    wkf_service.trg_validate(uid, 'procurement.order', procurement_id, 'button_confirm', cr)
                    wkf_service.trg_validate(uid, 'procurement.order', procurement_id, 'button_check',   cr)
                
                    # Find the stock move and cancel this stock.move  jon.chow<@>elico-corp.com    Jul 15, 2013
                    stock_move_pool.action_cancel(cr, uid, [procurement.move_id.id,])
                except Exception as err:
                    logger.warning('Procurement #%s for Product %s (Qty:%s) has failed: %s'%(procurement.id, procurement.product_id.default_code or procurement.product_id.name, procurement.product_qty, err))
        
        
        # step 2   Update Procurements Qty
        procurement_pool.update_qty_by_sol(cr, uid, procurement_ids + new_procurement_ids)
        # step 3   Update  PO lines Qty 
        procurement_pool.update_pol_qty(cr, uid, procurement_ids + new_procurement_ids)
        return True

wizard_sol2pol()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: