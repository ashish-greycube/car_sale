// Copyright (c) 2021, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Car Stock Entry', {
    setup:function(frm) {
        frm.set_query('item_code', 'items', () => {
            return {
                filters: {
                    has_serial_no: 1
                }
            }
        })   
    }, 
	refresh: function(frm) {
        if(frm.doc.docstatus == 1) {
            if(frm.doc.entry_type == "Receipt") {
                        frm.add_custom_button(__('Return Car Stock Entry'), make_return_car_stock_entry
                        , __('Create'));
        }
    }         
    }	
});
function make_return_car_stock_entry() {
    frappe.model.open_mapped_doc({
        method: "car_sale.api.make_return_car_stock_entry",
        frm: cur_frm
    })
} 