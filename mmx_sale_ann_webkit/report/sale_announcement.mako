<html>
<head>
</head>
<body>

<% cols=[
	{'width':"20%",'title':'Sequence',},
	{'width':"20%",'title':'State'},
	{'width':"20%",'title':'Create Date'},
	{'width':"20%",'title':'Public Date'},
	{'width':"20%",'title':'Responsible'},
]%>
%for o in objects:
	<h1 width='100%' style="text-align:center">Announcement: ${o.name}</h1>
	
	<table width='100%'>
		<tr width=100%>
            <th>Pubblication date</th>
            <th>Our contact</th>
		</tr>
		<tr width=100%>
			<th width=20%  height=50 class=title>  ${o.public_date}  </th>
			<th width=20%  height=50 class=title>  ${o.responsible_uid.name}  </th>
		</tr>
	</table>
	<p></p>
	<table width=100%>
			<tr width=100%>
				<th width=40% align="center">Product Image</th>
				<th width=60% align="center">Information</th>
			</tr>
		%for product in o.product_ids:
			<tr width=100%>
				<td align="center">  <img width=170 high=170 src='http://images.sparkmodel.dev/${product.default_code}.jpg'/></td>
				<td align='bottom'>
					<div>Name: ${product.name}</div>
					<div>${product.default_code and 'Code: '+product.default_code or ''}</div>
					<div>${ product.brand_id and 'Brand: '+product.brand_id.name or ''}</div>
					<div>Price: ${product.list_price}   ${product.list_price_label}</div>
					
					%if product.availability_date!='False':
						<div>Avaliab Date: ${product.availability_date[:7]}</div>
					%endif
					
				</td>
			</tr>
		%endfor
	</table>
%endfor
</body>
</html>