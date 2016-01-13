# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#
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
import logging

from openerp.addons.mmx_sale_status_mass_import.parser.csv_parser import \
    CSVParser
from openerp.osv import fields, orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

# this is the default field list.
DEFAULT_FIELDS = [
    'Partner Reference',
    'Address Reference',
    'Product Code',
    'Quantity'
]


class CSVMassImportParser(CSVParser):
    '''This class is more specific for this wizard'''
    def __init__(self, cr, uid, pool, context=None, *args, **kwargs):
        self.cr = cr
        self.uid = uid
        self.pool = pool
        self.blacklist = []
        return super(CSVMassImportParser, self).__init__(
            *args, **kwargs)

    def _check_product_exist(self, context=None):
        '''
        Check whether the product column of the file valid or not.

        :param result: list of dict
        :return: string of the log message, if return None, succeed.
        '''
        cr, uid = self.cr, self.uid
        # TOFIX: to make this more generic.
        # TODO: the list should be the line number of the initial file.
        index = 1
        self.blacklist = self.blacklist or []
        product_obj = self.pool['product.product']
        for r in self.result_row_list:
            if not r.get('msg'):
                r['msg'] = ''
            index += 1
            code = r.get('Product Code')
            if not code:
                r['msg'] += 'Line %d: empty Product Code!\n' % index
                self.blacklist.append(index)
                r['valid'] = False
                continue
            if not product_obj.search(
                    cr, uid,
                    [('default_code', '=', code)], context=context):
                r['msg'] += 'Line %d: No such Product %s in system!\n' % (
                    index, code)
                r['valid'] = False
                self.blacklist.append(index)
                continue
        self.blacklist = list(set(self.blacklist))
        return (r['msg'], self.blacklist)

    def _check_partner_exist(self, context=None):
        '''
        Check whether the partner columns are valid or not.

        :return: string of the log message, if return None, means succeed.
        '''
        # TOFIX: to make this more generic, for the column name is hard-coded.
        cr, uid = self.cr, self.uid
        self.blacklist = self.blacklist or []
        index = 1
        partner_obj = self.pool['res.partner']
        for r in self.result_row_list:
            index += 1
            partner_ref = r.get('Partner Reference')
            address_ref = r.get('Address Reference')
            if not partner_ref:
                r['msg'] += 'Line %d: empty Partner Reference!\n' % index
                self.blacklist.append(index)
                r['valid'] = False
                continue
            if not address_ref:
                r['msg'] += 'Line %d: empty Address Reference!\n' % index
                self.blacklist.append(index)
                r['valid'] = False
                continue
            # check if address exists
            if not partner_obj.search(
                    cr, uid, [('ref', '=', address_ref)],
                    context=context):
                r['msg'] += ('Line %d: '
                             'address reference:%s '
                             'doesnt exist!\n') % (
                                 index, address_ref)
                self.blacklist.append(index)
                r['valid'] = False
                continue
            # check if partner exists
            if not partner_obj.search(
                    cr, uid, [('ref', '=', partner_ref)],
                    context=context):
                r['msg'] += ('Line %d: '
                             'partner reference:%s '
                             'doesnt exist!\n') % (
                                 index, partner_ref)
                self.blacklist.append(index)
                r['valid'] = False
                continue
        self.blacklist = list(set(self.blacklist))
        return (r['msg'], self.blacklist)

    def _validate(self, context=None, *args, **kwargs):
        '''rewrite this method to add more specific
        checks on the data
        '''
        # set the default value for self.result_row_list
        for r in self.result_row_list:
            r.update({
                'valid': True,
                'msg': '',
                'so_id': False,
                'product_id': False,
                'address_id': False,
                'sol_id': False
            })
        # update the class variable: self.result_row_list
        # add blacklist and msg.
        self._check_product_exist(context=context)
        self._check_partner_exist(context=context)

        # check required fields
        parsed_cols = self.result_row_list[0].keys()
        for f in self.required_fields:
            if f not in parsed_cols:
                raise orm.except_orm(
                    _('Warning'),
                    _('Please make sure the columns names are correct!\n'
                        'You must have these fields:%s') % str(
                            self.required_fields))
        # TODO: more format and field type checkings.
        return True

    def parse(self, filebuffer, *args, **kwargs):
        """
        This will be the method that will be called by wizard, button and so
        to parse a filebuffer by calling successively all the private method
        that need to be define for each parser.
        Return:
             [] of rows as {'key':value}

        """
        if filebuffer:
            self.filebuffer = filebuffer
        else:
            raise Exception(_('No buffer file given.'))
        self._parse(*args, **kwargs)
        self._validate(*args, **kwargs)
        return self.result_row_list


class WizardQuotationMassImport(orm.TransientModel):
    _name = 'wizard.quotation.mass.import'
    _columns = {
        'name': fields.char('name', size=32),
        'date': fields.date(
            'Date', required=True,
            help="This date is used for Sale order."),
        'shop_id': fields.many2one(
            'sale.shop', 'Shop', required=True),
        'import_file': fields.binary(
            'Import file', required=True),
        'log_message': fields.text(
            'Log message'),
        'new_quotation': fields.boolean("Create new quotation?")
    }

    _defaults = {
        'date': fields.date.context_today,
        'new_quotation': False
    }

    def check_import_valid(self, cr, uid, wizard, context=None):
        '''This method is to check whether information is valid or not:
        * product exists or not
        * partner exists or not

        :return: True or False
        '''
        # instance the parser object
        # header is default fields.
        parser = CSVMassImportParser(
            cr=cr, uid=uid, required_fields=DEFAULT_FIELDS,
            pool=self.pool, context=context)
        parser.parse(wizard.import_file)

        # get all logging message
        msg = ''
        for r in parser.result_row_list:
            msg += r.get('msg')

        # write back the log msg
        wizard.write({'log_message': msg}, context=context)
        return (msg, parser)

    def force_import(
            self, cr, uid, ids, ftype='csv', context=None):
        '''
        import the file.
        '''
        if isinstance(ids, (tuple, list)):
            wizard_id = ids and ids[0] or False
        else:
            wizard_id = ids
        assert wizard_id, 'No wizard ID!'

        # get file stream result_row_list
        wizard = self.browse(cr, uid, wizard_id, context=context)

        partner_obj = self.pool['res.partner']
        sale_obj = self.pool['sale.order']
        sol_obj = self.pool['sale.order.line']
        product_obj = self.pool['product.product']

        msg, parser = self.check_import_valid(cr, uid, wizard, context=context)

        '''
        If user has "new quotation" checkbox checked, system will create
        New quotations for all the lines in the csv file.(one quotation per
            address partner)
        If checkbox "New Quotation" is not checked:
            1- system will first check if there are SO
            (quotation lines) in system whose whose
            partner exists in the CSV file and with "is_imported" check box
            checked, if so, delete them.

            2- create new quotations or quotation lines per address partner
            based all the lines in the csv file.
        '''
        partner_address_refs = [l.get(
            'Address Reference') for l in parser.result_row_list]
        csv_partner_address_list = partner_obj.search(
            cr, uid, [('ref', 'in', partner_address_refs)],
            context=context)
        if not wizard.new_quotation:
            # starting the clean up of old quotations lines
            file_so_ids = sale_obj.search(
                cr, uid, [('state', '=', 'draft'), (
                    'is_imported', '=', True),
                    ('partner_shipping_id', 'in', csv_partner_address_list)],
                context=context)

            sol_to_delete_ids = sol_obj.search(
                cr, uid,
                [('order_id', 'in', file_so_ids),
                 ('so_state', '=', 'draft'), ('is_imported', '=', True)],
                context=context)

            if sol_to_delete_ids:
                sol_obj.unlink(cr, uid, sol_to_delete_ids, context=context)
            # finished clean up

        line_nb = 1
        for r in parser.result_row_list:
            line_nb += 1
            # pass the invalid ones, this var is initialized when parse
            # this file.
            assert 'valid' in r, \
                'The "valid" should be in the result_row_list!'
            if not r['valid']:
                continue

            # get address reference
            address_ref = r.get('Address Reference')
            address_ids = partner_obj.search(
                cr, uid, [('ref', '=', address_ref)],
                context=context)
            assert address_ids, 'No Address found'
            ' by reference: %s' % address_ref
            address_id = address_ids[0]

            # update the address_id for the self.result_row_list
            r['address_id'] = address_id

            # get partner/billing reference
            partner_ref = r.get('Partner Reference')
            partner_ids = partner_obj.search(
                cr, uid, [('ref', '=', partner_ref)],
                context=context)
            assert partner_ids, 'No Partner found'
            ' by reference: %s' % partner_ref
            partner_id = partner_ids[0]

            # update the address_id for the self.result_row_list
            r['partner_id'] = partner_id

            if not wizard.new_quotation:
                # search for the SOs to be updated.
                # state is 'draft' and with check box checked.
                so_ids = sale_obj.search(
                    cr, uid,
                    [
                        ('state', '=', 'draft'),
                        ('is_imported', '=', True),
                        ('partner_shipping_id', '=', address_id)
                    ], context=context)
                so_id = so_ids and so_ids[0] or False
                # update the so_id for self.result_row_list
                r['so_id'] = so_id
                # TODO log warning when more than 2 so are found

            # create new quotation if we don't find any in system.
            # or new_quotation is True
            if not r['so_id'] or wizard.new_quotation:
                so_id = self.create_new_quotation(
                    cr, uid, partner_id, address_id,
                    wizard.shop_id and wizard.shop_id.id,
                    wizard.date, new_quotation=wizard.new_quotation,
                    context=context)

            # prepare sol according to the data.
            product_code = r.get('Product Code')
            quantity = 0
            try:
                quantity = float(r.get('Quantity'))
            except TypeError:
                raise orm.except_orm(
                    _('Quantity is empty !'),
                    _('Line %s of your file has no quantity.') % (
                        line_nb)
                )
            except Exception:
                raise orm.except_orm(
                    _('Something went wrong !'),
                    _('Line %s seems wrong.') % (
                        line_nb)
                )

            product_ids = product_obj.search(
                cr, uid, [('default_code', '=', product_code)],
                context=context)
            product_id = product_ids[0]

            # update the product_id for self.result_row_list
            r['product_id'] = product_id

            so_record = sale_obj.browse(
                cr, uid, so_id, context=context)
            if not wizard.new_quotation:
                # go through the so's sol
                # check if product already existing in one of them.
                for l in so_record.order_line:
                    # just for later checking.
                    if r.get('sol_id') != l.id:
                        _logger.error(
                            'There should not be existing '
                            'data with another sol_id.')
                        # TODO to save the file for checking the reason

                    # if exists, update the quantity in the csv
                    assert l.product_id, 'The product is None in the sol!'
                    if l.product_id.id == product_id:
                        self.update_quotation_line(
                            cr, uid, so_id, product_id,
                            quantity, l.id, context=context)
                        # update the sol_id for self.result_row_list
                        r['sol_id'] = l.id
                        break
            # if line doesn't exist in system, create a new one
            # or new_quotation is True, create anyway
            if not r.get('sol_id') or wizard.new_quotation:
                sol_id = self.create_new_quotation_line(
                    cr, uid, so_id, product_id,
                    quantity, new_quotation=wizard.new_quotation,
                    context=context)
                r['sol_id'] = sol_id
            so_record.write({}, context=context)

        # write back the log msg
        wizard.write(
            {'log_message': msg}, context=context)
        if msg:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Quotation Mass Import',
                'res_model': 'wizard.quotation.mass.import',
                'context': {
                    'log_message': msg},
                'res_id': wizard_id,
                'target': 'new',
                'view_mode': 'form'
            }
        else:
            return True

    def prepare_quotation_vals(
            self, cr, uid, partner_id, address_id,
            shop_id=False, date=None, new_quotation=False, context=None):
        '''Prepare the updating data for quotation.

        if with checkbox: new quotation checked, we create all the sale
        quotation per shipment address.(is_imported is False)
        '''
        so_obj = self.pool['sale.order']
        so_val = so_obj.onchange_partner_id(
            cr, uid, [], partner_id, context=context)['value']
        so_val.update({
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': address_id,
            'state': 'draft',
            'is_imported': not new_quotation
        })
        if shop_id:
            so_val['shop_id'] = shop_id
        if date:
            so_val['date_order'] = date
        return so_val

    def create_new_quotation(
            self, cr, uid, partner_id, address_id,
            shop_id=False, date=None, new_quotation=False, context=None):
        '''create new empty quotation'''

        so_obj = self.pool['sale.order']
        vals = self.prepare_quotation_vals(
            cr, uid, partner_id, address_id, shop_id=shop_id,
            date=date, new_quotation=new_quotation, context=context)
        so_id = so_obj.create(cr, uid, vals, context=context)
        return so_id

    def update_quotation(
            self, cr, uid, so_id, partner_id, address_id,
            shop_id=False, date=None, context=None):
        '''update existing quotation'''
        assert so_id, 'Must have a sale order to be updated.'
        so_obj = self.pool['sale.order']
        vals = self.prepare_quotation_vals(
            cr, uid, partner_id, address_id, shop_id=shop_id,
            date=date, context=context)

        so_id = so_obj.write(cr, uid, so_id, vals, context=context)
        return so_id

    def prepare_quotation_line_vals(
            self, cr, uid, so_id, product_id, quantity,
            new_quotation=False, context=None):
        '''Prepare the data to be update in the sol.

        if with checkbox: new quotation checked, we create all the sale
        quotation per shipment address.(is_imported is False)
        '''
        assert so_id, 'Data error, must have SO id to get information'
        so_obj = self.pool['sale.order']
        sol_obj = self.pool['sale.order.line']
        so = so_obj.browse(cr, uid, so_id, context=context)
        line_val = sol_obj.product_id_change(
            cr, uid, [],
            so.pricelist_id.id, product_id,
            qty=quantity, partner_id=so.partner_id.id,
            date_order=so.date_order,
            context=context)['value']
        line_val.update({
            'product_id': product_id,
            'order_id': so_id,
            'product_uom_qty': quantity,
            'so_state': 'draft',
            'is_imported': not new_quotation
        })
        return line_val

    def update_quotation_line(
            self, cr, uid, so_id, product_id, quantity, sol_id, context=None):
        '''Update the existing quotation line'''

        so_obj = self.pool['sale.order']
        line_val = self.prepare_quotation_line_vals(
            cr, uid, so_id, product_id, quantity, context=context)

        # don't update the description
        if 'name' in line_val:
            del line_val['name']

        so_obj.write(
            cr, uid, so_id, {'order_line': [(1, sol_id, line_val)]},
            context=context)
        return sol_id

    def create_new_quotation_line(
            self, cr, uid, so_id, product_id, quantity, new_quotation=None,
            context=None):
        sol_obj = self.pool['sale.order.line']
        line_val = self.prepare_quotation_line_vals(
            cr, uid, so_id, product_id, quantity, new_quotation=new_quotation,
            context=context)
        sol_id = sol_obj.create(cr, uid, line_val, context=context)
        return sol_id
