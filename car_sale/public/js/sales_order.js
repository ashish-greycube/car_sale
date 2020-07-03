
{% include "car_sale/public/js/car_search.js" %}
{% include 'erpnext/selling/sales_common.js' %}

frappe.ui.form.on('Sales Order', {
	customer:function(frm) {
		frappe.db.get_value('Customer', frm.doc.customer, 'bank_customer')
		.then(r => {
			let is_bank=r.message.bank_customer
			if (is_bank==1) {
				frm.set_df_property('sub_customer', 'read_only', 0);
				frm.set_query('sub_customer', () => {
					return {
						filters: {
							bank_customer: 0
						}
					}
				})
			}else{
				frm.doc.sub_customer=''
				frm.set_df_property('sub_customer', 'read_only', 1);
				frm.doc.sub_customer_name_cf=''
			}
		})		
	},
	refresh: function(frm) {
		if (cur_frm.doc.docstatus==1 && cur_frm.doc.status !== 'Closed' && cur_frm.doc.status !== 'On Hold') {
								// sales invoice
								if(flt(cur_frm.doc.per_billed, 6) < 100) {
									if (cur_frm.doc.so_payment_type_cf=='Cash' && cur_frm.doc.advance_paid < cur_frm.doc.grand_total) {
										setTimeout(() => cur_frm.remove_custom_button('Invoice','Make'), 1000);
									}					
								}
		}
	},
	validate: function(frm) {

		// check entered price is not less than sales price
		if (frappe.user.has_role("Sales Agent")) {
			for (let index = 0; index < frm.doc.items.length; index++) {
				let row = frm.doc.items[index];
				if(row.price_list_rate && row.rate < row.price_list_rate) {
					frappe.throw(__('Rate entered by you is <b> {0} </b>. It cannot be less than sales rate {1}',[row.rate, row.price_list_rate]))				
				}			
	
			}			
		}


		frappe.db.get_value('Customer', frm.doc.customer, 'bank_customer')
		.then(r => {
			let is_bank=r.message.bank_customer
			if (is_bank==1) {
				frm.set_df_property('po_no', 'reqd', 1);
			}else{
				frm.set_df_property('po_no', 'reqd', 0);
			}
		})




		
	},
	onload_post_render: function(doc, dt, dn) {
		if(cur_frm.doc.docstatus==1) {
			if(doc.status != 'Closed') {
			// delivery note
			if(cur_frm.custom_buttons.Delivery != undefined ){
				if(cur_frm.custom_buttons.Delivery.length==1){
					cur_frm.add_custom_button(__('Car Delivery'), () => {
						cur_frm.events.car_make_delivery_note_based_on_delivery_date();
					});
				}
			}
			if(cur_frm.custom_buttons.تسليم != undefined ){
				if(cur_frm.custom_buttons.تسليم.length==1){
					cur_frm.add_custom_button(__('تسليم السيارة'), () => {
						cur_frm.events.car_make_delivery_note_based_on_delivery_date();
					});
				}
			}

			} 
		}
	},
	car_make_delivery_note_based_on_delivery_date: function() {
		var me = this;
	
		var delivery_dates = [];
		$.each(cur_frm.doc.items || [], function(i, d) {
			if(!delivery_dates.includes(d.delivery_date)) {
				delivery_dates.push(d.delivery_date);
			}
		});
	
		var item_grid = cur_frm.fields_dict["items"].grid;
		if(!item_grid.get_selected().length && delivery_dates.length > 1) {
			var dialog = new frappe.ui.Dialog({
				title: __("Select Items based on Delivery Date"),
				fields: [{fieldtype: "HTML", fieldname: "dates_html"}]
			});
	
			var html = $(`
				<div style="border: 1px solid #d1d8dd">
					<div class="list-item list-item--head">
						<div class="list-item__content list-item__content--flex-2">
							${__('Delivery Date')}
						</div>
					</div>
					${delivery_dates.map(date => `
						<div class="list-item">
							<div class="list-item__content list-item__content--flex-2">
								<label>
								<input type="checkbox" data-date="${date}" checked="checked"/>
								${frappe.datetime.str_to_user(date)}
								</label>
							</div>
						</div>
					`).join("")}
				</div>
			`);
	
			var wrapper = dialog.fields_dict.dates_html.$wrapper;
			wrapper.html(html);
	
			dialog.set_primary_action(__("Select"), function() {
				var dates = wrapper.find('input[type=checkbox]:checked')
					.map((i, el) => $(el).attr('data-date')).toArray();
	
				if(!dates) return;
	
				$.each(dates, function(i, d) {
					$.each(item_grid.grid_rows || [], function(j, row) {
						if(row.doc.delivery_date == d) {
							row.doc.__checked = 1;
						}
					});
				})
				me.car_make_delivery_note();
				dialog.hide();
			});
			dialog.show();
		} else {
			this.car_make_delivery_note();
		}
	},
	
	car_make_delivery_note: function() {
		frappe.model.open_mapped_doc({
			method: "car_sale.api.car_make_delivery_note",
			frm: me.frm
		})
	},

	items_on_form_rendered: function() {
			erpnext.setup_serial_no();
	},
	onload: function (cur_frm) {
		$('[data-fieldname="customer_name_in_arabic"]').hide()
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

frappe.ui.form.on('Sales Order Item', {

	rate: function (frm,cdt,cdn) {
		// check entered price is not less than sales price
		let row = locals[cdt][cdn];
		if (row.price_list_rate && row.rate < row.price_list_rate && frappe.user.has_role("Sales Agent")) {
			frappe.throw(__('Rate entered by you is <b> {0} </b>. It cannot be less than sales rate {1}',[row.rate, row.price_list_rate]))
		}
	}
})