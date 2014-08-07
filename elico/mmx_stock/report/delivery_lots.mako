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
		.barcode39 {
		    font-family: "Free 3 of 9";
		    font-size: 36pt;
		}
    </style>
    
    
</head>
<body>

<table width="99%">
%for i in range(len(objects)):
	%if (i % 3)==0:
		<tr  width="99%" ></tr>
	%endif
	<td width='33%' height='80'>${objects[i].name}
	
	
		<p class="barcode39">3i5h43iht</p>
	
	<td>
%endfor
</table>

</body>
</html>









