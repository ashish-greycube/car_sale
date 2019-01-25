frappe.ui.form.on('Quotation', {
    on_submit:function(frm) {
        if (cur_frm.doc.reserve_above_items==0) {
            cur_frm.set_df_property("reserve_above_items", "read_only", 1);
        }
    },
    sales_partner: function(frm) {
		frappe.call({
			method: "car_sale.api.get_branch_of_sales_partner",
			args: {
				'sales_partner': cur_frm.doc.sales_partner
			},
			callback: function(r) {

				if(r.message) {
					console.log(r.message)
					cur_frm.set_value('sales_partner_branch',r.message[0]);
					cur_frm.refresh_field('sales_partner_branch');
				}
			}
		})
    },
});