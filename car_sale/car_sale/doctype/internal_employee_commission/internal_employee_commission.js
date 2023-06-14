// Copyright (c) 2023, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Internal Employee Commission', {
	setup: function (frm) {
		frm.set_query("calculate_for", function () {
			return {
				"filters": {
					"name": ["in", ["Sales Person", "Sales Partner"]],
				}
			}
		});
	},
	calculate_for: function (frm) {
		frm.trigger("toggle_commission_details_table");
	},
	toggle_commission_details_table: function(frm) {
		if (frm.doc.calculate_for == "Sales Partner") {
			frm.set_df_property('iec_sales_partner_commission_details', 'hidden', 0);
			frm.set_df_property('iec_sales_person_commission_details', 'hidden', 1);
			frm.refresh_field("iec_sales_partner_commission_details");
		} else if (frm.doc.calculate_for == "Sales Person") {
			frm.set_df_property('iec_sales_partner_commission_details', 'hidden', 1);
			frm.set_df_property('iec_sales_person_commission_details', 'hidden', 0);	
			frm.refresh_field("iec_sales_person_commission_details");	
		}else{
			frm.set_df_property('iec_sales_partner_commission_details', 'hidden', 1);
			frm.set_df_property('iec_sales_person_commission_details', 'hidden', 1);				
		}
	},	
	onload: function (frm) {
		frm.trigger("toggle_commission_details_table");
	},
	fetch: function (frm) {
		// all 4 fileds are required
		if (frm.doc.from_date == undefined || frm.doc.to_date == undefined || frm.doc.calculate_for == undefined || frm.doc.party == undefined) {
			frappe.msgprint(__("Please ensure From Date, Calculate For, To Date and Party has values."));
			return;
		}
		frm.call({
			method: "get_commission_details",
			doc: frm.doc,
			callback: function (r) {
				frm.trigger("toggle_commission_details_table");
				frm.refresh_field("total_commission");
			}
		});
	}
});

