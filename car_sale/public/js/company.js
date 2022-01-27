
frappe.provide("erpnext.company");

frappe.ui.form.on("Company", {
	setup: function(frm) {
		erpnext.company.setup_queries(frm);
		frm.set_query("default_car_individual_receivable_account", function(){
			return {
				filters: {"account_type": "Receivable"}
			}
		});
	}
})