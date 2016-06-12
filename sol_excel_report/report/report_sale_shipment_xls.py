# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
_logger = logging.getLogger(__name__)
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import pandas as pd
except ImportError:
    _logger.debug('Cannot `import pandas`.')
try:
    import numpy as np
except ImportError:
    _logger.debug('Cannot `import numpy`.')
from datetime import datetime
from collections import OrderedDict
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from osv import osv, fields
from tools.translate import _

_ir_translation_name = 'sale.shipment.xls'


class sale_order_list_xls_parser(report_sxw.rml_parse):
    # model for export excel


    def __init__(self, cr, uid, name, context):
        super(sale_order_list_xls_parser, self).__init__(
            cr, uid, name, context=context)

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) \
            or src

class sale_order_list_xls(report_xls):


    def __init__(self, name, table, rml=False, parser=False, header=True, store=False,):
        super(sale_order_list_xls, self).__init__(
            name, table, rml, parser, header, store)

    def generate_xls_report(self, _p, _xs, data, saleshipment_objects, wb):
        result = []
        for sols in saleshipment_objects.sol_ids:
            if len(sols):
                for sol in sols:
                    obj_dict = {}
                    obj_dict['product_default_code'] = sol.product_default_code
                    obj_dict['product_id'] = sol.product_id.name
                    obj_dict['order_partner_id'] = sol.order_partner_id.name
                    obj_dict['product_uom_qty'] = sol.product_uom_qty
                    obj_dict['final_qty'] = sol.final_qty
                    sol_obj = OrderedDict(obj_dict)
                    result.append(sol_obj)
            else:
                raise osv.except_osv(
                    _('Empty Sale Order Line !'),
                    _('Please Assign Sale Order Line to Sale Shipment first!'))
        df = pd.DataFrame(result)
        self._create_pivot_sheet(wb, df, "product_uom_qty", 'Sum - SO Qty')
        self._create_pivot_sheet(wb, df, "final_qty", 'Sum - Final Qty')
        self._create_sol_list_sheet(wb, result)

    def _create_pivot_sheet(self, wb, df, value, tab_name):
        ws = wb.add_sheet(tab_name)
        table_SO_df = pd.pivot_table(
            df,
            index=["product_default_code", "product_id"],
            columns=['order_partner_id'],
            values=[value],
            aggfunc=[np.sum],
            fill_value=0,
            margins=True,)
        table_SO = table_SO_df.to_dict('split')

        ws.portrait = False
        style2 = xlwt.XFStyle()
        ws.set_fit_num_pages(1)
        ws.set_fit_height_to_pages(0)

        ws.write(0, 0, tab_name, style2)
        ws.write(0, 2, 'Customer', style2)
        ws.write(1, 0, 'Code', style2)
        ws.write(1, 1, 'Product', style2)

        for i, col in enumerate(table_SO['columns']):
            col_name = (
                # Normally, the "Total" column label can be defined by
                # passing the parameter margins_name to pivot_table but
                # it's not working so this is a workaround
                'Total' if i == len(table_SO['columns']) - 1 else col[2])
            ws.write(1, i + 2, col_name, style2)

        for i, row in enumerate(table_SO['index']):
            ws.write(i + 2, 0, (
                'Total' if i == len(table_SO['index']) - 1 else row[0]),
                style2)
            ws.write(i + 2, 1, row[1], style2)

        for i, sums in enumerate(table_SO['data']):
            for j, data in enumerate(sums):
                ws.write(i + 2, j + 2, data, style2)

    def _create_sol_list_sheet(self, wb, result):
        ws = wb.add_sheet('SOL List')
        ws.portrait = False
        style2 = xlwt.XFStyle()
        ws.set_fit_num_pages(1)
        ws.set_fit_height_to_pages(0)
        columns = [u'Code', u'product', u'Customer', u'SO Qty', u'Final Qty']
        ws.write(0, 0, columns[0], style2)
        ws.write(0, 1, columns[1], style2)
        ws.write(0, 2, columns[2], style2)
        ws.write(0, 3, columns[3], style2)
        ws.write(0, 4, columns[4], style2)
        for col in range(len(result)):
            ws.write(col + 1, 0, result[col]['product_default_code'], style2)
            ws.write(col + 1, 1, result[col]['product_id'], style2)
            ws.write(col + 1, 2, result[col]['order_partner_id'], style2)
            ws.write(col + 1, 3, result[col]['product_uom_qty'], style2)
            ws.write(col + 1, 4, result[col]['final_qty'], style2)

sale_order_list_xls('report.sale.shipment.xls', 'sale.shipment',
                    parser=sale_order_list_xls_parser)
