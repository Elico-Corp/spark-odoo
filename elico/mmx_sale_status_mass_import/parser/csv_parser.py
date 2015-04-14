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
