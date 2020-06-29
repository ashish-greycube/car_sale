{% include "car_sale/public/js/car_search.js" %}
{% include "car_sale/public/js/sales_person.js" %}
frappe.ui.form.on('Quotation', {
	party_name:function(frm) {
		if ( frm.doc.quotation_to=='Customer') {
			frappe.db.get_value('Customer', frm.doc.party_name, 'bank_customer')
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
		}else{
			//for lead?
		}
	},	
	on_submit: function (frm) {
			if (cur_frm.doc.reserve_above_items == 0) {
				cur_frm.set_df_property("reserve_above_items", "read_only", 1);
			}
	},
	items_on_form_rendered: function () {
		erpnext.setup_serial_no();
	},
	setup: function (frm) {

	},
	refresh: function (frm) {
		if (cur_frm.doc.docstatus == 1 && cur_frm.doc.status !== 'Lost') {
			if (!cur_frm.doc.valid_till || frappe.datetime.get_diff(cur_frm.doc.valid_till, frappe.datetime.get_today()) > 0) {
				cur_frm.add_custom_button(__('Car Sales Order'),
					cur_frm.cscript['Make Sales Order From Quotation'], __("Make"));
			}
		}
	},

	validate: function (frm) {
		// check entered price is not less than sales price
		for (let index = 0; index < frm.doc.items.length; index++) {
			let row = frm.doc.items[index];
			if (row.price_list_rate && row.rate < row.price_list_rate) {
				frappe.throw(__('Rate entered by you is <b> {0} </b>. It cannot be less than sales rate {1}', [row.rate, row.price_list_rate]))
			}
		}
	}
});

frappe.ui.form.on('Quotation Item', {
	rate: function (frm,cdt,cdn) {
		// check entered price is not less than sales price
		let row = locals[cdt][cdn];
		if (row.price_list_rate && row.rate < row.price_list_rate) {
			frappe.throw(__('Rate entered by you is <b> {0} </b>. It cannot be less than sales rate {1}',[row.rate, row.price_list_rate]))
		}
	}
})

cur_frm.cscript['Make Sales Order From Quotation'] = function() {
	frappe.model.open_mapped_doc({
		method: "car_sale.api.make_sales_order_from_quotation",
		frm: cur_frm
	})
}
