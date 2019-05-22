// Copyright (c) 2019, GreyCube Technologies and contributors
// For license information, please see license.txt
frappe.ui.form.on('Expense Entry', {
	setup: function (frm) {
		const default_company = frappe.defaults.get_default('company');
		frm.set_value("company", default_company);

		frm.set_query("expense_account", "expenses_entry_detail", function () {
			return {
				filters: {
					'account_type': ["in", ['Expense Account', 'Cost of Goods Sold', 'Expenses Included in Valuation', 'Tax']],
					'company': frm.doc.company,
					'is_group': 0
				}
			};
		});	

		frm.set_query("paid_from_account", function () {
			return {
				"filters": {
					"account_type": ["in", ['Bank,Cash']],
					'company': frm.doc.company,
					"is_group": 0
				}
			};
		});
		if (frm.doc.expense_type == 'Cash'){
			frm.set_df_property("party", "reqd", 0);
			frm.set_df_property("mode_of_payment", "reqd", 1);
			frm.set_df_property("paid_from_account", "reqd", 1);
		}
	},
	onload_post_render:async function (frm) {

		if (frm.doc.expense_type == 'Credit') {
			
			frm.set_df_property("party", "reqd", 1);
			frm.set_df_property("mode_of_payment", "reqd", 0);
			frm.set_df_property("paid_from_account", "reqd", 0);

			frm.set_value('party_type', 'Supplier');
			let default_payable_account = (await frappe.db.get_value("Company", frm.doc.company, "default_payable_account")).message.default_payable_account;
			frm.set_value('payable_account', default_payable_account)

		}
		else if (frm.doc.expense_type == 'Cash'){
			frm.set_df_property("party", "reqd", 0);
			frm.set_df_property("mode_of_payment", "reqd", 1);
			frm.set_df_property("paid_from_account", "reqd", 1);
		}		

	},
	expense_type: async function (frm) {
		if (frm.doc.expense_type == 'Credit') {
			
			frm.set_df_property("party", "reqd", 1);
			frm.set_df_property("mode_of_payment", "reqd", 0);
			frm.set_df_property("paid_from_account", "reqd", 0);

			frm.set_value('party_type', 'Supplier');
			let default_payable_account = (await frappe.db.get_value("Company", frm.doc.company, "default_payable_account")).message.default_payable_account;
			frm.set_value('payable_account', default_payable_account)

		}
		else if (frm.doc.expense_type == 'Cash'){
			frm.set_df_property("party", "reqd", 0);
			frm.set_df_property("mode_of_payment", "reqd", 1);
			frm.set_df_property("paid_from_account", "reqd", 1);
		}
	},
	refresh: function (frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('View Accounting Ledger'), function () {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			});
		}
	},
	company: function (frm) {
		if (frm.doc.company) {
			frappe.call({
				method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_company_defaults",
				args: {
					company: frm.doc.company
				},
				callback: function (r, rt) {
					if (r.message) {
						console.log(r.message)
						let default_cost_center = r.message["cost_center"]
						frm.set_value("cost_center", default_cost_center || '');


					}
				}
			});
		}
	},
	mode_of_payment: function (frm) {
		if (frm.doc.mode_of_payment && frm.doc.company) {
			frappe.call({
				method: "erpnext.accounts.doctype.sales_invoice.sales_invoice.get_bank_cash_account",
				args: {
					"mode_of_payment": frm.doc.mode_of_payment,
					"company": frm.doc.company
				},
				callback: function (r, rt) {
					if (r.message) {
						frm.set_value("paid_from_account", r.message.account);
					} else {
						frm.set_value("mode_of_payment", undefined);
					}
				}
			});

		}
	},
});
frappe.ui.form.on('Expenses Entry Detail', {
	expenses_entry_detail_add: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.model.set_value(row.doctype, row.name, 'cost_center', frm.doc.cost_center);
	}
});
// cur_frm.set_query("cost_center", "expenses_entry_detail", function(doc, cdt, cdn) {
// 	var row = locals[cdt][cdn];
// 	frappe.model.set_value(row.doctype, row.name, 'cost_center', doc.cost_center);
// });