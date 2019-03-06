{% include "car_sale/public/js/car_search_lead.js" %}
frappe.ui.form.on('Purchase Invoice', {
    refresh: function (frm) {
        if (cur_frm.doc.docstatus === 0) {
            cur_frm.add_custom_button(__('Warranty Card'), function () {
                if (!frm.doc.supplier || !frm.doc.posting_date) {
                    frappe.msgprint(__("Please specify Supplier & Posting date to proceed"));
                } else {
                    return frappe.call({
                        method: "car_sale.api.get_waranty_card_items_for_PI",
                        args: {
                            "supplier": frm.doc.supplier,
                            "posting_date": frm.doc.posting_date
                        },
                        callback: function (r) {
                            console.log(r)
                            if (r.message) {
                                let warranty_item = r.message
                                warranty_item.forEach(fill_item_child);
                                function fill_item_child(value, index) {
                                    if ((cur_frm.doc.items[0]) && (cur_frm.doc.items[0].item_code == undefined || cur_frm.doc.items[0].item_code == '' || cur_frm.doc.items[0].item_code == null)) {
                                        cur_frm.doc.items.splice(cur_frm.doc.items[0], 1)
                                    }
                                    var child = cur_frm.add_child("items");
                                    frappe.model.set_value(child.doctype, child.name, "item_code", value.warranty_card_item)
                                    frappe.model.set_value(child.doctype, child.name, "qty", value.qty)
                                }
                                setTimeout(() => {
                                    warranty_item.forEach((value, idx) => {
                                        let child = cur_frm.doc.items[idx];
                                        frappe.model.set_value(child.doctype, child.name, "description", value.description)
                                    });
                                }, 500);
                                cur_frm.refresh_field("items")
                            }
                        }
                    })
                }

            }, __("Get items from"))

        }
    }
});