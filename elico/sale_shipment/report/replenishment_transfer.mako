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
                margin-top: 0;
                margin-bottom: 0;
                display: block;
            }
            li {
                border: 1px solid black;
                float: left;
                display: block;
                padding: 3px;
            }
            .product_div {
                margin-bottom: 25px;
            }
            h1, h2, tr, li {
                page-break-inside: avoid;
            }
            .product_name {
                text-align: left;
                width: 80%;
            }
            .sum_of_qty {
                text-align: right;
                width: 10%;
            }
            .shipment_name {
                border-bottom: double black;
                width: 30%;
            }
        </style>
    </head>
    <body>
        %for obj in objects:
            %for shipment in get_sale_shipments(cr, uid, context):
            <h1 class="shipment_name">${shipment.name or 'No Shipment'}</h1>
            <div class="product_div">
                <ul>
                    <li class="product_name">Product Name</li>
                    <li class="sum_of_qty">Quantity</li>
                </tr>
                    %for group in get_res(cr, uid, obj.src_location_id, obj.dest_location_id, shipment.id, context=context):
                        <tr>
                            <li class="product_name">${group.get('product_id') and group.get('product_id')[1] or "No Product Name"}</li>
                            <li class="sum_of_qty">${group.get('product_qty')}</li>
                        </tr>
                    %endfor
                %endfor
            </div>
            %endfor
    </body>
</html>