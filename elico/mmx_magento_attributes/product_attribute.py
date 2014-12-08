# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013
#    Author: Guewen Baconnier - Camptocamp
#            David Béal - Akretion
#            LIN Yu - Elico
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.osv.osv import except_osv
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.mapper import (
    mapping, changed_by, ExportMapper,
    only_create, ImportMapper)
from openerp.addons.magentoerpconnect.unit.delete_synchronizer import (
    MagentoDeleteSynchronizer)
from openerp.addons.magentoerpconnect.unit.export_synchronizer import (
    MagentoExporter)
from openerp.addons.magentoerpconnect.unit.import_synchronizer import (
    BatchImportSynchronizer,
    DelayedBatchImport,
    MagentoImportSynchronizer)
from openerp.addons.magentoerpconnect.backend import magento
from openerp.addons.magentoerpconnect.product import (
    ProductImportMapper)
from openerp.addons.magentoerpconnect_catalog.product import (
    ProductProductExportMapper)
from openerp.addons.magentoerpconnect.connector import get_environment
from openerp.addons.magentoerpconnect.unit.backend_adapter import (
    GenericAdapter)
from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.exception import IDMissingInBackend

import logging
_logger = logging.getLogger(__name__)


class magento_product_product(orm.Model):
    _inherit = 'magento.product.product'

    # _columns = {
    #     'attribute_set_id': fields.many2one('magento.attribute.set',
    #                                         string='Attribute Set',
    #                                         ),
    # }


# @magento
# class ProductProductExportMapperForSet(ProductProductExportMapper):
#     _model_name = 'magento.product.product'

#     @mapping
#     def set(self, record):
#         binder = self.get_binder_for_model('magento.attribute.set')
#         set_id = binder.to_backend(record.attribute_set_id.id)

#         return {'attrset': set_id}

"""
Can not inherit the class
    for the reason connector have a contraint of uniqueness
        of (model name, exporter )
"""


# @mapping
# def ProductProductExportMapperForSet(self, record):
#     binder = self.get_binder_for_model('magento.attribute.set')
#     set_id = binder.to_backend(record.attribute_set_id.id)

#     return {'attrset': set_id}

# ProductProductExportMapper.set = ProductProductExportMapperForSet

# @magento
# class ProductImportMapperForSet(ProductImportMapper):
#     _model_name = 'magento.product.product'

#     @mapping
#     def set(self, record):
#         binder = self.get_binder_for_model('magento.attribute.set')
#         # binder = self.get_binder_for_model('magento.product.attribute.set')
#         set_id = binder.to_openerp(record['set'])
#         if set_id is None:
#             raise MappingError("The product attribute set with "
#                                "magento id %s is not imported." %
#                                record['set'])
#         return {'attribute_set_id': set_id}


def ProductImportMapperForSet(self, record):
    binder = self.get_binder_for_model('magento.attribute.set')
    # binder = self.get_binder_for_model('magento.product.attribute.set')
    set_id = binder.to_openerp(record['set'])
    if set_id is None:
        raise MappingError("The product attribute set with "
                           "magento id %s is not imported." %
                           record['set'])
    return {'attribute_set_id': set_id}

ProductImportMapper.set = ProductImportMapperForSet


# Attribute
class AttributeAttribute(orm.Model):
    _inherit = 'attribute.attribute'

    def _get_model_product(self, cr, uid, ids, idcontext=None):
        model, res_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'product', 'model_product_product')
        return res_id

    _columns = {
        'magento_bind_ids': fields.one2many(
            'magento.product.attribute',
            'openerp_id',
            string='Magento Bindings',),
    }

    _defaults = {
        'model_id': _get_model_product,
    }


class MagentoProductAttribute(orm.Model):
    _name = 'magento.product.attribute'
    _description = "Magento Product Attribute"
    _inherit = 'magento.binding'
    # _inherits = {'attribute.attribute': 'openerp_id'}
    _rec_name = 'attribute_code'
    MAGENTO_HELP = "Defined on magento"

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['attribute_code'] = default.get('attribute_code', '') + 'Copy '
        return super(MagentoProductAttribute, self).copy(
            cr, uid, id, default, context=context)

    def _frontend_input(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for elm in self.browse(cr, uid, ids):
            field_type = elm.openerp_id.attribute_type
            map_type = {
                'char': 'text',
                'text': 'textarea',
                'float': 'price',
                'datetime': 'date',
                'binary': 'media_image',
                'selection': 'select',
            }
            res[elm.id] = map_type.get(field_type, field_type)
        return res

    _columns = {
        'openerp_id': fields.many2one(
            'attribute.attribute',
            string='Attribute',
            # required=True,
            ondelete='cascade'),
        'attribute_code': fields.char(
            'Code',
            required=True,
            size=200,),
        'scope': fields.selection(
            [('store', 'store'), ('website', 'website'), ('global', 'global')],
            'Scope',
            required=True,
            help=MAGENTO_HELP),
        'apply_to': fields.selection(
            [('simple', 'simple'), ],
            'Apply to',
            required=True,
            help=MAGENTO_HELP),
        'frontend_input': fields.function(
            _frontend_input,
            method=True,
            string='Frontend input',
            type='char',
            store=True,
            help="This field depends on OpenERP attribute 'type' field "
            "but used on Magento"),
        'set_id': fields.many2one(
            'magento.attribute.set',
            string='Attribute Set',
            required=True,
            ondelete='cascade'),
        'backend_id': fields.related(
            'set_id', 'backend_id',
            type='many2one',
            relation='magento.backend',
            string='Magento Backend',
            store=True,
            readonly=True),
        'frontend_label': fields.char(
            'Label', required=0, size=100, help=MAGENTO_HELP),
        # 'position':fields.integer('Position', help=MAGENTO_HELP),
        # 'group_id': fields.integer('Group', help=MAGENTO_HELP) ,
        # 'default_value': fields.char(
        #     'Default Value',
        #     size=10,
        #     help=MAGENTO_HELP),
        # 'note':fields.char('Note', size=200,
        #     help=MAGENTO_HELP),
        # 'entity_type_id':fields.integer('Entity Type',
        #     help=MAGENTO_HELP),
        # # boolean fields
        # 'is_visible_in_advanced_search':fields.boolean(
        #     'Visible in advanced search?', help=MAGENTO_HELP),
        # 'is_visible':fields.boolean('Visible?', help=MAGENTO_HELP),
        # 'is_visible_on_front':fields.boolean('Visible (front)?',
        #     help=MAGENTO_HELP),
        # 'is_html_allowed_on_front':fields.boolean('Html (front)?',
        #     help=MAGENTO_HELP),
        # 'is_wysiwyg_enabled':fields.boolean('Wysiwyg enabled?',
        #     help=MAGENTO_HELP),
        # 'is_global':fields.boolean('Global?', help=MAGENTO_HELP),
        # 'is_unique':fields.boolean('Unique?', help=MAGENTO_HELP),
        'is_required': fields.boolean('Required?', help=MAGENTO_HELP),
        # 'is_filterable':fields.boolean('Filterable?', help=MAGENTO_HELP),
        # 'is_comparable':fields.boolean('Comparable?', help=MAGENTO_HELP),
        # 'is_searchable':fields.boolean('Searchable ?', help=MAGENTO_HELP),
        # 'is_configurable':fields.boolean('Configurable?', help=MAGENTO_HELP),
        # 'is_user_defined':fields.boolean('User defined?', help=MAGENTO_HELP),
        #'used_for_sort_by':fields.boolean('Use for sort?', help=MAGENTO_HELP),
        # 'is_used_for_price_rules':fields.boolean('Used for pricing rules?',
        #     help=MAGENTO_HELP),
        # 'is_used_for_promo_rules':fields.boolean('Use for promo?',
        #     help=MAGENTO_HELP),
        # 'used_in_product_listing':fields.boolean('In product listing?',
        #     help=MAGENTO_HELP),
    }

    _defaults = {
        'scope': 'global',
        'apply_to': 'simple',
        # 'is_visible': True,
        # 'is_visible_on_front': True,
        # 'is_visible_in_advanced_search': True,
        # 'is_filterable': True,
        # 'is_searchable': True,
        # 'is_comparable': True,
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(attribute_code)',
         "Attribute with the same code already exists : must be unique")
    ]


@magento
class ProductAttributeAdapter(GenericAdapter):
    _model_name = 'magento.product.attribute'
    _magento_model = 'product_attribute'

    def delete(self, id):
        return self._call(
            '%s.remove' % self._magento_model, [int(id)])

    def search(self, set_id):
        attribute_ids = [item['attribute_id'] for item in self._call(
            '%s.list' % self._magento_model, [int(set_id)])]

        return attribute_ids

    def read(self, magento_id):
        return self._call(
            '%s.info' % self._magento_model, [int(magento_id)])


@magento
class ProductAttributeDeleteSynchronizer(MagentoDeleteSynchronizer):
    _model_name = ['magento.product.attribute']


@magento
class ProductAttributeExport(MagentoExporter):
    _model_name = ['magento.product.attribute']

    def _should_import(self):
        "Attributes in magento doesn't retrieve infos on dates"
        return False


@magento
class ProductAttributeExportMapper(ExportMapper):
    _model_name = 'magento.product.attribute'

    direct = [
            ('attribute_code', 'attribute_code'), # required
            ('frontend_input', 'frontend_input'),
            ('scope', 'scope'),
            # ('is_global', 'is_global'),
            # ('is_filterable', 'is_filterable'),
            # ('is_comparable', 'is_comparable'),
            # ('is_visible', 'is_visible'),
            # ('is_searchable', 'is_searchable'),
            # ('is_user_defined', 'is_user_defined'),
            # ('is_configurable', 'is_configurable'),
            # ('is_visible_on_front', 'is_visible_on_front'),
            # ('is_used_for_price_rules', 'is_used_for_price_rules'),
            # ('is_unique', 'is_unique'),
            ('is_required', 'is_required'),
            # ('position', 'position'),
            # ('group_id', 'group_id'),
            # ('default_value', 'default_value'),
            # ('is_visible_in_advanced_search', 'is_visible_in_advanced_search'),
            # ('note', 'note'),
            # ('entity_type_id', 'entity_type_id'),
        ]

    @mapping
    def frontend_label(self, record):
        #required
        return {'frontend_label': [{
                'store_id': 0,
                'label': record.frontend_label,
            }]}

"""
Magento Attribute Importer
"""


@magento
class ProductAttributeImport(MagentoImportSynchronizer):
    _model_name = ['magento.product.attribute']

    def _after_import(self, attribute_binding_id):
        """ Import the addresses """
        # env = self.environment
        # importer = env.get_connector_unit(ProductAttributeOptionBatchImport)
        get_unit = self.get_connector_unit_for_model
        option_importer = get_unit(ProductAttributeOptionBatchImport, 'magento.attribute.option')
        option_importer.run(attribute_binding_id,
                            self.mapper.data['magento_id'])
        return

    def run(self, magento_id, set_id, force):
        """ Run the synchronization

        :param magento_id: identifier of the record on Magento
        """
        self.magento_id = magento_id
        try:
            self.magento_record = self._get_magento_data()
        except IDMissingInBackend:
            return _('Record does no longer exist in Magento')
        binding_id = self._get_binding_id()

        if not force and self._is_uptodate(binding_id):
            return _('Already up-to-date.')
        self._before_import()

        # import the missing linked resources
        self._import_dependencies()

        self.magento_record['set_id'] = set_id
        self._map_data()

        if binding_id:
            record = self.mapper.data
            # special check on data before import
            self._validate_data(record)
            self._update(binding_id, record)
        else:
            record = self.mapper.data_for_create
            # special check on data before import
            self._validate_data(record)
            binding_id = self._create(record)

        self.binder.bind(self.magento_id, binding_id)

        self._after_import(binding_id)


@magento
class ProductAttributeBatchImport(DelayedBatchImport):
    _model_name = ['magento.product.attribute']

    def run(self, set_id, filters=None):
        """ Run the synchronization

        :param set_id: identifier of the attribute set on Magento
        """
        attribute_ids = self.backend_adapter.search(set_id)

        for attribute_id in attribute_ids:
            self._import_record(attribute_id, set_id=set_id)

    def _import_record(self, record_id, **kwargs):
        """ Import the record directly """
        product_attribute_import_record.delay(
            self.session,
            self.model._name,
            self.backend_record.id,
            record_id,
            **kwargs)


@magento
class ProductAttributeImportMapper(ImportMapper):
    _model_name = 'magento.product.attribute'

    direct = [('attribute_id', 'magento_id'),
              ('attribute_code', 'attribute_code'),
              ('frontend_input', 'frontend_input'),
              ('is_required', 'is_required'),
              ]

    # related field in model is used
    # @mapping
    # def backend_id(self, record):
    #     return {'backend_id': self.backend_record.id}

    @mapping
    def scope(self, record):
        if record.get('scope', False):
            return {'scope': record['scope']}

    @mapping
    def set_id(self, record):
        binder = self.get_binder_for_model('magento.attribute.set')
        binding_id = binder.to_openerp(record['set_id'])
        return {'set_id': binding_id}


@job
def product_attribute_import_batch(
        session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from Magento """
    if filters is None:
        filters = {}
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(ProductAttributeBatchImport)
    pool, cr, uid = session._pool, session.cr, session.uid
    attr_set_pool = pool.get('magento.attribute.set')
    attr_set_ids = attr_set_pool.search(cr, uid, [])
    for attr_set in attr_set_pool.browse(cr, uid, attr_set_ids):
        importer.run(attr_set.magento_id)


@job
def product_attribute_import_record(
        session, model_name, backend_id, magento_id, set_id, force=False):
    """ Import a record from Magento """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(MagentoImportSynchronizer)
    importer.run(magento_id, set_id, force=force)


# Set
class AttributeSet(orm.Model):
    _inherit = 'attribute.set'

    _columns = {
        'magento_bind_ids': fields.one2many(
            'magento.attribute.set',
            'openerp_id',
            string='Magento Bindings',),
    }


class MagentoAttributeSet(orm.Model):
    _name = 'magento.attribute.set'
    _description = ""
    _inherit = 'magento.binding'
    _rec_name = 'attributeSetName'
    SKELETON_SET_ID = '4'

    _columns = {
        'openerp_id': fields.many2one(
            'attribute.set',
            string='Attribute set',
            # required=True,
            ondelete='cascade'),
        'attributeSetName': fields.char(
            'Name',
            size=64,
            required=True),
        'skeletonSetId': fields.char(
            'Attribute set template',
            readonly=True),
    }

    _defaults = {
        'skeletonSetId': SKELETON_SET_ID,
    }


@magento
class AttributeSetAdapter(GenericAdapter):
    _model_name = 'magento.attribute.set'
    _magento_model = 'ol_catalog_product_attributeset'

    def create(self, data):
        """ Create a record on the external system """
        return self._call(
            'product_attribute_set.create',
            [data['attributeSetName'], data['skeletonSetId']])

    def delete(self, id):
        return self._call(
            'product_attribute_set.remove', [str(id)])


@magento
class AttributeSetDeleteSynchronizer(MagentoDeleteSynchronizer):
    _model_name = ['magento.attribute.set']


@magento
class AttributeSetExport(MagentoExporter):
    _model_name = ['magento.attribute.set']


@magento
class AttributeSetExportMapper(ExportMapper):
    _model_name = 'magento.attribute.set'

    direct = [
        ('attributeSetName', 'attributeSetName'),
        ('skeletonSetId', 'skeletonSetId'),
    ]

"""
Magento Import for Attribute Set

"""
@magento
class ProductAttributeSetImport(MagentoImportSynchronizer):
    _model_name = ['magento.attribute.set']


@magento
class ProductAttributeSetBatchImport(DelayedBatchImport):
    """ Import the Magento Product Attributs.

    For every product category in the list, a delayed job is created.
    Import from a date
    """
    _model_name = ['magento.attribute.set']

@magento
class ProductAttributeSetImportMapper(ImportMapper):
    _model_name = 'magento.attribute.set'

    direct = [('attribute_set_id', 'magento_id'),
              ('attribute_set_name', 'attributeSetName')
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


# Attribute option
class AttributeOption(orm.Model):
    _inherit = 'attribute.option'

    _columns = {
        'magento_bind_ids': fields.one2many(
            'magento.attribute.option',
            'openerp_id',
            string='Magento Bindings',),
    }


class MagentoAttributeOption(orm.Model):
    _name = 'magento.attribute.option'
    _description = "Attribute Option"
    _inherit = 'magento.binding'
    _rec_name = 'name'
    # _inherits = {'attribute.option': 'openerp_id'}

    _columns = {
        'openerp_id': fields.many2one(
            'attribute.option',
            string='Attribute option',
            # required=True,
            ondelete='cascade'),
        'name': fields.char(
            'Name',
            size=64,
            required=True),
        'value': fields.char('value', size=64),
        'is_default': fields.boolean('Is default'),
        'magento_attribute_id': fields.many2one(
            'magento.product.attribute',
            string='Magento Attribute',
            required=True,
            ondelete='cascade'),
        'magento_attribute_code': fields.related(
            'magento_attribute_id', 'attribute_code',
            type='char', size=32,
            string='Magento Attribute Code',
            readonly=True),
        'scale_id': fields.many2one(
            'product.scale', 'Product Scale'),
        'model_id': fields.many2one(
            'product.model', 'Product Model'),
        'race_edition_id': fields.many2one(
            'product.race.ed', 'Product Race Edition'),
        'driver_id': fields.many2one(
            'product.driver', 'Product Driver'),
    }

    _defaults = {
        'is_default': True,
    }


@magento
class AttributeOptionAdapter(GenericAdapter):
    _model_name = 'magento.attribute.option'
    _magento_model = 'product_attribute'

    def create(self, data):
        option_id = self._call(
            '%s.addOption' % 'ol_catalog_product_attribute',
            [data.pop('attribute'), data])
        return option_id

    def search_read(self, attribute_id):
        return self._call(
            '%s.options' % self._magento_model,
            [attribute_id])


@magento
class AttributeOptionDeleteSynchronizer(MagentoDeleteSynchronizer):
    _model_name = ['magento.attribute.option']


@magento
class AttributeOptionExport(MagentoExporter):
    _model_name = ['magento.attribute.option']


@magento
class AttributeOptionExportMapper(ExportMapper):
    _model_name = 'magento.attribute.option'

    direct = []

    @mapping
    def label(self, record):
        return {'label': [{
                'store_id': ['0'],
                'value': record.value,
            }]
        }

    @mapping
    def attribute(self, record):
        return {
            'attribute': record.magento_attribute_id.magento_id
        }

    @mapping
    def order(self, record):
        return {'order': 0}

    @mapping
    def is_default(self, record):
        return {'is_default': int(record.is_default)}

"""
Import option
"""

@magento
class ProductAttributeOptionImport(MagentoImportSynchronizer):
    _model_name = ['magento.attribute.option']

    def run(self, magento_data, force=None):
        """ Run the synchronization

        :param magento_id: identifier of the record on Magento
        """
        self.magento_record = magento_data
        self.magento_id = magento_data['magento_id']

        binding_id = self._get_binding_id()
        # _logger.debug("\n\n %s, binder: %s \n", self.__dict__, binding_id)

        if not force and self._is_uptodate(binding_id):
            return _('Already up-to-date.')
        self._before_import()

        # import the missing linked resources
        self._import_dependencies()

        self._map_data()

        if binding_id:
            record = self.mapper.data
            # special check on data before import
            self._validate_data(record)
            self._update(binding_id, record)
        else:
            record = self.mapper.data_for_create
            # special check on data before import
            self._validate_data(record)
            binding_id = self._create(record)

        self.binder.bind(self.magento_id, binding_id)

        self._after_import(binding_id)


@magento
class ProductAttributeOptionBatchImport(DelayedBatchImport):
    """ Import the Magento Product Attributs.

    For every product category in the list, a delayed job is created.
    Import from a date
    """
    _model_name = ['magento.attribute.option']

    #not used
    # def _prepare_magento_data(self, record_data, other_data):
    #     record_data.update(other_data)
    #     return

    def run(self, openerp_attribute_id, magento_attribute_id):
        record_datas = self.backend_adapter.search_read(magento_attribute_id)
        # _logger.debug("\n\n Attribute Id%s :\n Options %s", magento_attribute_id, record_datas)
        for record_data in record_datas:
            if not record_data.get('label', False):
                continue
            record_data.update(
                {'magento_attribute_id': magento_attribute_id,
                 'openerp_attribute_id': openerp_attribute_id,
                 'magento_id': record_data['value']})
            self._import_record(record_data)

    def _import_record(self, record_data):
        """ Delay the import of the records"""
        importer = self.environment.get_connector_unit(ProductAttributeOptionImport)
        importer.run(record_data, force=False)
        return


@magento
class ProductAttributeSetImportMapper(ImportMapper):
    _model_name = 'magento.attribute.option'

    direct = [('label', 'name'),
              ('value', 'value'),
              ('magento_attribute_id', 'magento_attribute_id'),
              ('magento_id', 'magento_id'),
              # ('openerp_attribute_id', 'attribute_id'),
              ]

    # @mapping
    # @only_create
    # def attribute_id(self, record):
    #     binder = self.get_binder_for_model('magento.product.attribute')
    #     attribute_id = binder.to_openerp(record['openerp_id'])
    #     return {'openerp_attribute_id': 'attribute_id'}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
