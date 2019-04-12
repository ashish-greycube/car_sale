// Copyright (c) 2019, GreyCube Technologies and contributors
// For license information, please see license.txt
frappe.ui.form.on('Expense Entry', {
	setup: function (frm) {
		const default_company = frappe.defaults.get_default('company');
		frm.set_value("company", default_company);

		frm.set_query("expense_account", "expenses_entry_detail", function () {
			return {
				filters: {
					'account_type': 'Expense Account',
					'company': frm.doc.company,
					'is_group': 0
				}
			};
		});

		frm.set_query("paid_from_account", function () {
			return {
				"filters": {
					"account_type": ["in",['Bank,Cash']],
					'company': frm.doc.company,
					"is_group": 0
				}
			};
		});
	},
	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
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
						}else{
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