{% include "car_sale/public/js/car_search.js" %}
frappe.ui.form.on('Purchase Invoice', {
    refresh: function (frm) {
        if (cur_frm.doc.docstatus === 0) {

            // cur_frm.add_custom_button(__('Warranty Card'), function () {
            //     if (!frm.doc.supplier || !frm.doc.posting_date) {
            //         frappe.msgprint(__("Please specify Supplier & Posting date to proceed"));
            //     } else {
            //         return frappe.call({
            //             method: "car_sale.api.get_waranty_card_items_for_PI",
            //             args: {
            //                 "supplier": frm.doc.supplier,
            //                 "posting_date": frm.doc.posting_date
            //             },
            //             callback: function (r) {
            //                 console.log(r)
            //                 if (r.message) {
            //                     let warranty_item = r.message
            //                     if ((cur_frm.doc.items.length>0)) {
            //                         cur_frm.doc.items.splice(cur_frm.doc.items[0],cur_frm.doc.items.length)
            //                      }
            //                     warranty_item.forEach(fill_item_child);
            //                     function fill_item_child(value, index) {
            //                         var child = cur_frm.add_child("items");
            //                         frappe.model.set_value(child.doctype, child.name, "item_code", value.warranty_card_item)
            //                         frappe.model.set_value(child.doctype, child.name, "qty", value.qty)
            //                         // frappe.msgprint(__(" {0} - warranty cards found for '{1}'.",[value.qty,value.warranty_card_item]));

            //                     }
            //                     setTimeout(() => {
            //                         warranty_item.forEach((value, idx) => {
            //                             let child = cur_frm.doc.items[idx];
            //                             console.log(idx)
            //                             console.log(value.description)
            //                             frappe.model.set_value(child.doctype, child.name, "description", value.description)
            //                             var df = frappe.meta.get_docfield("Purchase Invoice Item","description", cur_frm.doc.name);
            //                             df.read_only = 1;
            //                             frappe.msgprint(__(" {0} - warranty cards found for '{1}'.",[value.qty,value.warranty_card_item]));
            //                         });
            //                     }, 1000);
            //                     cur_frm.refresh_field("items")
            //                 }else{
            //                     frappe.msgprint(__("No warranty card found for {0} and {1}",[cur_frm.doc.supplier,cur_frm.doc.posting_date]));
            //                 }
            //             }
            //         })
            //     }

            // }, __("Get items from"))

            cur_frm.add_custom_button(__('Car Transferred'), function () {
                if (!frm.doc.supplier || !frm.doc.posting_date) {
                    frappe.msgprint(__("Please specify Supplier & Posting date to proceed"));
                } else {
                    return frappe.call({
                        method: "car_sale.api.car_transferred_items_for_PI",
                        args: {
                            "supplier": frm.doc.supplier,
                            "posting_date": frm.doc.posting_date
                        },
                        callback: function (r) {
                            console.log(r)
                            if (r.message) {
                                let transferred_item = r.message
                                if ((cur_frm.doc.items.length>0)) {
                                    cur_frm.doc.items.splice(cur_frm.doc.items[0],cur_frm.doc.items.length)
                                 }
                                 transferred_item.forEach(fill_item_child);
                                function fill_item_child(value, index) {
                                    var child = cur_frm.add_child("items");

                                    frappe.model.set_value(child.doctype, child.name, "item_code", value.default_item_for_car_transfer)
                                    frappe.model.set_value(child.doctype, child.name, "qty", value.qty)
                                    frappe.model.set_value(child.doctype, child.name, "stock_entry_for_car_transfer", value.stock_entry)
                                    
                                    // frappe.msgprint(__(" {0} - warranty cards found for '{1}'.",[value.qty,value.warranty_card_item]));

                                }
                                setTimeout(() => {
                                    transferred_item.forEach((value, idx) => {
                                        let child = cur_frm.doc.items[idx];
                                        console.log(idx)
                                        console.log(value.description)
                                        frappe.model.set_value(child.doctype, child.name, "description", value.description)
                                        frappe.model.set_value(child.doctype, child.name, "rate", value.transfer_cost)
                                        var df = frappe.meta.get_docfield("Purchase Invoice Item","description", cur_frm.doc.name);
                                        df.read_only = 1;
                                        frappe.msgprint(__(" {0} - stock entry found for '{1}'.",[value.qty,value.item_name]));
                                    });
                                }, 1000);
                                cur_frm.refresh_field("items")
                            }else{
                                frappe.msgprint(__("No stock entry found for {0} and {1}",[cur_frm.doc.supplier,cur_frm.doc.posting_date]));
                            }
                        }
                    })
                }

            }, __("Get items from"))            

        }
    },
    before_save: function (frm) {
        return make_color_model_mandatory_for_serialized_items(frm)
    }
    
});

function make_color_model_mandatory_for_serialized_items(frm) {
    return new Promise((resolve, reject) => {
        frm.doc.items.forEach(row => {
            let grid_row = frm.get_field('items').grid.get_row(row.name)
            if (row.serial_no == undefined || row.serial_no == '') {} else {
                //  item has serial no
                if (row.car_color_cf == undefined || row.car_color_cf == '') {
                    // item has serial_no and no color
                    frappe.throw(__("Row <b>{0}</b> : is a serialized item and hence  <b>car color</b> is required.", [row.idx]));
                }
                if (row.car_model_cf == undefined || row.car_model_cf == '') {
                    // item has serial_no and no model
                    frappe.throw(__("Row <b>{0}</b> : is a serialized item and hence  <b>car model</b> is required.", [row.idx]));
                }
            }
        });
        resolve()
    })
}