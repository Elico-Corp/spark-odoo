<html>
<head>
    <style type="text/css">
        table, th, td{
            border-left:1px solid  black;
            border-right:1px solid  black;
            border-top:1px solid  black;
            border-bottom:1px solid  black;
            border-collapse:collapse;
            cellpadding:"0"; 
            cellspacing:"0";
            word-break:break-all;
            text-align: center; 
        }

        table, tr {
            width: 100%;
        }

        .text_center{
            text-align:center;
        }

        .product_image {
            width: 100px;
        }

        .product_info {
            vertical-align: top;
            padding: 5px;
            text-align: left;
        }

        .page_break_margin {
            height:30px;
        }

    </style>


</head>
<body>

<h1 class=text_center>PRODUCT PURCHASE ORDERS</h1>
<h3>Report Date: <Print date>${time.strftime('%Y-%m-%d %H:%M:%S')}</h3>
    <%
    i = 0
    max_obj = 6
    %>
    %for pol in objects:
        %if i == 0 or i == max_obj:
            <table>
                <tr>
                    <th>Image</th>
                    <th>Product Info</th>
                    <th>Required<br />Quantity</th>
                </tr>
                %if i == max_obj:
                    <% max_obj = 7 %>
                    <p style="page-break-after: always"/>
                    <div class="page_break_margin"></div>
                %endif
                <%i = 0 %>
        %endif
            <tr>
                <td width="18%"><img />  <img src="${pol.product_id.web_image}" class="product_image" /> </td>
                <td width="52%" class="product_info">
                    <div><strong>[${pol.product_id.default_code and pol.product_id.default_code or 'N/A'}]</strong></div>
                    <div> ${pol.product_id.name} </div>
                    <div>Supplier: ${pol.order_id.partner_id.name}</div>
                    %if pol.job_number:
                        <div>Job Number: ${pol.job_number}</div>
                    %endif 
                    %if pol.note:
                        <div>Notes: ${pol.note}</div>
                    %endif 
                </td>
                <td width="15%">${pol.product_qty}</td>
            </tr>
        <% i += 1 %>
        %if i == max_obj:
            </table>
        %endif
    %endfor



<p></p>
</body>
</html>