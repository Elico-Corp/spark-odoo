# -*- coding: utf-8 -*-

import logging
from openerp.osv import fields, orm, osv
import openerp.addons.decimal_precision as dp
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                 )
from .backend import magento
from openerp.addons.magentoerpconnect.unit.backend_adapter import GenericAdapter
from openerp.addons.magentoerpconnect.unit.import_synchronizer import (BatchImportSynchronizer,
                                                                       DelayedBatchImport,
                                                                       MagentoImportSynchronizer
                                                                      )
from openerp.addons.magentoerpconnect.unit.binder import MagentoModelBinder
from openerp.addons.connector.queue.job import job


from openerp.tools.translate import _
_logger = logging.getLogger(__name__)
 
class product_attribute_set(orm.Model):
  _name = 'product.attribute.set'

  _columns = {
    'name': fields.char('name', required=True),
    'magento_bind_ids': fields.one2many('magento.product.attribute.set', 'openerp_id',
                                            string="Magento Bindings"),
  }

  



class magento_product_attribute_set(orm.Model):
	_name = 'magento.product.attribute.set'
	_inherit = 'magento.binding'
	_inherits = {'product.attribute.set': 'openerp_id'}

	_columns = {
	    'openerp_id': fields.many2one('product.attribute.set',
	                                   string='Magento order',
	                                   required=True,
	                                   ondelete='cascade'),
      'created_at': fields.date('Created At (on Magento)'),
      'updated_at': fields.date('Updated At (on Magento)'),
	}

	_sql_constraints = [
	    ('magento_uniq', 'unique(backend_id, magento_id)',
	     'A partner tag with same ID on Magento already exists.'),
	]


@magento
class ProductAttributeSetBatchImport(MagentoImportSynchronizer):
    _model_name = ['magento.product.attribute.set']

@magento
class ProductAttributeSetBatchImport(DelayedBatchImport):
    """ Import the Magento Products.

    For every product category in the list, a delayed job is created.
    Import from a date
    """
    _model_name = ['magento.product.attribute.set']


@magento
class ProductAttributeSetAdapter(GenericAdapter):
    _model_name = 'magento.product.attribute.set'
    _magento_model = 'ol_catalog_product_attributeset'


@magento
class ProductAttributeSetImportMapper(ImportMapper):
    _model_name = 'magento.product.attribute.set'

    direct = [('attribute_set_id', 'magento_id'),
              ('attribute_set_name', 'name')
              ]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
        
@job
def product_attribute_set_import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from Magento """
    if filters is None:
        filters = {}
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(ProductAttributeSetBatchImport)
    importer.run(filters)