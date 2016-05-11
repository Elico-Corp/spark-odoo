# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Total Number Of Lines",
    "summary": "Add the total lines on the right top at PO/SO/DO",
    "version": "7.0.1.0.2",
    "category": "tools",
    "website": "www.elico-corp.com",
    "author": "Elico corp",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'description': """
    This module extends the functionality of Stock Picking and add the “Total number of lines” on top right:
    * SO/Quotation line;
    * PO/Quotation line;
    * Delivery order line;
    """,
    "depends": [
        "purchase",
        "sale",
        'stock',
    ],
    "data": [
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
    ]

}
