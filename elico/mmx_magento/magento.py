from openerp.osv import fields, orm


class magento_website(orm.Model):
    _inherit = 'magento.website'
    _columns = {
        'company_id': fields.many2one('res.company', string="Company")
    }


class magento_backend(orm.Model):
    _inherit = 'magento.backend'
    _columns = {
        'pricelist_id': fields.many2one('product.pricelist', string="Pricelist")
    }
