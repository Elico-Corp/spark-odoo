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

        .signature {
            vertical-align: top;
        }
        .page_break_margin {
            height:30px;
        }
    </style>
    

</head>
<body>
<% main_i = 0 %>
%for main_o in objects:
    %for o in announcement_pool.browse(cr, uid, map(int, main_o.sale_announcement_ids.split(','))):
        % if main_i > 0:
            <p style="page-break-after: always"/>
            <div class="page_break_margin"></div>
        % endif
        <% main_i = 1 %>
    	<h1 width="100%" style="text-align:center; clear:both;">Announcement<br />${o.name}</h1>
    	<table>
            <tr>
                <th width="15%">Customer:</th>
                <th width="45%">${main_o.partner_id.name}</th>
                <th width="40%" rowspan="4" class="signature">Authorized Signature &amp; Stamp</th>
            </tr>
            <tr>
                <th>Address:</th>
                <td>${display_address(main_o.partner_id)}</td>
            </tr>
            <tr>
                <th>Telephone:</th>
                <td>${main_o.partner_id.phone or main_o.partner_id.mobile or ""}</td>
            </tr>
            <tr>
                <th>Date:</th>
                <td>${time.strftime('%Y-%m-%d %H:%M:%S')}</td>
            </tr>
        </table>
        <p></p>
    	<table>
    		<tr>
                <th width="50%">Public Date</th>
    			<th width="50%">Responsible</th>
    		</tr>
    		<tr>
    			<th class="title">${o.public_date} </th>
    			<th class="title">${o.responsible_uid.name} </th>
    		</tr>
    	</table>
    	<p></p>
        <% i = 0 %>
        <% j = 0 %>
        <% max_i = 4 %>
    	% for product in o.product_ids:
            % if i == 0:
                %if j > 0:
                    </table>
                    <p></p>
                    <p style="page-break-after: always"/>
                    <div class="page_break_margin"></div>
                %endif
                <% j += 1 %>
                <table>
                    <tr>
                        <th width="20%">Product Image</th>
                        <th width="80%" class="product_info">Information</th>
                    </tr>
            % endif
            <% i += 1 %>
    			<tr>
    				<td><img class="product_image" src="${product.web_image}" /> </td>
    				<td class="product_info">
    					<div>Name: ${product.name}</div>
    					<div>${product.default_code and 'Code: '+product.default_code or ''}</div>
    					<div>${ product.brand_id and 'Brand: '+product.brand_id.name or ''}</div>
                        <% 
                        quantity = 1
                        partner = main_o.partner_id
                        pricelist = partner.property_product_pricelist
                        try:
                            price = pricelist_pool.price_get(
                                cr,uid,[pricelist.id], product.id, quantity,
                                partner=partner)[pricelist.id]
                        except:
                            price = 0.0
                        %>
                        <div>Price: ${formatLang(price, digits=get_digits(dp='Product Price'), currency_obj=pricelist.currency_id)}</div>
                             
    					%if product.availability_date:
    						<div>Available Date: ${product.availability_date[:7]}</div>
    					%endif
    				</td>
    			</tr>
            % if i == max_i:
                <% max_i = 7 %>
                <% i = 0 %>
            % endif
        %endfor
        </table>
    %endfor
%endfor
</body>
</html>


