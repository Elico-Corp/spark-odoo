from openerp.osv import fields, orm


class purchase_order(orm.Model):
    _inherit = 'purchase.order'
    _columns = {
        'is_locked': fields.boolean('Is Locked')
    }

    _defaults = {
        'location_id': False
    }


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    def _recompute_procurement_qty(self, cr, uid, ids, context=None):
        for l in self.browse(cr, uid, ids, context=context):
            if not l.order_id.is_locked:
                continue
            # TODO only if the PO is locked
            # if we change the purcahse order line
            # we change the associated procurement qty
            if l.procurement_id and\
                    l.procurement_id.product_qty != l.product_qty:
                l.procurement_id.write(
                    {'product_qty': l.product_qty},
                    context=context
                )
                if l.procurement_id.move_id and\
                        l.procurement_id.move_id.product_qty != l.product_qty:
                    l.procurement_id.move_id.write(
                        {'product_qty': l.product_qty})

    def write(self, cr, uid, ids, data, context={}):
        res = super(purchase_order_line, self).write(
            cr, uid, ids, data, context=context)
        self._recompute_procurement_qty(cr, uid, ids, context=context)
        return res
