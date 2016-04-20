# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sum Of Qty And Final Qty",
    "version": "7.0.1.0.2",
    "website": "www.elico-corp.com",
    "author": "Elico corp",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
        "stock",
        "purchase",
    ],
    "data": [
        'views/stock_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
    ]
}
