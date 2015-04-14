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
import csv

from openerp.osv import orm
from openerp.tools.translate import _

SUPPORT_FILE_TYPE = ('csv')


def unicode_dict_reader(utf8_data, **kwargs):
    sniffer = csv.Sniffer()
    pos = utf8_data.tell()
    sample_data = utf8_data.read(2048)
    utf8_data.seek(pos)
    dialect = sniffer.sniff(sample_data, delimiters=',;\t')
    dialect.quotechar = '"'
    try:
        csv_reader = csv.DictReader(utf8_data, dialect=dialect, **kwargs)
        import pdb
        pdb.set_trace()
        if sniffer.has_header(sample_data):
            next(csv_reader, None)
        for row in csv_reader:
            yield dict(
                [(key, unicode(value, 'utf-8'))
                    for key, value in row.iteritems()])
    except:
        raise Exception(_('Error when parsering the file.'))


class FileParser(object):
    '''
    Generic abstract class for defining parser for
    .csv, .cls or .clsx file format
    '''
    def __init__(self, ftype="csv", required_fields=None, **kwargs):
        '''
        :param ftype: the type of the file to be parsed
        :param header: the list of field names
        '''
        if ftype.lower() not in SUPPORT_FILE_TYPE:
            raise orm.except_orm(
                _('Warning'),
                _('Invalid file type %s.') % ftype)
        else:
            self.ftype = ftype.lower()[0:3]

        # store row data: list of dict.
        # normally you have the following fields in the dict:
        #   msg, valid(True, False)
        # normally this var is initialized in parse method
        self.result_row_list = []
        self.filebuffer = []

        # store the required fields
        self.fieldnames = []
        self.required_fields = required_fields

        # blacklist of the lines
        self.blacklist = []

    def _format(self, *args, **kwargs):
        return NotImplementedError

    def _pre(self, *args, **kwargs):
        '''
        Implement the pre-treatment in this funciton'''
        return NotImplementedError

    def _parse(self, *args, **kwargs):
        '''
        select the parse method to parse the file.
        '''
        res = None
        base_name = '_parse_'
        try:
            res = getattr(self, base_name + self.ftype)()
        except:
            raise orm.except_orm(
                _('Warning'),
                _('There is no parse method for this format %s,'
                    'Please make sure you have defined one!') % self.ftype)
        self.result_row_list = res
        return True

    def _validate(self, *args, **kwargs):
        '''check the validation of the data parsed
        * check the number of fields
        rewrite this method to implement more customised requirement.
        '''
        return NotImplementedError

    def _post(self, *args, **kwargs):
        '''actions performed after checking.'''
        return NotImplementedError

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

    def _cast_rows(self, *args, **kwargs):
        """
        Convert the self.result_row_list using
        the self.conversion_dict providen.
        We call here _from_xls or _from_csv
        depending on the self.ftype variable.
        """
        func = getattr(self, '_from_%s' % self.ftype)
        res = func(self.result_row_list, self.conversion_dict)
        return res
