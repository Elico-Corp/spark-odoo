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
from openerp import netsvc


class sale_announcement_line(osv.osv):
    _name = 'sale.announcement.line'
    _columns = {
        'name': fields.char('Name', size=64),
        'announcement_id': fields.many2one('sale.announcement',
                                           'Sale Announcement'),
    }


class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'announcement_id': fields.many2one('sale.announcement',
                                           'Sale Announcement'),
    }


class sale_announcement (osv.osv):
    _name = 'sale.announcement'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=1),
        'state': fields.selection([('draft', 'Draft'),
                                   ('publish', 'Publish'),
                                   ('cancel', 'Cancel')],
                                  'State', size=32,),
        'sequence': fields.char('Sequence', size=32, required=True, select=1),
        'create_date': fields.date('Creation date', readonly=True),
        'public_date': fields.date('Publication Date'),
        'cut_off_date': fields.date('Cut-off Date'),
        'responsible_uid': fields.many2one('res.users', 'Person responsible'),
        'lines': fields.one2many('sale.announcement.line',
                                 'announcement_id', 'Announcement Line'),
        'product_ids': fields.one2many('product.product', 'announcement_id',
                                       'Products',),
        'categ_ids': fields.many2many(
            'product.category', 'announcement_categ_rel', 'announcement_id',
            'categ_id', string='Announcement Website Categories'),
        'order_categ_ids': fields.many2many(
            'product.category', 'order_announcement_categ_rel',
            'announcement_id', 'categ_id', string='Order Website Categories'),
        'sale_order_line_ids': fields.one2many(
            'sale.order.line', 'announcement_id', 'Sale order lines')
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'sequence': lambda self, cr, uid, context=None: self.pool.get(
            'ir.sequence').get(cr, uid, 'sale.announcement'),
    }

    def action_publish(self, cr, uid, ids, context=None):
        """
        action publish, all product approve to announcement
        TODO:The categories included in the announcement
            should be added to the products.
        """
        product_obj = self.pool.get('product.product')
        wkf_service = netsvc.LocalService("workflow")

        for announcement in self.browse(cr, uid, ids, context=None):
            categ_ids = [c.id for c in announcement.categ_ids]
            product_ids = [p.id for p in announcement.product_ids]

            product_obj.write(cr, uid, product_ids,
                              {'categ_ids': [(4, x) for x in categ_ids]})
            for product_id in product_ids:
                wkf_service.trg_validate(uid, 'product.product',
                                         product_id, 'approve', cr)

        self.write(cr, uid, ids, {'state': 'publish'})

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def check_back_draft(self, cr, uid, ids, context=None):
        """
        check all line status is Announcement
        """
        for ann in self.browse(cr, uid, ids, context=context):
            for product in ann.product_ids:
                if product.state != 'preorder':
                    return False
        return True

    def action_back_draft(self, cr, uid, ids, context=None):
        """
        cancel all Announcement web categ
        cancel all Order web categ
        """
        product_obj = self.pool.get('product.product')
        wkf_service = netsvc.LocalService("workflow")
        for ann in self.browse(cr, uid, ids, context=None):
            categ_ids = [c.id for c in ann.categ_ids]
            product_ids = [p.id for p in ann.product_ids]

            self.write(cr, uid, ids, {'categ_ids': [(6, 0, [])],
                                      'order_categ_ids': [(6, 0, [])]})
            product_obj.write(cr, uid, product_ids,
                              {'categ_ids': [(5, x) for x in categ_ids]})
            for product_id in product_ids:
                wkf_service.trg_validate(
                    uid, 'product.product', product_id, 'back_approve', cr)

        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        seq = self.pool.get('ir.sequence').get(cr, uid, 'sale.announcement')
        seq = str(seq)
        default.update({
            'sequence': seq,
            'product_ids': False,
            'state': 'draft',
            'categ_ids': False, })
        return super(sale_announcement, self).copy(cr, uid, id, default)


class product_product(osv.osv):
    _inherit = 'product.product'

    def link_to_product(self, cr, uid, ids, context=None):
        """
        announcement product editable tree view , open Product form.
        """
        return {
            'name': 'Product',
            'target': "new",
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'product.product',
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
        }

    def approve_from_announcement(self, cr, uid, ids, context=None):
        """
        product approve next step,
        then product categories  subtract
        Announcement_categ_ids  , plus Sale_categ_ids
        """
        if context is None:
            context = {}

        wkf_service = netsvc.LocalService("workflow")
        wkf_service.trg_validate(uid, 'product.product', ids[0],
                                 'approve', cr)

        categ_ids = context.get('categ_ids', False)[0][2]
        order_categ_ids = context.get('order_categ_ids', False)[0][2]
        # unlink announcement_categ and link order_categ
        self.write(cr, uid, ids,
                   {'categ_ids': [(3, x) for x in categ_ids]
                    + [(4, x) for x in order_categ_ids]})
        return True


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def _get_announcement(
            self, cr, uid, ids, fieldname, arg=None,
            context=None):
        res = {}
        for sol in self.browse(cr, uid, ids, context=context):
            res[sol.id] = (sol.product_id.announcement_id
                           and sol.product_id.announcement_id.id
                           or False)
        return res

    def _get_sale_order_lines(self, cr, uid, ids, context=None):
        if ids:
            res = {}
            anno_obj = self.pool['sale.announcement']
            for anno in anno_obj.browse(cr, uid, ids, context=context):
                for sol in anno.sale_order_line_ids:
                    res[sol.id] = True
            return res.keys()

    def _get_cut_off_date(
            self, cr, uid, ids, field_names, args, context=None):
        if not ids:
            return {}
        res = {}.fromkeys(ids, None)
        for line in self.browse(cr, uid, ids, context=context):
            if line.announcement_id:
                res[line.id] = line.announcement_id.cut_off_date
        return res

    _columns = {
        'announcement_id': fields.function(
            _get_announcement,
            type='many2one',
            relation='sale.announcement',
            string='Announcement',
            store=True),
        'cut_off_date': fields.function(
            _get_cut_off_date,
            type="date", string="Cut-off Date",
            store={
                'sale.announcement': (_get_sale_order_lines, ['cut_off_date'], 1),
            })
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
