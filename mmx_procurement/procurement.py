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
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp import netsvc
import logging
logger = logging.getLogger(__name__)

#TODO: when write SOL, if the  schedule PO state is confirm , raise the error, can not be change 
 

class product_product(osv.osv):
    _inherit = 'product.product'
    _name    = 'product.product'
    
    def _auto_init(self, cr, context=None):
        super(product_product, self)._auto_init(cr, context=context)
        #TODO:  Is it necessary all product procurement method set to  MTS or MTO?
        cr.execute("UPDATE product_template SET procure_method='make_to_stock'")

product_product()



class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _name    = 'sale.order.line'
    
    _columns={
        'procurement_id': fields.many2one('procurement.order', 'Procurement Order'),
    }

sale_order_line()



class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _name    = 'purchase.order.line'
    
    _columns={
        'procurement_id': fields.many2one('procurement.order', 'Procurement Order'),
        #'pol_ids':        fields.related('procurement_id',     'sol_ids', type='one2many', relation='sale.order.line', string='SOL info', readonly=True),
    }

purchase_order_line()



class res_company(osv.osv):
    _inherit = 'res.company'
    _name    = 'res.company'
    
    _columns={
        'sequence_mmx_schedule': fields.integer('MMX Schedule Sequence', help='Define the order in which the MMX scheduler will be run.'),
    }

res_company()



class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    _name    = 'procurement.order'
    
    _columns={
        'sol_ids':  fields.one2many('sale.order.line',     'procurement_id', 'Sale Order line'),
        'pol_ids':  fields.one2many('purchase.order.line', 'procurement_id', 'Purchase Order line'),
        'type':     fields.selection([('standard','Standard'),('mmx','MMX')], type='char', size=16, string='Type'),
        'po_state': fields.related('purchase_id', 'state', type='char', string='PO state'),
    }
    
    
    #jon  update procurement qty according the sum of  SOL
    def update_qty_by_sol(self, cr, uid, ids, context=None):
        for p in self.browse(cr, uid, ids, context=context):
            qty = sum([line.product_uom_qty for line in p.sol_ids])
            self.write(cr, uid, p.id, {'product_qty':qty}, context=context)
        return True
    
    
    def update_pol_qty(self, cr, uid, ids, context=None):
        """ According procurement qty update POL qty, if the POL state  is draft
            mention: change  write sol  -->  write so,so that can auto trigger intercompany action to update the PO
        """
        context     = context or {}
        wkf_service = netsvc.LocalService("workflow")
        pol_object  = self.pool.get('purchase.order.line')
        po_object   = self.pool.get('purchase.order')
        
        for procurement in self.browse(cr,uid,ids):
            #pol_ids=pol_object.search(cr,uid, [('product_id','=',procurement.product_id.id),('order_id','=',procurement.purchase_id.id),('state','=','draft')])
            pol = procurement.purchase_id and procurement.purchase_id.order_line[0] or False
            if pol:
                if pol.product_qty != procurement.product_qty:
                    if pol.state=='draft':
                        
                        #use PO write,not POL write, so that can auto trigger the intercompany action.
                        #pol_object.write(cr,uid,pol.id,{'product_qty':procurement.product_qty})
                        po_object.write(cr,uid, procurement.purchase_id.id ,{
                            'order_line':[(1,pol.id,{'product_qty':procurement.product_qty})],
                        })
                        
                        self.pool.get('stock.move').write(cr, uid, procurement.move_id.id, {'product_qty':procurement.product_qty}, context=context)
                        
                        #if product_qty==0 cancel this PO and POL  ?? why standard OE wkf, cancel action only  write{'state':'cancel'}, not cancel the POL??
                        if procurement.product_qty == 0:
                            pol_object.write(cr,uid,pol.id,{'state':'cancel'})
                            wkf_service.trg_validate(uid, 'purchase.order', pol.order_id.id , 'purchase_cancel', cr)
                    else:
                        self.write(cr,uid,procurement.id,{'message':'Can not update the Confirm POL QTY %s to %s' % (pol.product_qty,procurement.product_qty)})
        return True
    
    
    #rewrite the check, never pop the exception ,only record the error info.   jon.chow<@>elico-corp.com    Jul 15, 2013                    
    def check_supplier_info(self, cr, uid, ids, context=None):
        logger.debug('>>>>into check supplier info')
        partner_obj = self.pool.get('res.partner')
        user        = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for procurement in self.browse(cr, uid, ids, context=context):
            if not procurement.product_id.seller_ids:
                message = _('No supplier defined for this product !')
                self.message_post(cr, uid, [procurement.id], body=message)
                cr.execute('UPDATE procurement_order SET message=%s WHERE id=%s', (message, procurement.id))
                return False
            partner = procurement.product_id.seller_id #Taken Main Supplier of Product of Procurement.
            
            if not partner:
                message = _('No default supplier defined for this product')
                self.message_post(cr, uid, [procurement.id], body=message)
                cr.execute('UPDATE procurement_order SET message=%s WHERE id=%s', (message, procurement.id))
                return False
            if user.company_id and user.company_id.partner_id:
                if partner.id == user.company_id.partner_id.id:
                    #jon  never pop error, only write the error info into procurement
                    cr.execute('UPDATE procurement_order SET message=%s WHERE id=%s', ("The product has been defined with your company as reseller which seems to be a configuration error", procurement.id))
                    #raise osv.except_osv(_('Configuration Error!'), _('The product "%s" has been defined with your company as reseller which seems to be a configuration error!' % procurement.product_id.name))
            
            address_id = partner_obj.address_get(cr, uid, [partner.id], ['delivery'])['delivery']
            if not address_id:
                message = _('No address defined for the supplier')
                self.message_post(cr, uid, [procurement.id], body=message)
                cr.execute('UPDATE procurement_order SET message=%s WHERE id=%s', (message, procurement.id))
                return False
        return True
    
    
    def _get_supplier_by_company(self,cr,uid,procurement):
        """ Select a supplier from prourement.seller_ids, if the seller company same as the procurement company """
        res     = [9999999, None]
        sellers = procurement.product_id.seller_ids
        procurement_company_id = procurement.company_id.id
        for seller in sellers:
            seller_company_id = seller.company_id and seller.company_id.id or False
            if seller_company_id == procurement_company_id and seller.sequence < res[0]:
                res = [seller.sequence, seller.name.id]
        return res[1]
    
    
    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line_vals, context=None):
        """ When Procurement create PO and POL, PO parner_id come form  product supplier_info
            POL record the procurement's id
        """
        partner_id = self._get_supplier_by_company(cr,uid,procurement)
        if partner_id:
            po_vals.update({'partner_id': partner_id})
        line_vals.update({'procurement_id': procurement.id})
        
        return super(procurement_order,self).create_procurement_purchase_order(cr,uid, procurement, po_vals, line_vals, context=context)
    
    
    def action_confirm(self, cr, uid, ids, context=None):
        ''' jon: if the procurements type is mmx, dont creat the stock.picking '''
        """ Confirms procurement and writes exception message if any.
        @return: True
        """
        move_obj = self.pool.get('stock.move')
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.product_qty <= 0.00:
                raise osv.except_osv(_('Data Insufficient !'), _('Please check the quantity in procurement order(s) for the product "%s", it should not be 0 or less!' % procurement.product_id.name))
            if procurement.product_id.type in ('product', 'consu'):
                if not procurement.move_id:
                    source = procurement.location_id.id
                    if procurement.procure_method == 'make_to_order':
                        source = procurement.product_id.property_stock_procurement.id
                    id = move_obj.create(cr, uid, {
                        'name':             procurement.name,
                        'location_id':      source,
                        'location_dest_id': procurement.location_id.id,
                        'product_id':       procurement.product_id.id,
                        'product_qty':      procurement.product_qty,
                        'product_uom':      procurement.product_uom.id,
                        'date_expected':    procurement.date_planned,
                        'state':            'draft',
                        'company_id':       procurement.company_id.id,
                        'auto_validate':    True,
                    })
                    
                    #===========================================================
                    # ##jon 
                    # if procurement.type == 'mmx':
                    #     move_obj.write(cr,uid,id,{'state':'cancel',})
                    #     #move_obj.action_cancel(cr, uid, [id], context=context)
                    # else:
                    #===========================================================
                    move_obj.action_confirm(cr, uid, [id], context=context)
                    ###
                    
                    self.write(cr, uid, [procurement.id], {'move_id': id, 'close_move': 1})
        self.write(cr, uid, ids, {'state': 'confirmed', 'message': ''})
        return True

procurement_order()



class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _name    = 'purchase.order'
    
    def _get_sol(self,cr,uid,ids,fields,arg=None,context=None):
        res = {}
        for po in self.browse(cr,uid,ids):
            value = []
            if po.order_line:
                if po.order_line[0].procurement_id:
                    if po.order_line[0].procurement_id.sol_ids:
                        sols  = po.order_line[0].procurement_id.sol_ids
                        value = [x.id for x in sols]
            res[po.id] = value
        return res
    
    _columns = {
        'sol_ids': fields.function(_get_sol, arg=None, type='one2many', relation='sale.order.line', string='SOL Info')
    }

purchase_order()


#confirm_pol_ids=pol_object.search(cr,uid, [('product_id','=',procurement.product_id.id),('order_id','=',procurement.purchase_id.id),('state','in',['confirm','done'])])

#===================================================================
# if draft_pol_ids:
#     #update qty
#     pol_object.write(cr, uid, draft_pol_ids[0], {'product_qty':procurement.product_qty})
# else:
#     #not do any thing, only wirte the error message, and  
#     self.write(cr, uid, procurement.id,{'message':'Can\'t update the Confirm POL qty %s to %s' % (9,8)})
#===================================================================
    

    #self.create_new_pol(cr, uid, [procurement.id,], context=context)



#===============================================================================
# 
# '''
#     def create_new_pol(self, cr, uid, ids, context=None):
#         res = {}
#         if context is None:
#             context = {}
#         company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
#         partner_obj = self.pool.get('res.partner')
#         uom_obj = self.pool.get('product.uom')
#         pricelist_obj = self.pool.get('product.pricelist')
#         prod_obj = self.pool.get('product.product')
#         acc_pos_obj = self.pool.get('account.fiscal.position')
#         seq_obj = self.pool.get('ir.sequence')
#         warehouse_obj = self.pool.get('stock.warehouse')
#         for procurement in self.browse(cr, uid, ids, context=context):
#             res_id = procurement.move_id.id
#             partner = procurement.product_id.seller_id # Taken Main Supplier of Product of Procurement.
#             seller_qty = procurement.product_id.seller_qty
#             partner_id = partner.id
#             address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
#             pricelist_id = partner.property_product_pricelist_purchase.id
#             warehouse_id = warehouse_obj.search(cr, uid, [('company_id', '=', procurement.company_id.id or company.id)], context=context)
#             uom_id = procurement.product_id.uom_po_id.id
# 
#             qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
#             if seller_qty:
#                 qty = max(qty,seller_qty)
# 
#             price = pricelist_obj.price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, partner_id, {'uom': uom_id})[pricelist_id]
# 
#             schedule_date = self._get_purchase_schedule_date(cr, uid, procurement, company, context=context)
#             purchase_date = self._get_purchase_order_date(cr, uid, procurement, company, schedule_date, context=context)
# 
#             #Passing partner_id to context for purchase order line integrity of Line name
#             new_context = context.copy()
#             new_context.update({'lang': partner.lang, 'partner_id': partner_id})
# 
#             product = prod_obj.browse(cr, uid, procurement.product_id.id, context=new_context)
#             taxes_ids = procurement.product_id.supplier_taxes_id
#             taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)
# 
#             name = product.partner_ref
#             if product.description_purchase:
#                 name += '\n'+ product.description_purchase
#             line_vals = {
#                 'name': name,
#                 'product_qty': qty,
#                 'product_id': procurement.product_id.id,
#                 'product_uom': uom_id,
#                 'price_unit': price or 0.0,
#                 'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
#                 'move_dest_id': res_id,
#                 'taxes_id': [(6,0,taxes)],
#                 'procurement_id':procurement.id,
#             }
#             name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % procurement.name
#             po_vals = {
#                 'name': name,
#                 'origin': procurement.origin,
#                 'partner_id': partner_id,
#                 'location_id': procurement.location_id.id,
#                 'warehouse_id': warehouse_id and warehouse_id[0] or False,
#                 'pricelist_id': pricelist_id,
#                 'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
#                 'company_id': procurement.company_id.id,
#                 'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
#                 'payment_term_id': partner.property_supplier_payment_term.id or False,
#             }
#             
#             po_id = self.pool.get('purchase.order').create(cr, uid, po_vals, context=context)
#             line_vals.update({'order_id':po_id})
#             pol_id=self.pool.get('purchase.order.line').create(cr, uid, line_vals, context=context)
#
# '''
#===============================================================================

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
