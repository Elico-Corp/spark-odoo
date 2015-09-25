# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
#    Eric Caudal <eric.caudal@elico-corp.com>

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
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from openerp.osv import osv


_logger = logging.getLogger(__name__)
recorder = {}


def call_to_key(method, arguments):
    """ Used to 'freeze' the method and arguments of a call to Coswin
    so they can be hashable; they will be stored in a dict.

    Used in both the recorder and the tests.
    """
    def freeze(arg):
        if isinstance(arg, dict):
            items = dict((key, freeze(value)) for key, value
                         in arg.iteritems())
            return frozenset(items.iteritems())
        elif isinstance(arg, list):
            return tuple([freeze(item) for item in arg])
        else:
            return arg

    new_args = []
    for arg in arguments:
        new_args.append(freeze(arg))
    return (method, tuple(new_args))


def record(method, arguments, result):
    """ Utility function which can be used to record test data
    during synchronisations. Call it from CoswinOracleAdapter._call

    Then ``output_recorder`` can be used to write the data recorded
    to a file.
    """
    recorder[call_to_key(method, arguments)] = result


def output_recorder(filename):
    import pprint
    with open(filename, 'w') as f:
        pprint.pprint(recorder, f)
    _logger.debug('recorder written to file %s', filename)


# class ICOPSLocation(object):

#     def __init__(self, location, db_name, username, password):
#         self.location = location
#         self.db_name = db_name
#         self.username = username
#         self.password = password


class GenericAdapter(CRUDAdapter):

    """ External Records Adapter for Coswin """

    def __init__(self, environment):
        """

        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(GenericAdapter, self).__init__(environment)
        # self.icops = ICOPSLocation(self.backend_record.icops_server,
        #                              self.backend_record.backup_server)

    def search(self, filters=None):
        """ Search records according to some criterias
        and returns a list of ids """
        raise NotImplementedError

    def read(self, id, attributes=None):
        """ Returns the information of a record """
        raise NotImplementedError

    def search_read(self, filters=None):
        """ Search records according to some criterias
        and returns their information"""
        raise NotImplementedError

    def create(self, data):
        """ Create a record on the external system """
        raise NotImplementedError

    def write(self, id, data):
        """ Update records on the external system """
        raise NotImplementedError

    def delete(self, id):
        """ Delete a record on the external system """
        raise NotImplementedError

    def _write(self, text):
        return True


class ICOPSAdapter(GenericAdapter):

    _model_name = None

    def __init__(self, environment):
        super(GenericAdapter, self).__init__(environment)
        self._icops = None
        self._backend_to = None

    def _get_pool(self):
        raise NotImplementedError

    def create(self, data):
        sess = self.session
        # always set backward to true for creation so it won't go backward
        context = {'icops': True, 'backward': True}
        icops_uid = self._backend_to.icops_uid.id
        pool = self._get_pool()
        return pool.create(
            sess.cr, icops_uid, data, context)

    def write(self, id, data):
        sess = self.session
        context = {'icops': True}
        if 'backward' in self.session.context:
            context.update({'backward': True})
        icops_uid = self._backend_to.icops_uid.id
        pool = self._get_pool()
        try:
            pool.write(sess.cr, icops_uid, id, data,
                       context)
        except:
	    return
            raise osv.except_osv(
                'ICOPS Error',
                'You can only add a new record\
                 from the original object..')

    def delete(self, id):
        sess = self.session
        context = {'icops': True}
        if 'backward' in self.session.context:
            context.update({'backward': True})
        icops_uid = self._backend_to.icops_uid.id
        pool = self._get_pool()
        pool.unlink(sess.cr, icops_uid, [id],
                    context)
