from openerp.osv import fields, orm


class purchase_order(orm.Model):
    _inherit = 'magento.website'
    _columns = {
        'company_id': fields.many2one('res.company', string="Company")
    }
