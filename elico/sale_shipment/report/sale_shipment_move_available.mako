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
			margin: 0px;
			padding: 0px;
		}
		table.product_table {
			margin-bottom: 25px;
		}
		h1, tr {
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
		<% list_of_dicts = get_res_list(cr, uid, obj.stock_move_ids, filter_states=['confirmed', 'assigned']) %>
    		%for partner in get_unique_list_of_partner(list_of_dicts):
    		<% one_partner_move_list = filter_partner_moves(list_of_dicts, partner) %>
    		<h2> ${partner} </h2>
	        	<table class="product_table">
	        		<tr>
	        			<th class="product_name">Product Name</th>
	        			<th class="sum_of_qty">Quantity</th>
	        		</tr>
	        		
	        		%for move_line in one_partner_move_list:
		        			<tr class="content_tr">
		        				<td class="product_name">${ move_line.get('product_name', '') }</td>
		        				<td class="sum_of_qty">${ int(move_line.get('product_qty', 0)) }</td>
		        			</tr>
	        		%endfor
	        	</table>
	     %endfor
	%endfor
</body>
</html>