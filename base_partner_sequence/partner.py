# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Thomas Rehn <thomas.rehn at initos.com>
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class ResPartner(orm.Model):
    """Assigns 'ref' from a sequence on creation and copyfing"""

    _inherit = 'res.partner'

    def create(self, cr, uid, vals, context=None):
        context = context or {}
        sequence_obj = self.pool['ir.sequence']
        if not vals.get('ref') and self._needs_ref(
                cr, uid, vals=vals, context=context):
            vals['ref'] = sequence_obj.next_by_code(
                cr, uid, 'res.partner', context)
        return super(ResPartner, self).create(cr, uid, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        sequence_obj = self.pool['ir.sequence']
        if self._needs_ref(cr, uid, id=id, context=context):
            default['ref'] = sequence_obj.next_by_code(
                cr, uid, 'res.partner', context=context)
        return super(ResPartner, self).copy(cr, uid, id, default,
                                            context=context)

    def _needs_ref(self, cr, uid, id=None, vals=None, context=None):
        """
        Checks whether a sequence value should be assigned to a partner's 'ref'
        extend this method for specific need.

        :param cr: database cursor
        :param uid: current user id
        :param id: id of the partner object
        :param vals: known field values of the partner object
        :return: true iff a sequence value should be assigned to the
                      partner's 'ref'
        """
        return True

    def _get_default_ref(self, cr, uid, context=None):
        sequence_obj = self.pool['ir.sequence']
        if self._needs_ref(cr, uid, context=context):
            return sequence_obj.next_by_code(
                cr, uid, 'res.partner', context=context)
        return ''

    _columns = {
        'ref': fields.char(
            'Reference', size=64, readonly=True, required=True),
    }

    _defaults = {
        'ref': _get_default_ref
    }

    _sql_constraints = [
        ('ref_unique', 'unique(ref)',
            _('The partner reference should be unique!'))]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
