frappe.ui.form.on(cur_frm.doctype, {
    onload: function (cur_frm) {
			//get sales partenr
			if (cur_frm.doc.sales_person==undefined || cur_frm.doc.sales_person=='' ) {
				return frappe.call({
					method: "car_sale.api.get_sales_person_and_branch",
					args: {"user_email":frappe.session.user_email},
					callback: function(r) {
						if(r.message) {
							let sales_person=r.message[0][0]
							let branch=r.message[0][1]
							if (cur_frm.doctype=='Lead') {
								let source=r.message[0][3] 
								let customer_group=r.message[0][4]
								cur_frm.set_value('source',source);
								cur_frm.set_value('customer_group',customer_group);
								cur_frm.refresh_field('source')
								cur_frm.refresh_field('customer_group')

							}
							cur_frm.set_value('sales_person',sales_person);
							cur_frm.set_value('sales_person_branch',branch);
							cur_frm.refresh_field('sales_person_branch')
							cur_frm.refresh_field('sales_person')

						}
					}
				})				
			}
    }
});