# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Alex Duan <alex.duan@elico-corp.com>
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

from openerp.osv import osv, fields


class stock_invoice_onshipping(osv.osv_memory):
    _inherit = 'stock.invoice.onshipping'

    _columns = {
        'if_merge_invoice_lines': fields.boolean('Merge invoice lines', 
            help="if true, the invoice "
            "lines that have the same product will be merged into one.Default is true.")
    }

    def create_invoice(self, cr, uid, ids, context=None):
        """inherit from stock/wizard/stock_invoice_onshipping.py, passing if_merge_invoice_lines.
        
        Parameters
        ----------
        
        Returns
        -------
        
        """
            
        if context is None:
            context = {}
        picking_pool = self.pool.get('stock.picking')
        onshipdata_obj = self.read(cr, uid, ids, ['journal_id', 'group', 'invoice_date', 'if_merge_invoice_lines'])
        if context.get('new_picking', False):
            onshipdata_obj['id'] = onshipdata_obj.new_picking
            onshipdata_obj[ids] = onshipdata_obj.new_picking
        context['date_inv'] = onshipdata_obj[0]['invoice_date']
        active_ids = context.get('active_ids', [])
        active_picking = picking_pool.browse(cr, uid, context.get('active_id',False), context=context)
        inv_type = picking_pool._get_invoice_type(active_picking)
        context['inv_type'] = inv_type
        if isinstance(onshipdata_obj[0]['journal_id'], tuple):
            onshipdata_obj[0]['journal_id'] = onshipdata_obj[0]['journal_id'][0]
        res = picking_pool.action_invoice_create(cr, uid, active_ids,
              journal_id = onshipdata_obj[0]['journal_id'],
              group = onshipdata_obj[0]['group'],
              type = inv_type,
              if_merge_invoice_lines = onshipdata_obj[0]['if_merge_invoice_lines'],
              context=context)
        return res

    _defaults = {
        'if_merge_invoice_lines': False,
    }


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', if_merge_invoice_lines=False, context=None, *args, **wargs):
        #I think the type should not be default to set to 'out_invoice' alex
        """ This overwrite the former one added the functionality that merging invoice lines.
        Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        partner_obj = self.pool.get('res.partner')
        ml_obj = self.pool.get('stock.move')
        invoices_group = {}
        res = {}
        inv_type = type
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.invoice_state != '2binvoiced':
                continue
            partner = self._get_partner_to_invoice(cr, uid, picking, context=context)
            if isinstance(partner, int):
                partner = partner_obj.browse(cr, uid, [partner], context=context)[0]

            if not partner: 
                raise osv.except_osv(_('Error, no partner !'),
                    _('Please put a partner on the picking list if you want to generate invoice.'))

            if not inv_type:
                inv_type = self._get_invoice_type(picking)

            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
            else:
                invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id

            if not if_merge_invoice_lines:
                for move_line in picking.move_lines:
                    if move_line.state == 'cancel':
                        continue
                    if move_line.scrapped:
                        # do no invoice scrapped products
                        continue
                    vals = self._prepare_invoice_line(cr, uid, group, picking, move_line,
                                    invoice_id, invoice_vals, context=context)
                    if vals:
                        invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
                        self._invoice_line_hook(cr, uid, move_line, invoice_line_id)
            else:
                #if need merge the invoice lines. we group the move lines and create merged invoice
                invoice_lines_val = []
                for move_line in picking.move_lines:
                    if move_line.state == 'cancel':
                        continue
                    if move_line.scrapped:
                        continue
                    vals = self._prepare_invoice_line(cr, uid, group, picking, move_line,
                                    invoice_id, invoice_vals, context=context)
                    vals.update({'move_line': [move_line]})
                    invoice_lines_val.append(vals)
                real_val = []
                for i in range(0, len(invoice_lines_val)):
                    j = i+1
                    while j < len(invoice_lines_val):
                        if self._cmp_move_lines(invoice_lines_val[i], invoice_lines_val[j]):
                            #do the merge, mainly add the quantity and move_line.
                            invoice_lines_val[j]['quantity'] += invoice_lines_val[i]['quantity']
                            invoice_lines_val[j]['move_line'].extend(invoice_lines_val[i]['move_line'])
                            break
                        j += 1
                    if j == len(invoice_lines_val):
                        real_val.append(invoice_lines_val[i])

                for vals in real_val:
                    invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
                    for ml in vals.get('move_line'):
                        #there may be many share one invoice_line_id
                        self._invoice_line_hook(cr, uid, ml, invoice_line_id)

            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                    set_total=(inv_type in ('in_invoice', 'in_refund')))
            self.write(cr, uid, [picking.id], {
                'invoice_state': 'invoiced',
                }, context=context)
            self._invoice_hook(cr, uid, picking, invoice_id)
        self.write(cr, uid, res.keys(), {
            'invoice_state': 'invoiced',
            }, context=context)
        return res

    def _cmp_move_lines(self, move_line1, move_line2):
        ''' the conditions to check to see if the two lines can be merge into one invoice line.
            1- same product
            2- same product uom
            3- same discount
            4- same price_unit
        '''
        #TODO what if move line doesn't have company_id or other?
        #TODO the name of this method is a bit unproper
        if move_line1 and move_line2:
            return (move_line1.get('product_id', None) == move_line2.get('product_id', None) \
                and move_line1.get('uos_id', None) == move_line2.get('uos_id', None) \
                and move_line1.get('discount', 0.0) == move_line2.get('discount', 0.0) \
                and move_line1.get('price_unit', 0.0) == move_line2.get('price_unit', 0.0))
        else:
            return False
stock_picking()

