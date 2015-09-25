from openerp.osv import fields, orm


class purchase_order(orm.Model):
    _inherit = 'purchase.order'
    _columns = {
        'is_locked': fields.boolean('Is Locked')
    }

    _defaults = {
        'location_id': False
    }
