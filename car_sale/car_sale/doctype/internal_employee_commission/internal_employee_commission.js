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
		commission_details_UI(frm)
	},
	onload: function (frm) {
		commission_details_UI(frm)
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
				frm.refresh_field("commission_details");
				frm.refresh_field("total_commission");
				commission_details_UI(frm)
			}
		});
	}
});

function commission_details_UI(frm) {
	// hide-unhide + show in list view + set column width
	let sales_partner_fields = ["sales_amount", "cogs", "other_cost", "profit"];
	let sales_person_fields = ["item_code", "customer_name", "sales_invoice", "profit_for_party"];
	if (frm.doc.calculate_for == "Sales Partner") {
		sales_person_fields.forEach(function (field) {
			// frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).columns = 1;
			// cur_frm.set_df_property(field, 'columns', 1, frm.doc.name, 'commission_details')
		})
		sales_partner_fields.forEach(function (field) {
			frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).hidden = 0;
			cur_frm.set_df_property(field, 'hidden', 0, cur_frm.doc.name, 'commission_details')
			frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).in_list_view = 1;
			cur_frm.set_df_property(field, 'in_list_view', 1, cur_frm.doc.name, 'commission_details')
			// frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).columns = 1;
			// cur_frm.set_df_property(field, 'columns', 1, cur_frm.doc.name, 'commission_details')
		})

		cur_frm.refresh_field('commission_details')
	} else if (frm.doc.calculate_for == "Sales Person") {
		sales_partner_fields.forEach(function (field) {
			frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).hidden = 1;
			cur_frm.set_df_property(field, 'hidden', 1, frm.doc.name, 'commission_details')
			frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).in_list_view = 0;
			cur_frm.set_df_property(field, 'in_list_view', 0, frm.doc.name, 'commission_details')
			// frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).columns = 1;
			// cur_frm.set_df_property(field, 'columns', 1, frm.doc.name, 'commission_details')
			cur_frm.set_df_property('sales_amount', 'in_list_view', 1, cur_frm.doc.name, 'commission_details')
		})
		sales_person_fields.forEach(function (field) {
			// frappe.meta.get_docfield("Internal Employee Commission Detail", field, cur_frm.doc.name).columns = 2;
			// cur_frm.set_df_property(field, 'columns', 2, cur_frm.doc.name, 'commission_details')
		})
		cur_frm.refresh_field('commission_details')
	}
}