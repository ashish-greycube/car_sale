// Copyright (c) 2019, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('New Car Request', {
	refresh: function(frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Make Purchase Order'), function () {
				frappe.call({
					args: {
						"source_name": cur_frm.doc.name,
					},
					method: "car_sale.api.make_purchase_order_from_new_car_request",
					callback: function (r) {
						if (r.message) {
							var doc = frappe.model.sync(r.message)[0];
							frappe.set_route("Form", doc.doctype, doc.name);
						}
					}
				});
			})
		}
	}
});
