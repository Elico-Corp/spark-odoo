from openerp.osv import fields, orm
from .backend import magento_sparkmodel
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.magentoerpconnect_catalog.product import(
    ProductProductExportMapper)
from openerp.addons.magentoerpconnect.product import ProductImportMapper
from openerp.addons.magentoerpconnect.unit.export_synchronizer import(
    MagentoExporter)
from openerp.addons.connector.exception import (InvalidDataError, MappingError)


@magento_sparkmodel
class ProductProductExport(MagentoExporter):
    _model_name = ['magento.product.product']

    def _validate_product_status(self, data):
        forbidden_status = ['draft', 'private']
        state = data.pop('state')
        mmx_type = data.pop('mmx_type')
        if state in forbidden_status or mmx_type == 'oem':
            raise InvalidDataError("The product cannot not "
                                   "be sent to the magento.")

    def _validate_data(self, data):
        """ Check if the values to import are correct

        Pro-actively check before the ``Model.create`` or
        ``Model.update`` if some fields are missing

        Raise `InvalidDataError`
        """
        self._validate_product_status(data)


@magento_sparkmodel
class MMXProductImportMapper(ProductImportMapper):
    _model_name = 'magento.product.product'

    def categories(self, record):
        mag_categories = record['categories']
        binder = self.get_binder_for_model('magento.product.category')

        category_ids = []

        for mag_category_id in mag_categories:
            cat_id = binder.to_openerp(mag_category_id, unwrap=True)
            if cat_id is None:
                raise MappingError("The product category with "
                                   "magento id %s is not imported." %
                                   mag_category_id)

            category_ids.append(cat_id)

        return {'categ_ids': [(6, 0, category_ids)]}


@magento_sparkmodel
class MMXProductProductExportMapper(ProductProductExportMapper):
    _model_name = 'magento.product.product'

    @mapping
    def custom_attributes(self, record):
        attributes = {}
        if record.classification_id:
            attributes['car_number'] = record.classification_id.name
        if record.color_ids:
            attributes['customer_color'] = ', '.join(
                color.name for color in record.color_ids)
        # if record.driver_ids:
        #     attributes['driver'] = ', '.join(
        #         driver.name + " " +
        #         driver.surname for driver in record.driver_ids)
        if record.model_id:
            attributes['custom_manufacturer'] = (
                record.model_id.manufacturer_id.name
                if record.model_id.manufacturer_id else '')
        # if record.model_id:
        #     attributes['model'] = record.model_id.name
        # if record.race_ed_id:
        #     attributes['race_edition'] = (
        #         record.race_ed_id.race_id.name if record.race_ed_id else '')
        if record.rank_id:
            attributes['rank'] = record.rank_id.name
        # if record.scale_id:
        #     attributes['scale'] = record.scale_id.name
        if record.year:
            attributes['year'] = record.year
        if record.model_year:
            attributes['model_year'] = record.model_year
        attributes['can_sell'] = record.do_not_allow_checkout
        return attributes

    @mapping
    def scale(self, record):
        scale_obj = record.scale_id
        if scale_obj:
            scale_option_magento_id = False
            for magento_backend in scale_obj.magento_bind_ids:
                if magento_backend.backend_id == record.backend_id:
                    scale_option_magento_id = magento_backend.magento_id

            magento_attribute = scale_obj.attribute_id
            if magento_attribute:
                return {
                    str(magento_attribute.attribute_code):
                        scale_option_magento_id
                }
        return False

    @mapping
    def product_model(self, record):
        model_obj = record.model_id

        if model_obj and model_obj.magento_bind_ids:
            model_option_magento_id = model_obj.magento_bind_ids[0].magento_id

            magento_attribute = model_obj.attribute_id
            if magento_attribute:
                return {
                    str(magento_attribute.attribute_code):
                        model_option_magento_id
                }
        return False

    @mapping
    def race_edition(self, record):
        res = {}
        race_ed_obj = record.race_ed_id

        if race_ed_obj and race_ed_obj.race_id:
            race_id = race_ed_obj.race_id
            if race_id.magento_bind_ids:
                race_option_magento_id = race_id.magento_bind_ids[0].magento_id

                magento_attribute = race_id.attribute_id

                if magento_attribute:
                    res[magento_attribute.attribute_code] =\
                        race_option_magento_id
        if race_ed_obj and race_ed_obj.year:
                res['race_edition_year'] = race_ed_obj.year
        return res

    @mapping
    def product_driver(self, record):
        driver_objs = record.driver_ids

        if driver_objs:
            magento_attribute = False

            driver_option_magento_ids = []
            for driver_obj in driver_objs:
                if driver_obj.magento_bind_ids:
                    driver_option_magento_id = \
                        driver_obj.magento_bind_ids[0].magento_id
                    driver_option_magento_ids.append(
                        str(driver_option_magento_id))
                magento_attribute = driver_obj.attribute_id
            if magento_attribute:
                return {
                    str(magento_attribute.attribute_code):
                    driver_option_magento_ids
                }
        return False

    @mapping
    def custom_status(self, record):
        status_list = {
            'draft': 3,
            'private': 3,
            'catalogue': 7,
            'preorder': 6,
            'order': 5,
            'backorder': 4,
            'solded': 3,
            'done': 3
        }
        status = status_list[record.state]

        return {
            'custom_status': status,
            'state': record.state,
            'mmx_type': record.mmx_type}

    @mapping
    def pricelist(self, record):
        sess = self.session
        pricelist_pool = sess.pool.get('product.pricelist')
        mag_pricelist_pool = sess.pool.get('magento.product.pricelist')
        pricelist_ids = mag_pricelist_pool.search(
            sess.cr, sess.uid, [('backend_id', '=', record.backend_id.id)])
        pricelists = mag_pricelist_pool.read(
            sess.cr, sess.uid, pricelist_ids, ['id', 'magento_id'])
        group_price = []

        for pricelist in pricelists:
            price = pricelist_pool.price_get(
                sess.cr, sess.uid, [pricelist['openerp_id']],
                record.openerp_id.id, 1)
            if not price[pricelist['openerp_id']]:
                continue
            group_price.append({'website_id': 0,
                                'cust_group': pricelist['magento_id'],
                                'price': price[pricelist['openerp_id']]})
        return {'group_price': group_price}

    @mapping
    def prices(self, record):
        prices = []

        for website_id in record.website_ids:
            for store_id in website_id.store_ids:
                shop_id = store_id.openerp_id
                if not shop_id.pricelist_id:
                    continue
                currency_name = shop_id.pricelist_id.currency_id.name
                for view_id in store_id.storeview_ids:
                    if record.list_price_label == currency_name:
                        prices.append([view_id.magento_id, record.list_price])
                    elif record.list2_price_label == currency_name:
                        prices.append([view_id.magento_id, record.list2_price])
                    elif record.list3_price_label == currency_name:
                        prices.append([view_id.magento_id, record.list3_price])
        return {'prices': prices}

    @mapping
    def qty(self, record):
        sess = self.session
        mag_product_pool = sess.pool.get('magento.product.product')
        record = mag_product_pool.browse(sess.cr, 1, record.id)
        product_pool = sess.pool.get('product.product')
        stocks = {}
        for website_id in record.website_ids:
            if not website_id.company_id:
                continue
            company = website_id.company_id
            if not company.stock_user_id:
                continue
            product = product_pool.browse(sess.cr, company.stock_user_id.id,
                                          record.openerp_id.id)
            for store_id in website_id.store_ids:
                for view_id in store_id.storeview_ids:
                    stocks[view_id.magento_id] = [
                        view_id.magento_id,
                        product.qty_available + product.outgoing_qty
                    ]

        return {
            'stocks': stocks,
            'custom_product_qty': 0,
            'qty': 100}


class prouct_category(orm.Model):
    _inherit = 'product.category'
    _columns = {
        'company_id': fields.many2one('res.company', string="Company")
    }
