# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012-2013 Camptocamp SA
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

import openerp

from contextlib import contextmanager


class ConnectorSessionHandler(object):
    """ Allow to create a new `ConnectorSession` for a database.

    .. attribute:: db_name

        The name of the database we're working on

    .. attribute:: uid

        The User ID as integer

    .. attribute:: context

        The current OpenERP's context

    Usage::

        session_hdl = ConnectorSessionHandler(db_name, 1)
        with session_hdl.session() as session:
            # work with session
    """

    def __init__(self, db_name, uid, context=None):
        self.db_name = db_name
        self.uid = uid
        self.context = {} if context is None else context

    @contextmanager
    def session(self):
        """ Start a new session and ensure that the session's cursor is:

        * rollbacked on errors
        * commited at the end of the ``with`` context when no error occured
        * always closed at the end of the ``with`` context
        """
        db = openerp.sql_db.db_connect(self.db_name)
        session = ConnectorSession(db.cursor(),
                                   self.uid,
                                   context=self.context)

        try:
            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()


class ConnectorSession(object):
    """ Container for the OpenERP transactional stuff:

    .. attribute:: cr

        The OpenERP Cursor

    .. attribute:: uid

        The User ID as integer

    .. attribute:: pool

        The registry of models

    .. attribute:: context

        The current OpenERP's context

    .. attribute:: model

        Instance of the model we're working on

    A session can hold a reference to a model. This is useful
    in the connectors' context because a session's life is usually
    focused on a model (export a product, import a sale order, ...)
    """

    def __init__(self, cr, uid, context=None):
        self.cr = cr
        self.uid = uid
        self._pool = None
        self._context = context

    @contextmanager
    def change_user(self, uid):
        """ Temporarily change the user's session and restablish the
        normal user at closing,
        """
        current_uid = self.uid
        self.uid = uid
        yield self
        self.uid = current_uid

    @property
    def context(self):
        if self._context is None:
            user_obj = self.pool['res.users']
            self._context = user_obj.context_get(self.cr, self.uid)
        return self._context

    @property
    def pool(self):
        if self._pool is None:
            self._pool = openerp.pooler.get_pool(self.cr.dbname)
        return self._pool

    @contextmanager
    def change_context(self, values):
        """ Shallow copy the context, update it with values,
        then restore the original context on closing.

        :param values: values to apply on the context
        :type values: dict
        """
        original_context = self._context
        self._context = original_context.copy()
        self._context.update(values)
        yield
        self._context = original_context

    def commit(self):
        """ Commit the cursor """
        self.cr.commit()

    def rollback(self):
        """ Rollback the cursor """
        self.cr.rollback()

    def close(self):
        """ Close the cursor """
        self.cr.close()

    def search(self, model, domain, limit=None, offset=0, order=None):
        return self.pool[model].search(self.cr, self.uid, domain,
                                       limit=limit, offset=offset,
                                       order=order, context=self.context)

    def browse(self, model, ids):
        return self.pool[model].browse(self.cr, self.uid, ids, context=self.context)

    def read(self, model, ids, fields):
        return self.pool[model].read(self.cr, self.uid, ids, fields, context=self.context)

    def create(self, model, values):
        return self.pool[model].create(self.cr, self.uid, values, context=self.context)

    def write(self, model, ids, values):
        return self.pool[model].write(self.cr, self.uid, ids, values, context=self.context)

    def __repr__(self):
        return '<Session db_name: %s, uid: %d>' % (self.cr.dbname, self.uid)

    def is_module_installed(self, module_name):
        """ Indicates whether a module is installed or not
        on the current database.

        .. note:: Use a convention established for the connectors addons:
                  To know if a module is installed, it looks if an abstract
                  model with name ``module_name.installed`` is loaded in the
                  registry.
        """
        return bool(self.pool.get('%s.installed' % module_name))
