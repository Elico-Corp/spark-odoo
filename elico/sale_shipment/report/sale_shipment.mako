<!DOCTYPE html>
<html>
<head>
    <title></title>
	<style type="text/css">
		body {
			margin-top: 30px;
			vertical-align: top;
			margin-bottom: 50px;
		}
		table td, table th {
			border-bottom: 1px solid black;
		}
		table.product_table {
			margin-bottom: 25px;
		}
		h2.h2_partner_name {
			margin-top: 20px;
			border-bottom: 1px double black;
		}
		h1, h2, tr {
			page-break-inside: avoid;
		}
		.sum_of_qty {
			text-align: right;
			width: 10%;
		}
		.product_name {
			text-align: left;
			width: 90%;
		}
	</style>
</head>
<body>
    %for obj in objects:
        <h1>${obj.name}</h1>
        <% group_orders = so_pool.read_group(cr, uid, [('sale_shipment_id', '=', obj.id)], ['name', 'partner_id'],['partner_id']) %>
        %for group in group_orders:
        	<% order_ids = so_pool.search(cr, uid, group['__domain']) %>
        	<h2 class="h2_partner_name">${group.get('partner_id', '') and group.get('partner_id')[1]}</h2>
        	<table class="product_table">
        		<tr>
        			<th class="product_name">Product Name</th>
        			<th class="sum_of_qty">Quantity</th>
        		</tr>
        		
        		<% order_lines = so_line_pool.read_group(cr, uid, [('order_id', 'in', order_ids)], ['product_id'], ['product_id']) %>
        		%for product_line in order_lines:
	        		<% sum_of_qty = get_sum_of_product_qty(cr, uid, product_line['__domain']) %>
	        			<tr class="content_tr">
	        				<td class="product_name">${product_line['product_id'][1]}</td>
	        				<td class="sum_of_qty">${ int(sum_of_qty) }</td>
	        			</tr>
        		%endfor
        	</table>
        %endfor
    %endfor
</body>
</html>