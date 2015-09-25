import time
from openerp.report import report_sxw


class sale_announcement(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_announcement, self).__init__(cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'time':            time,
            'cr':              cr,
            'uid':             uid,
        })

report_sxw.report_sxw(
    'report.sale_announcement_webkit1',
    'sale.announcement',
    'addons/mmx_sale_ann_webkit/report/sale_announcement.mako',
    parser=sale_announcement,)
