// Copyright (c) 2020, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Showroom Car', {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Make Purchase Receipt'), function () {
				let serial_no_list = get_tree_options(frm.doc.showroom_car_item)
				if (serial_no_list.length == 0) {
					frappe.throw(__('There is no serial no in items table.'))
				}
				var d = new frappe.ui.Dialog({
					title: __('Make Purchase Receipt'),
					fields: [{
						label: "Select Serial No",
						fieldname: "serial_no",
						fieldtype: "Select",
						reqd: 1,
						options: serial_no_list
					}],

				});
				d.set_primary_action(__('Create'), function () {
					d.hide();
					var serial_no = d.get_value('serial_no');
					frappe.call({
						args: {
							"source_name": cur_frm.doc.name,
							"serial_no": serial_no
						},
						method: "car_sale.api.make_purchase_receipt_from_showroom_car",
						callback: function (r) {
							if (r.message) {
								var doc = frappe.model.sync(r.message)[0];
								frappe.set_route("Form", doc.doctype, doc.name);
							}
						}
					});
				});
				d.show();
			})
		}
	},
});
var get_tree_options = function (showroom_car_item) {
	let options = [];
	for (let index = 0; index < showroom_car_item.length; index++) {
		let row = showroom_car_item[index];
		let sn = row.serial_no.split('\n')
		if (sn.length) {
			$.each(sn, function (i, serial_no) {
				options.push(serial_no)
			})
		}
	}
	return options
}