// Copyright (c) 2019, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warranty Card Issued', {
	refresh: function(frm) {

	},
	onload: function(frm) {
			//get only customer of bank type
			frm.set_query('warranty_card_item', function() {
				return {
					filters: {
						item_group: 'Warranty Card Group'
					}
				}
			})
	},
	validate: function(frm) {
		if (frm.doc.sales_invoice==undefined) {
			frappe.throw(__("Sales Invoice not found  for serial no: {0}",[frm.doc.serial_no]));
			return false;
			
		}

	}
});
