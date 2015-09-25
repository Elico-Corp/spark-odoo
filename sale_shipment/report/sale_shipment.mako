<!DOCTYPE html>
<html>
<head>
    <title></title>
    <style type="text/css">
        body {
                vertical-align: top;
                margin-bottom: 50px;
            }
            h1, h2, tr, td, th{
                page-break-inside: avoid;
            }
            table {
                width:100%;
                height: 100%;
                border: 1px solid #000;
                border-spacing: inherit;
                border-collapse: collapse;
            }

            th {
                text-align: center;
                border:1px solid black;
                padding: 3px;
            }

            td {
                border: 1px solid black;
                padding: 3px;
            }
            .table1 td, .table1 tr{
                border: none;
            }
            .table1{
                border: none;
            }
            .col_name {
                font-weight: bold;
                font-size: 15px;
                vertical-align: bottom;
            }
            .shipment_name{
                border-bottom: 1px double black;
                width: 45%;
                font-size: 22px;
                padding-top: 50px;
            }
            table.table2{
                margin-bottom: 10px;
            }
            table.table2 th{
                padding-top: 5px;
            }
    </style>
</head>
<body>
    %for obj in objects:
        <h1 class="shipment_name">${obj.name}</h1>
        <% group_moves = move_pool.read_group(cr, uid, [('sale_shipment_id', '=', obj.id)], ['name', 'partner_id'],['partner_id']) %>
        %for group in group_moves:
            <% move_ids = move_pool.search(cr, uid, group['__domain']) %>

                %for pack_move_group in move_pool.read_group(cr, uid, [('id', 'in', move_ids)], ['tracking_id'], ['tracking_id']):
                    <table class="table2">
                    <thead>
                        <tr>
                            <th style="border: none;">
                                <table class="table1">
                                    <tr>
                                        <td class="col_name">Customer:</td>
                                        <td>${group.get('partner_id', '') and group.get('partner_id')[1]}</td>
                                        <td class="col_name">Package:</td>
                                        <td>${pack_move_group.get('tracking_id', '') and pack_move_group.get('tracking_id', '')[1] or 'No Package'}</td>
                                    </tr>
                                </table>
                            </th>
                            <th style="border: none;"></th>
                        </tr>
                        <tr>
                            <th>Product Name</th>
                            <th>Quantity</th>
                        </tr>
                    </thead>
                        <% pack_move_ids = move_pool.search(cr, uid, pack_move_group['__domain']) %>
                        <% move_lines = move_pool.read_group(cr, uid, [('id', 'in', pack_move_ids)], ['product_id', 'product_qty'], ['product_id']) %>
                            <tbody>
                            %for product_line in move_lines:
                                <tr>
                                    <td>${product_line['product_id'][1]}</td>
                                    <td>${ product_line.get('product_qty') }</td>
                                </tr>
                            %endfor
                            </tbody>
                    </table>
                    %endfor
        %endfor
    %endfor
</body>
</html>