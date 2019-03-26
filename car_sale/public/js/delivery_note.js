{% include "car_sale/public/js/car_search.js" %}
{% include "car_sale/public/js/sales_person.js" %}

frappe.ui.form.on('Delivery Note', {
    onload: function (frm) {

        //get customer of non bank type
        cur_frm.set_query('sub_customer', function(doc) {
            return {
                query: "car_sale.api.get_non_bank_customer"
            }
        });

        $.each(cur_frm.doc.items || [], function (i, v) {
            if (v.against_sales_order && !v.branch_cost_center)
                frappe.model.set_value(v.doctype, v.name, "cost_center", locals["Sales Order"][v.against_sales_order].branch_cost_center)
        })
        cur_frm.refresh_field('items');
    },
    customer: function (frm){
        console.log(frm.doc.customer)
        if (frm.doc.customer) {
            return frappe.call({
                method: "car_sale.api.is_customer_a_bank",
                args: {"customer":frm.doc.customer},
                callback: function(r) {
                    console.log(r)
                        let is_bank_customer=r.message
                        if (is_bank_customer=='1') {
                            frm.set_df_property("sub_customer", "hidden", 0);
                            cur_frm.refresh_field('sub_customer')
                        }else{
                            frm.set_df_property("sub_customer", "hidden", 1);
                            cur_frm.refresh_field('sub_customer')                          
                        }
                }
            })
            
        }
    }
});