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
            h1, h2, tr, li {
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
            .shipment_name{
                border-bottom: 1px double black;
                width: 45%;
                font-size: 22px;
            }
        </style>
    </head>
    <body>
        %for obj in objects:
            %for shipment in get_sale_shipments(cr, uid, context):
            <h1 class="shipment_name">${shipment.name or 'No Shipment'}</h1>
            <table>
                <thead>
                    <tr>
                        <th>Product Name</th>
                       <th>Quantity</th>
                    </tr>
                </thead>
                <tbody>
                    %for group in get_res(cr, uid, obj.src_location_id, obj.dest_location_id, shipment.id, context=context):
                        <tr>
                            <td>${group.get('product_id') and group.get('product_id')[1] or "No "}</td>
                            <td>${group.get('product_qty')}</td>
                        </tr>
                    %endfor
                %endfor
                </tbody>
            </table>
            %endfor
    </body>
</html>