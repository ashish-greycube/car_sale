{% include "car_sale/public/js/car_search.js" %}

frappe.ui.form.on('Sales Invoice', {
    onload: function (frm) {
        $('[data-fieldname="customer_name_in_arabic"]').hide()
        //get customer of non bank type
        // cur_frm.set_query('sub_customer', function(doc) {
        //     return {
        //         query: "car_sale.api.get_all_customer"
        //     }
        // });
		cur_frm.set_query("sub_customer", function() {
			return {
				filters: [
					["bank_customer", "=", 0]
				]
			}
		});

        $.each(cur_frm.doc.items || [], function (i, v) {
            if (v.against_sales_order && !v.cost_center){
                frappe.model.set_value(v.doctype, v.name, "cost_center", locals["Sales Order"][v.against_sales_order].branch_cost_center)
            }
        })
        cur_frm.refresh_field('items');

                //get sales partenr
        if (cur_frm.doc.sales_person==undefined || cur_frm.doc.sales_person=='' ) {
            return frappe.call({
                method: "car_sale.api.get_sales_person_and_branch",
                args: {"user_email":frappe.session.user_email},
                callback: function(r) {
                    if(r.message) {
                        let sales_person=r.message[0][0]
                        let branch=r.message[0][1]
                        let commission_per_car=r.message[0][2]
                        cur_frm.set_value('sales_person',sales_person);
                        cur_frm.set_value('sales_person_branch',branch);
                        cur_frm.set_value('commission_per_car',commission_per_car);
                        cur_frm.refresh_field('sales_person')
                        cur_frm.refresh_field('commission_per_car')
                        cur_frm.refresh_field('sales_person_branch')
                    }
                }
            })				
        }
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
        })
    }
        else{
            row.registration_plate_no=undefined
            cur_frm.refresh_field('items')
        }
    }
});
