# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale order line report",
    "summary": "excel report",
    "version": "7.0.1.0.1",
    "category": "report",
    "website": "www.elico-corp.com",
    "author": "Elico corp",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_shipment",
    ],
    "data": [
        'report/report_sale_shipment_xls.xml',
    ]
}
