{% include "car_sale/public/js/car_search.js" %}

frappe.ui.form.on('Sales Order', {
	items_on_form_rendered: function() {
			erpnext.setup_serial_no();
	},
	onload: function (cur_frm) {
		//get sales partenr
		if (cur_frm.doc.sales_person==undefined || cur_frm.doc.sales_person=='' ) {
			return frappe.call({
				method: "car_sale.api.get_sales_person_and_branch_and_costcenter",
				args: {"user_email":frappe.session.user_email},
				callback: function(r) {
					if(r.message) {
						let sales_person=r.message[0][0]
						let branch=r.message[0][1]
						let cost_center=r.message[0][3]
						cur_frm.set_value('sales_person',sales_person);
						cur_frm.set_value('sales_person_branch',branch);
						cur_frm.set_value('branch_cost_center',cost_center);
						cur_frm.refresh_field('sales_person_branch')
						cur_frm.refresh_field('sales_person')
						cur_frm.refresh_field('branch_cost_center')
					}
				}
			})				
		}
},
sales_person: function (frm) {
	if (cur_frm.doc.sales_person!='' ) {
		return frappe.call({
			method: "car_sale.api.get_branch_and_costcenter",
			args: {"name":cur_frm.doc.sales_person},
			callback: function(r) {
				if(r.message) {
					let branch=r.message[0][0]
					let cost_center=r.message[0][2]
					cur_frm.set_value('sales_person_branch',branch);
					cur_frm.set_value('branch_cost_center',cost_center);
					cur_frm.refresh_field('sales_person_branch')
					cur_frm.refresh_field('branch_cost_center')
				}
			}
		})				
	}
}
	
});