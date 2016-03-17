# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv


class MMXMagentoAttributeSet(osv.osv):
    _inherit = 'magento.attribute.set'
    _name = 'magento.attribute.set'

    def name_get(self, cr, uid, ids, context=None):
        result = []
        if type(ids) not in (list, tuple):
            ids = [ids]
        for s in self.browse(cr, uid, ids, context=context):
            result.append((s.id, "%s (%s)" % (s.attributeSetName, s.backend_id.name)))
        return result
