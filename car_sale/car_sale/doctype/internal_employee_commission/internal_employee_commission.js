// Copyright (c) 2023, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Internal Employee Commission', {
	setup: function(frm) {
		frm.set_query("calculate_for", function() {
			return{
				"filters": {
					"name": ["in", ["Sales Person", "Sales Partner"]],
				}
			}
		});
	},


	onload: function(frm){

		let fields_to_show_in_listview = ["sales_amount","cogs","other_cost","profit"];
		fields_to_show_in_listview.forEach(function(field) {

        	frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).in_list_view = 0;	
		})
	},


	fetch: function(frm){

		// let fields_to_toggle = ["sales_amount","cogs","other_cost","profit"];

		// if (frm.doc.calculate_for == "Sales Person"){

		// 	fields_to_toggle.forEach(function(field) {
		// 		frm.fields_dict['commission_details'].grid.toggle_display(field,false);
		// 	})			
		// } 
		// else {
		// 	fields_to_toggle.forEach(function(field) {
		// 		frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).in_list_view = 1;
		// 		frm.fields_dict['commission_details'].grid.toggle_display(field,true);

		// 	})	
		// }


		var fields_to_toggle = ["sales_amount", "cogs", "other_cost", "profit"];
        var show_fields = (frm.doc.calculate_for !== "Sales Person");

        fields_to_toggle.forEach(function(field) {
            frm.fields_dict.commission_details.grid.toggle_display(field, show_fields);
            frappe.meta.get_docfield("Internal Employee Commission Detail", field).in_list_view = show_fields;
        });


		



		let fields_read_only = ["sales_invoice", "item_name","serial_no","customer_name","sales_amount","cogs","other_cost","profit","profit_for_party"];
                fields_read_only.forEach(function(field) {
                        frappe.meta.get_docfield("Internal Employee Commission Detail", field, frm.doc.name).read_only = 1;
                });
		frm.call({
			doc: frm.doc,
			method: "get_commission_details",	
		})
	} 

});
