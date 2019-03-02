{% include "car_sale/public/js/car_search.js" %}

frappe.ui.form.on('Sales Invoice', {
    onload: function (frm) {
        $.each(cur_frm.doc.items || [], function (i, v) {
            if (v.against_sales_order && !v.cost_center)
                frappe.model.set_value(v.doctype, v.name, "cost_center", locals["Sales Order"][v.against_sales_order].branch_cost_center)
        })
        cur_frm.refresh_field('items');
    }
});
frappe.ui.form.on('Sales Invoice Item', {
    serial_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.serial_no.length > 0){
       return frappe.call({
            method: "car_sale.api.get_registration_plate_no",
            args: {"serial_nos":row.serial_no},
            callback: function(r, rt) {
                if(r.message) {
                    let new_registration_plate_no=r.message
                    row.registration_plate_no=new_registration_plate_no
                    cur_frm.refresh_field('items')
                }
            }
        })}
        else{
            row.registration_plate_no=undefined
            cur_frm.refresh_field('items')
        }
    }
});