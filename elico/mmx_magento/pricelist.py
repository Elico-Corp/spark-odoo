# -*- coding: utf-8 -*-
import xmlrpclib
from openerp.osv import fields, orm, osv
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


class product_pricelist(orm.Model):
    _inherit = 'product.pricelist'

    _columns = {
        'magento_bind_ids': fields.one2many(
            'magento.product.pricelist',
            'openerp_id',
            string='Magento Bindings'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['magento_bind_ids'] = False
        return super(product_pricelist, self).copy_data(cr, uid, id,
                                                        default=default,
                                                        context=context)


class magento_product_pricelist(orm.Model):
    _name = 'magento.product.pricelist'
    _inherit = 'magento.binding'
    _inherits = {'product.pricelist': 'openerp_id'}

    _columns = {
        'openerp_id': fields.many2one('product.pricelist',
                                      string='Partner Category',
                                      required=True,
                                      ondelete='cascade')
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A partner tag with same ID on Magento already exists.'),
    ]


@magento_sparkmodel
class ProductPricelistDeleteSynchronizer(MagentoDeleteSynchronizer):

    """ Partner deleter for Magento """
    _model_name = ['magento.product.pricelist']


@magento_sparkmodel
class ProductPricelistExport(MagentoExporter):
    _model_name = ['magento.product.pricelist']


@magento_sparkmodel
class ProductPricelistExportMapper(ExportMapper):
    _model_name = 'magento.product.pricelist'

    direct = [('name', 'customer_group_code')]


@magento_sparkmodel
class ProductPricelistAdapter(GenericAdapter):
    _model_name = 'magento.product.pricelist'
    _magento_model = 'ol_customer_groups'

    def _call(self, method, arguments):
        try:
            return super(ProductPricelistAdapter, self)._call(
                method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the Magento API
            # when the product does not exist
            if err.faultCode == 101:
                raise IDMissingInBackend
            else:
                raise

    def search(self, filters=None, from_date=None):
        """ Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        filters = filters or None
        return [int(row['customer_group_id']) for row
                in self._call('%s.list' % self._magento_model,
                              [filters] if filters else [{}])]

    def create(self, data):
        return self._call('%s.create' % self._magento_model, [data])

    def read(self, id, storeview_id=None, attributes=None):
        """ Returns the information of a record

        :rtype: dict
        """
        return self._call('%s.info' % self._magento_model,
                          [int(id), storeview_id, attributes, 'id'])

    def write(self, id, data, storeview_id=None):
        """ Update records on the external system """
        # XXX actually only ol_catalog_product.update works
        # the PHP connector maybe breaks the catalog_product.update
        return self._call('%s.update' % self._magento_model,
                          [int(id), data, storeview_id, 'id'])
