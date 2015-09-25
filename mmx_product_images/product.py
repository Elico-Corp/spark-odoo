from openerp.osv import orm, fields


class product_product(orm.Model):
    _inherit = 'product.product'

    def _ger_web_image(self, cr, uid, ids, fields, arg=None,
                       context=None):
        res = {}
        for product in self.browse(cr, uid, ids):
            config_pool = self.pool.get('ir.config_parameter')
            config_ids = config_pool.search(
                cr,
                uid,
                [('key', '=', 'web.image.url')])
            if config_ids:
                config = config_pool.browse(cr, uid, config_ids[0])
                url = 'http://'+config.value+'/'+product.code+'.jpg'
                res[product.id] = url
            else:
                res[product.id] = ''
        return res

    _columns = {
        'web_image': fields.function(
            _ger_web_image,
            arg=None,
            type='char',
            string='Web Image',
            readonly=True,
            store=False)
    }
