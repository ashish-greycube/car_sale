{% include "car_sale/public/js/car_search.js" %}
{% include "car_sale/public/js/sales_person.js" %}
frappe.ui.form.on('Quotation', {
    on_submit:function(frm) {
        if (cur_frm.doc.reserve_above_items==0) {
            cur_frm.set_df_property("reserve_above_items", "read_only", 1);
        }
	},
	items_on_form_rendered: function() {
		erpnext.setup_serial_no();
	},
	setup:function(frm){

	}
});