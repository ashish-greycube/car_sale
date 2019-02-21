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