frappe.ui.form.on('Sales Order', {
    sales_partner: function(frm) {
		frappe.call({
			method: "car_sale.api.get_branch_of_sales_partner",
			args: {
				'sales_partner': cur_frm.doc.sales_partner
			},
			callback: function(r) {
				if(r.message) {
					cur_frm.set_value('sales_partner_branch',r.message);
					cur_frm.refresh_fields('sales_partner_branch');
				}
			}
		})
    },
});