from openerp.osv import orm, fields
from .backend import magento_sparkmodel
from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.mapper import (mapping,
                                                  changed_by,
                                                  ExportMapper)
from openerp.addons.magentoerpconnect.unit.delete_synchronizer import (
    MagentoDeleteSynchronizer)
from openerp.addons.magentoerpconnect.unit.export_synchronizer import (
    MagentoExporter)
from openerp.addons.magentoerpconnect.unit.backend_adapter import (
    GenericAdapter)
from .backend import magento_sparkmodel
from openerp.addons.connector.exception import MappingError
from datetime import datetime


class stock_move(orm.Model):
    _inherit = 'stock.move'

    _columns = {
        'magento_bind_ids': fields.one2many('magento.stock.move',
                                            'openerp_id',
                                            string="Magento Bindings")
    }

    def create(self, cr, uid, data, context=None):
        product_pool = self.pool.get('product.product')
        if 'product_id' in data:
            pdt_id = data['product_id']
            product = product_pool.browse(
                cr, uid, pdt_id, context=context)
            bind_ids = []
            for mb in product.magento_bind_ids:
                bind_ids.append((0, 0,  {'backend_id': mb.backend_id.id}))
            data['magento_bind_ids'] = bind_ids
        return super(stock_move, self).create(
            cr, uid, data, context=context)


class magento_stock_move(orm.Model):
    _name = 'magento.stock.move'
    _inherit = 'magento.binding'
    _inherits = {'stock.move': 'openerp_id'}

    _columns = {
        'openerp_id': fields.many2one('stock.move',
                                      string='Stock Move',
                                      required=True,
                                      ondelete='cascade'),
        'magento_id': fields.integer('Magento Cart ID',
                                     help="'order_id' field in Magento")
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A partner tag with same ID on Magento already exists.'),
    ]


@magento_sparkmodel
class StockDeleteSynchronizer(MagentoDeleteSynchronizer):

    """ Stock deleter for Magento """
    _model_name = ['magento.stock.move']


@magento_sparkmodel
class StockAdapter(GenericAdapter):
    _model_name = 'magento.stock.move'
    _magento_model = 'cataloginventory_stock_item'

    def create(self, data):
        """ Create a record on the external system """

        return self._call('%s.update' % self._magento_model,
                          [data.pop('product_id'), data])


@magento_sparkmodel
class StockExport(MagentoExporter):
    _model_name = ['magento.stock.move']


@magento_sparkmodel
class StockExportMapper(ExportMapper):
    _model_name = 'magento.stock.move'
    direct = [('product_id', 'product_id')]

    @mapping
    def qty(self, record):
        return {'qty': record.product_qty, 'is_in_stock': 1}
