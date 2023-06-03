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
	fetch: function(frm){
		// frappe.msgprint("clicked me")
		frm.call({
			
			doc: frm.doc,
			method: "get_commission_details",
			
		})
	}
});
