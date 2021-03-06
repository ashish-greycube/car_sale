{% include "car_sale/public/js/car_search.js" %}
frappe.ui.form.on("Purchase Order", {
	refresh: function(frm) {
        if(frm.doc.docstatus == 1) {
            if(frm.doc.status != "Closed") {
                if (frm.doc.status != "On Hold") {
                        frm.add_custom_button(__('Car Stock Entry'), make_car_stock_entry
                        , __('Create'));
            }
        }
    }         
    },
})
function make_car_stock_entry() {
    frappe.model.open_mapped_doc({
        method: "car_sale.api.make_car_stock_entry",
        frm: cur_frm
    })
} 