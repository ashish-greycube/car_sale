// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Individual Car Stock Entry', {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1 && frm.doc.status == "Car Sold Out") {
			if (frm.doc.payment_status == 'Paid') {

				frappe.db.get_list('Journal Entry', {
					fields: ['name'],
					filters: {
						individual_car_entry_reference: frm.doc.name,
						individual_car_entry_type: 'Payment'
					}
				}).then(records => {
					if (records.length == 0) {
						frm.add_custom_button(__('Payment Journal Entry'), function () {
							frappe.call({
								method: "create_payment_journal_entry",
								doc: frm.doc,
								callback: function (r) {
									if (!r.exc) {
										frm.refresh();
									}
								}
							});
						}, __('Create'));
					}
				})
			}

			if (frm.doc.payment_status == 'Paid') {

				frappe.db.get_list('Journal Entry', {
					fields: ['name'],
					filters: {
						individual_car_entry_reference: frm.doc.name,
						individual_car_entry_type: 'Other'
					}
				}).then(records => {
					if (records.length == 0) {
						frm.add_custom_button(__('Other Journal Entry'), function () {
							frappe.call({
								method: "create_other_journal_entry",
								doc: frm.doc,
								callback: function (r) {
									if (!r.exc) {
										frm.refresh();
									}
								}
							});
						}, __('Create'));
					}
				})

			}

			frappe.db.get_list('Sales Invoice', {
				fields: ['name'],
				filters: {
					individual_car_entry_reference: frm.doc.name
				}
			}).then(records => {
				if (records.length == 0) {
					frm.add_custom_button(__('Sales Invoice'), function () {
						frappe.call({
							method: "create_sales_invoice",
							doc: frm.doc,
							callback: function (r) {
								if (!r.exc) {
									frm.refresh();
								}
							}
						});
					}, __('Create'));
				}
			})

		}
	},
	payment_status: function (frm) {
		frm.trigger("toggle_reqd_fields")
	},
	status: function (frm) {
		frm.trigger("toggle_reqd_fields")
	},
	reservation_status: function (frm) {
		frm.trigger("toggle_reqd_fields")
	},
	toggle_reqd_fields: function (frm) {
		frm.toggle_reqd(["mode_of_payment"], frm.doc.payment_status == 'Paid' ? 1 : 0);
		frm.toggle_reqd(["sale_rate"], frm.doc.status == "Car Sold Out" ? 1 : 0);
		if (frm.doc.status == "Car Received") {
			frm.set_df_property('selling_or_return_date', 'reqd', 0)
			frm.set_df_property('customer_buyer', 'reqd', 0)
		} else if (frm.doc.status == "Car Returned") {
			frm.set_df_property('selling_or_return_date', 'reqd', 1)
			frm.set_df_property('customer_buyer', 'reqd', 0)
		} else if (frm.doc.status == "Car Sold Out") {
			frm.set_df_property('selling_or_return_date', 'reqd', 1)
			frm.set_df_property('customer_buyer', 'reqd', 1)
		}
	}
});