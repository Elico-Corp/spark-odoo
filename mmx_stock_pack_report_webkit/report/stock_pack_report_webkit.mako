## -*- coding: utf-8 -*-
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

		table.first_table td, table.first_table th, table.first_table tr{
			border:1px black solid;
			margin: 0;
			text-align: center;
		}
		table.first_table {
			width:100%;
			margin-bottom: 20px;
		}
		table.pack_info_table {
			width:100%;
			border-bottom: 2px black double;
		}
		table.pack_info_table td, table.pack_info_table th {
			border: none;
		}
		table.pack_total_table {
			border-top: 2px black solid;
			width:100%;
		}
		th.total_bottom {
			text-align: left;
			width: 27%;
		}
	</style>
</head>
<body>
    %for obj in objects:
    		<h1>Delivery Order:${ obj.name or '' }</h1>
    		<table class="first_table">
	        		<tr>
	        			<th>Jounal</th>
	        			<th>Order(Origin)</th>
	        			<th>Schedule Date</th>
	        			<th>Weight</th>
	        		</tr>
	        		<tr>
	        			<td>${obj.stock_journal_id and obj.stock_journal_id.id or ''}</td>
	        			<td>${obj.origin or ''}</td>
	        			<td>${(obj.min_date or '').decode('utf-8') } </td>
	        			<td>${ 'weight' in obj._columns.keys() and obj.weight or '' }</td>
	        		</tr>
	        	</table>
	        	<% gw_total=0.0 %>
	        	<% nw_total=0.0 %>
	        	<% cbm_total=0.0 %>
	        	%for pack_obj in get_pack_objs(cr, uid, obj):
	        		<table class="pack_info_table">
		        		<tr>
		        			<th>Pack</th>
		        			<td>${ pack_obj and pack_obj.name or 'No Pack Specified'}</td>
		        			<th>GW(total)</th>
		        			<td>${ pack_obj and pack_obj.gross_weight or 0.0 }</td>
		        			<th>NW(total)</th>
		        			<td>${ get_pack_net_weight(cr, uid, pack_obj) }</td>
		        			<th>CBM</th>
		        			<td>${ '%0.3f' % (pack_obj and pack_obj.pack_cbm or 0.0)}</td>
		        		</tr>
		        	</table>
		        	<% nw_total += get_pack_net_weight(cr, uid, pack_obj) %>
		        	<% gw_total += (pack_obj and pack_obj.gross_weight or 0.0) %>
		        	<% cbm_total += (pack_obj and pack_obj.pack_cbm or 0.0) %>

		        	<table class="product_table">
	        		<tr>
	        			<td class="product_name">Description</td>
	        			<td >Serial Number</td>
	        			<td >Status</td>
	        			<td >Location</td>
	        			<td class="sum_of_qty">Quantity</td>
	        			<td>Uom</td>
	        		</tr>
	        		
	        		<% move_objs = get_pack_move(cr, uid, pack_obj, obj.id) %>
	        		%for move in move_objs:
		        			<tr class="content_tr">
		        				<td class="product_name">${ get_product_desc(move) }</td>
		        				<td class="sum_of_qty">${ (move.prodlot_id and move.prodlot_id.name) or '' }</td>
		        				<td> ${ move.state }</td>
		        				<td>${ move.location_id and move.location_id.name or '' }</td>
		        				<td>${ formatLang(move.product_qty) }</td>
		        				<td>${ move.product_uom.name }</td>
		        			</tr>
	        		%endfor
		        	</table>
	        	%endfor
    %endfor
    <table class="pack_total_table">
		<tr>
			<th class='total_bottom'>Total:</th>
			<th>GW(total)</th>
			<td>${ gw_total }</td>
			<th>NW(total)</th>
			<td>${ nw_total }</td>
			<th>CBM</th>
			<td>${ '%0.3f' %cbm_total }</td>
		</tr>
    	</table>
</body>
</html>