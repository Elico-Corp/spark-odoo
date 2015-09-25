from .backend import magento_sparkmodel
from openerp.addons.magentoerpconnect.partner import PartnerImportMapper
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


@magento_sparkmodel
class PartnerDeleteSynchronizer(MagentoDeleteSynchronizer):

    """ Partner deleter for Magento """
    _model_name = ['magento.res.partner']


@magento_sparkmodel
class PartnerExport(MagentoExporter):
    _model_name = ['magento.res.partner']


@magento_sparkmodel
class PartnerExportMapper(ExportMapper):
    _model_name = 'magento.res.partner'

    direct = [
            ('email', 'email'),
            ('birthday', 'dob'),
            ('emailid', 'email'),
            ('taxvat', 'taxvat'),
    ]


    @mapping
    def group(self, record):
        sess = self.session
        pricelist_id = record.property_product_pricelist.id
        backend_id = self.backend_record.id
        mag_pricelist_pool = sess.pool.get('magento.product.pricelist')
        pricelist_ids = mag_pricelist_pool.search(
            sess.cr, sess.uid,
            [('openerp_id', '=', pricelist_id),
             ('backend_id', '=', backend_id)])
        res = {}
        if pricelist_ids and len(pricelist_ids) > 0:
            pricelist = mag_pricelist_pool.read(
                sess.cr, sess.uid, pricelist_ids[0], ['magento_id'])
            res['group_id'] = pricelist['magento_id']
        return res


@magento_sparkmodel
class MMXPartnerImportMapper(PartnerImportMapper):
    _model_name = 'magento.res.partner'

    @mapping
    def company(self, record):
        sess = self.session
        binder = self.get_binder_for_model('magento.store')
        store_id = binder.to_openerp(record['website_id'], unwrap=True)
        store = sess.pool.get('sale.shop').browse(sess.cr, sess.uid, store_id)
        if not store:
            raise MappingError("The store does not exist in magento.\
                                You need to import it first")
        return {'company_id': store.company_id.id}
