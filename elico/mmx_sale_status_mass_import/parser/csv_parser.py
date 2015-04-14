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
import tempfile
import base64

from openerp.osv import orm
from openerp.tools.translate import _

from parser import FileParser
from parser import unicode_dict_reader
from parser import SUPPORT_FILE_TYPE

if 'csv' not in SUPPORT_FILE_TYPE:
    SUPPORT_FILE_TYPE += ('csv')


class CSVParser(FileParser):
    '''
    a parser to parse csv format files.
    '''
    # def __init__(self, ftype="csv", header=None, **kwargs):
    #     self.default_fields = {
    #         ''
    #     }

    def _format(self, *args, **kwargs):
        return True

    def _pre(self, *args, **kwargs):
        '''
        Implement the pre-treatment in this funciton'''
        return True

    def _parse(self, *args, **kwargs):
        '''
        select the parse method to parse the file.
        '''
        res = None
        base_name = '_parse_'
        try:
            res = getattr(self, base_name + self.ftype)()
        except AttributeError:
            raise orm.except_orm(
                _('Warning'),
                _('There is no parse method for this format %s,'
                    'Please make sure you have defined one!') % self.ftype)
        except:
            # TODO how to handle this is a user error.
            raise orm.except_orm(
                _('Warning'),
                _('There is error when parsing this file.'))
        self.result_row_list = res
        return True

    def _validate(self, *args, **kwargs):
        '''check the validation of the data parsed
        * check the number of fields
        rewrite this method to implement more customised requirements.
        '''
        return True

    def _post(self, *args, **kwargs):
        """
        Cast row type depending on the file format .csv or .xls
        after parsing the file.
        """
        # self.result_row_list = self._cast_rows(*args, **kwargs)
        return True

    def _parse_csv(self):
        """
        :return: list of dict from csv file (line/rows)
        """
        csv_file = tempfile.NamedTemporaryFile()
        # in odoo, the binary file is default encoded in base64,
        # so we need to decode it.
        filebuffer = base64.b64decode(self.filebuffer)
        csv_file.write(filebuffer)
        csv_file.flush()
        try:
            with open(csv_file.name, 'rU') as fobj:
                reader = unicode_dict_reader(fobj)
                return list(reader)
        except:
            raise orm.except_orm(
                _('Warning'),
                _('Error occurs when opening the file.'))

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
        self._format(*args, **kwargs)
        self._pre(*args, **kwargs)
        self._parse(*args, **kwargs)
        self._validate(*args, **kwargs)
        self._post(*args, **kwargs)
        return self.result_row_list
