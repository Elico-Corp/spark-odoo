from .backend import magento_sparkmodel
from openerp.addons.magentoerpconnect.unit.binder import MagentoModelBinder


@magento_sparkmodel
class MyMagentoModelBinder(MagentoModelBinder):
    _model_name = MagentoModelBinder._model_name + ['magento.sale.cart', 'magento.sale.wishlist', 'magento.stock.move', 'magento.product.pricelist']
