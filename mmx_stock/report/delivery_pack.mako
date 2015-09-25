<html>
<head>
    <style type="text/css">
        ${css}
        
        table{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all; 
        }
        .table_no_border{
        	border-left:none;
        	border-right:none;
        	border-top:none;
        	border-bottom:none;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        }
        
        .table_horizontal_border{
        	frame:"vsides";
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:none;
        	border-bottom:none;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        	
        }
        .table_top_border{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:'none';
        	
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        }
        
		.underline {
			border:1px solid #002299;
			position:absolute;
			left:5px;
		}


		.left_td{border-left:0px solid  black;}  
		.top_td{border-top:0px solid  black;} 
		.right_td{border-right:0px solid  black;}  
		.bottom_td{border-bottom:0px solid  black;} 
		
		td{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
         	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}
		th{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        	font-size:13px;
		}
		.tdh_no_border{
        	border-left:none;
        	border-right:none;
        	border-top:none;
        	border-bottom:none;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}

		.td_all_border{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}

		.new_page {page-break-after: always}

    </style>
    

</head>
<body>

<% cols=[
	{'width':"10%",'title':'PACK'},
	{'width':"40%",'title':' ',
		'childs':[
			{'width':"30%",'title':'DESCRIPTION'},
			{'width':"10%",'title':'UNIT PER PACK'},
		],  
	},
	{'width':"12%",'title':'TOTAL QTY'},
	{'width':"9%",'title':'N.W. (kg)'},
	{'width':"9%",'title':'G.W. (kg)'},
	{'width':"12%",'title':'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PACK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;SIZE(cm)'},
	{'width':"8%",'title':'CBM'},
]%>




%for o in objects:
	<h1 width='100%' style="text-align:center">Delivery Order/交货单 : ${o.name}</h1>
	
	<%
	sum_pack=0
	sum_qty=0
	sum_nw=0
	sum_gw=0
	sum_cbm=0
	%>
	
	<table border="1"   width="100%"  >
		<tr width="100%" >
			<th width="50%" class=tdh_no_border >
				<table   class=table_no_border  style='text-align:left;text-valign:top'>
					<tr><th class=tdh_no_border>Shipping address：</th></tr>
					<tr><th class=tdh_no_border>${ o.partner_id and o.partner_id.id and o.partner_id.title.name or ''}</th></tr>
					<tr><th class=tdh_no_border>${ o.partner_id and o.partner_id.id and o.partner_id.name }</th></tr>
					<tr><th class=tdh_no_border>${ o.partner_id and display_address(o.partner_id) }</th></tr>
					<tr><th class=tdh_no_border>${ o.partner_id.phone or o.partner_id.email or ''}</th></tr>
				</table>
			
			</th>
			<th width="50%" >
				<table   class=table_no_border  style='text-align:left'>
					<tr><th class=table_no_border>Invoicing address：</th></tr>
					<tr><th class=table_no_border>${ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.street or ''}</th></tr>
					<tr><th class=table_no_border>${ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.street2 or ''}</th></tr>
					<tr><th class=table_no_border>${ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.zip or ''}</th></tr>
					<tr><th class=table_no_border>${ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.city or ''}</th></tr>
					<tr><th class=table_no_border>${ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.state_id and  o.sale_id.partner_invoice_id.state_id.name or '' }</th></tr>
					<tr><th class=table_no_border>${ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.country_id and  o.sale_id.partner_invoice_id.country_id.name or ''}</th></tr>
				</table>
			</th>
		</tr>

	</table>
	
	</p>
	
	<table border="1"  width="100%" >
		<tr>
			%for i in cols :
				<th width=${i['width']} height=50 class=font-size8 >
					${i['title']}
					
					%if i.get('childs'):
						<table border=0 class=table_no_border >
							<tr>
								%for child in i['childs']:
									<th width=${child['width']}  class=tdh_no_border>${child['title']}</th>
								%endfor
							</tr>
						</table>
					
					%endif
				
				</th>
			%endfor
		</tr>
	</table>
	
	
	
	
	<table  border="1"   width="100%" class=table_horizontal_border  >
		<% data=get_tracking(o.id) %>
	
		%for k in data :

			<% 
			have_tacking=k and True or Flase
			tracking=data[k]['tracking']
			%>
			%if tracking:
				<% sum_pack+=1 %>
			%endif
		
			<tr>
																		
				<td width="10%" class=td_all_border vAlign="top">${tracking and tracking.name or 'No tracking'}</td>
				
				
				
				<td width="40%">
					<table width="100%" border="1" class=table_no_border >
						<tr height="20" class=tdh_noborder>
								<td width="30%" class=table_no_border align="left"></td>
								<td width="10%" class=table_no_border align="left"></td>
						</tr>
						
						%for move  in data[k]['moves']:
							<tr>
								<td width="30%"  class=table_no_border align="left">${get_product_description(move.product_id.id)}</td>
								<td width="10%"  class=table_no_border  valign="top" align="center">${move.product_qty}</td>
								<%sum_qty+=move.product_qty%>
							</tr>
						%endfor
						
					</table>
				</td>
				
				<td width="12%"  class=td_all_border valign="top" align="center">${ sum([move.product_qty for move in  data[k]['moves'] ])  } </td>
				
				<td width="9%" class=td_all_border valign="top" align="center">${tracking and tracking.net_weight or 0}</td>
				%if tracking:
					<% sum_nw+=tracking.net_weight%>
				%endif
				<td width="9%" class=td_all_border valign="top" align="center">${tracking and tracking.gross_weight or 0}</td>
				%if tracking:
					<% sum_gw+=tracking.gross_weight%>
				%endif
				<td width="12%"class=td_all_border  valign="top" align="center">${tracking and get_measurement( tracking.id ) or ''}</td> 
				<td width="8%" class=td_all_border valign="top" align="center" style="mso-number-format:'0\.00';">${tracking and tracking.pack_cbm or 0 } </td>  
				%if tracking:
					<% sum_cbm+=tracking.pack_cbm%>
				%endif
				
			</tr>
		%endfor
	</table>
	
	<p class=title>TOTAL:</p>
	
	<table border="1"  style="word-break:break-all;" width="100%" >
		<tr>
			<th width=${cols[0]['width']}  >${sum_pack}</th>
			<th width=${cols[1]['width']}  ></th>
			<th width=${cols[2]['width']}  >${sum_qty}</th>
			<th width=${cols[3]['width']}  >${sum_nw}</th>
			<th width=${cols[4]['width']}  >${sum_gw}</th>
			<th width=${cols[5]['width']}  ></th>
			<th width=${cols[6]['width']}  >${sum_cbm}</th>
			
		
		</tr>
	</table>
	


	
	
%endfor






</body>
</html>

<%doc>



Shipping address:

Supplier Address : [[ (shipping.type == 'in' or removeParentNode('para')) and '' ]]
Customer Address : [[ (shipping.type == 'out' or removeParentNode('para')) and '' ]]
Warehouse Address : [[ (shipping.type == 'internal' or removeParentNode('para')) and '' ]] ]]
[[ (shipping.partner_id and shipping.partner_id.id and shipping.partner_id.title.name) or '' ]] [[ shipping.partner_id and shipping.partner_id.id and shipping.partner_id.name ]]
[[ shipping.partner_id and display_address(shipping.partner_id) ]]
[[ shipping.partner_id.phone or shipping.partner_id.email or removeParentNode('para')]]


Invoicing address/发票地址：

[[ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.street or '']]
[[ (o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.street2) or removeParentNode('para')]]
[[ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.zip or '']] [[ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.city or '' ]]
[[ (o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.state_id and  o.sale_id.partner_invoice_id.state_id.name) or removeParentNode('para') ]] - [[ o.sale_id and o.sale_id.partner_invoice_id and o.sale_id.partner_invoice_id.country_id and  o.sale_id.partner_invoice_id.country_id.name or '']]








	<h1>${picking.name}</h1>

	<% trackings = get_tracking(picking.id)%>
	
	%for tracking in trackings:
	
		<p>${tracking}</p>
	
	%endfor
</%doc>









