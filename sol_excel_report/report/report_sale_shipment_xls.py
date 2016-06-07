# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import xlwt
import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
import logging
_logger = logging.getLogger(__name__)

_ir_translation_name = 'sale.shipment.xls'


class sale_order_list_xls_parser(report_sxw.rml_parse):
    # model for export excel


    def __init__(self, cr, uid, name, context):
        super(sale_order_list_xls_parser, self).__init__(
            cr, uid, name, context=context)
        sol_obj = self.pool.get('sale.shipment')
        self.context = context
        wanted_list = sol_obj._report_xls_fields(cr, uid, context)
        template_changes = sol_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) \
            or src


class sale_order_list_xls(report_xls):


    def __init__(self, name, table, rml=False, parser=False, header=True, store=False,):
        super(sale_order_list_xls, self).__init__(
            name, table, rml, parser, header, store)

    def get_result(self, cr, uid, name, context):
        sql = """
        select b.default_code, b.name_template, c.name, sum(a.final_qty) as  final_qty
        from sale_order_line a, product_product b, res_partner c
        where a.product_id = b.id and a.order_partner_id = c.id
        group by b.default_code, b.name_template, c.name
        """
        self.env.cr.execute(sql)
        result_rows = self.env.cr.fetchall()
        added_partners = []
        titles = []
        for row in result_rows:
            partner = row[2]
            if not row[2] in added_partners:
                titles.append(partner)

        excel_title = ['product_code', 'prodect_name']
        for row in titles:
            excel_title.append(row)

        excel_data = [excel_title]
        for row in result_rows:
            excel_row = []
            excel_row[0] = row[0]
            excel_row[1] = row[1]
            partner = row[2]
            pos = titles.indexof(partner)
            excel_row[pos + 2] = row[3]
            excel_data.append(excel_row)

    def generate_xls_report(self, _p, _xs, data, saleshipment_objects, wb):
        result = []
        for sols in saleshipment_objects.sol_ids:
            for sol in sols:
                obj_dict = {}
                obj_dict['product_default_code'] = sol.product_default_code
                obj_dict['product_id'] = sol.product_id.name
                obj_dict['order_partner_id'] = sol.order_partner_id.name
                obj_dict['product_uom_qty'] = sol.product_uom_qty
                obj_dict['final_qty'] = sol.final_qty
                sol_obj = OrderedDict(obj_dict)
                result.append(sol_obj)

        df = pd.DataFrame(result)

        table_SO_df = pd.pivot_table(
            df,
            index=["product_default_code", "product_id"],
            columns=['order_partner_id'],
            values=["product_uom_qty"],
            aggfunc=[np.sum],
            fill_value=0,
            margins=True,)
        table_SO = table_SO_df.to_dict('split')

        ws = wb.add_sheet('Pivot table SO Qty')
        ws.portrait = False
        style2 = xlwt.XFStyle()
        ws.set_fit_num_pages(1)
        ws.set_fit_height_to_pages(0)

        ws.write(0, 0, 'Sum – SO Qty', style2)
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

        table_final_df = pd.pivot_table(
            df,
            index=["product_default_code", "product_id"],
            columns=['order_partner_id'],
            values=["final_qty"],
            aggfunc=[np.sum],
            fill_value=0,
            margins=True,)
        table_Final = table_final_df.to_dict('split')

        ws = wb.add_sheet('Pivot table Final Qty')
        ws.portrait = False
        style2 = xlwt.XFStyle()
        ws.set_fit_num_pages(1)
        ws.set_fit_height_to_pages(0)

        ws.write(0, 0, 'Sum - Final Qty', style2)
        ws.write(0, 2, 'Customer', style2)
        ws.write(1, 0, 'Code', style2)
        ws.write(1, 1, 'Product', style2)

        for i, col in enumerate(table_Final['columns']):
            col_name = (
                'Total' if i == len(table_Final['columns']) - 1 else col[2])
            ws.write(1, i + 2, col_name, style2)

        for i, row in enumerate(table_Final['index']):
            ws.write(i + 2, 0, (
                'Total' if i == len(table_Final['index']) - 1 else row[0]),
                style2)
            ws.write(i + 2, 1, row[1], style2)

        for i, sums in enumerate(table_Final['data']):
            for j, data in enumerate(sums):
                ws.write(i + 2, j + 2, data, style2)

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
