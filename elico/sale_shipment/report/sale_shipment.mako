<!DOCTYPE html>
<html>
<head>
    <title></title>
    <style type="text/css">
        body {
            vertical-align: top;
            margin-bottom: 50px;
        }
        ul {
            padding: 0;
            display: block;
        }
        li {
            border: 1px solid black;
            float: left;
            display: block;
            padding: 3px;
        }
        .product_div {
            margin-bottom: 80px;
        }
        .shipment_name {
            border-bottom: double black;
            width: 30%;
        }
        h1, h2, ul, li {
            page-break-inside: avoid;
        }
        .sum_of_qty {
            text-align: right;
            width: 10%;
        }
        .product_name {
            text-align: left;
            width: 80%;
        }
        .sum_of_qty {
            text-align: left;
            width: 10%;
        }
        .col_name {
            width: 15%;
            border: none;
            font-weight: bold;
            font-size: 15px;
            vertical-align: bottom;
        }
        .col_content {
            width: 30%;
            text-align: left;
            border: none;
            font-size: 15px;
            vertical-align: bottom;
        }
        .info_div {
            width: 100%;
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
                    <div class="info_div">
                        <ul>
                            <li class="col_name">Customer:</li>
                            <li class="col_content">${group.get('partner_id', '') and group.get('partner_id')[1]}</li>
                            <li class="col_name">Package:</li>
                            <li class="col_content">${pack_move_group.get('tracking_id', '') and pack_move_group.get('tracking_id', '')[1] or 'No Package'}</li>
                        </ul>
                    </div>
                    <div class="product_div">
                        <ul>
                            <li class="product_name">Product Name</li>
                            <li class="sum_of_qty">Quantity</li>
                        </ul>
                        <% pack_move_ids = move_pool.search(cr, uid, pack_move_group['__domain']) %>
                        <% move_lines = move_pool.read_group(cr, uid, [('id', 'in', pack_move_ids)], ['product_id', 'product_qty'], ['product_id']) %>
                            %for product_line in move_lines:
                                <ul class="content_tr">
                                    <li class="product_name">${product_line['product_id'][1]}</li>
                                    <li class="sum_of_qty">${ product_line.get('product_qty') }</li>
                                </ul>
                            %endfor
                    </div>
                    %endfor
        %endfor
    %endfor
</body>
</html>