// Copyright (c) 2020, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Custom Card Entry', {
    refresh:function(frm){
        me.frm.add_custom_button(__('Fetch from Purchase Receipt'), function() {
            erpnext.utils.map_current_doc({
                method: "car_sale.api.make_custom_card_from_purchase_receipt",
                source_doctype: "Purchase Receipt",
                target: me.frm,
                date_field: "posting_date",
                setters: {
                    supplier: me.frm.doc.supplier || undefined,
                },
                get_query_filters: {
                    docstatus: 1,
                    status: ["not in", ["Closed", "Completed"]],
                    company: frappe.sys_defaults.company,
                    is_return: 0
                }
            })
        },);

    }
});

//car search code
frappe.ui.form.on(cur_frm.doctype, {
    search_group: function (frm) {
        if (cur_frm.doc.search_group) {
            frappe.call({
                method: "car_sale.api.get_template_name",
                args: {
                    search_group: cur_frm.doc.search_group
                },
                callback: function (r) {
                    if (r.message) {
                        cur_frm.fields_dict.search_template.df.options = r.message;
                        cur_frm.set_value('search_template', null);
                        cur_frm.refresh_field("search_template");


                    } else {
                        cur_frm.fields_dict.search_template.df.options = '';
                        cur_frm.set_value('search_template', null);
                        cur_frm.refresh_field("search_template");

                    }

                    cur_frm.fields_dict.search_category.df.options = ''
                    cur_frm.set_value('search_category', null);
                    cur_frm.refresh_field("search_category");

                    cur_frm.fields_dict.search_model.df.options = ''
                    cur_frm.set_value('search_model', null);
                    cur_frm.refresh_field("search_model");

                    cur_frm.fields_dict.search_color.df.options = ''
                    cur_frm.set_value('search_color', null);
                    cur_frm.refresh_field("search_color");

                }
            })

        } else {
            cur_frm.fields_dict.search_template.df.options = '';
            cur_frm.set_value('search_template', null);
            cur_frm.refresh_field("search_template");

        }
    },
    search_template: function (frm) {
        frappe.call({
            method: "car_sale.api.get_category_name",
            args: {
                search_template: cur_frm.doc.search_template
            },
            callback: function (r) {
                if (r.message) {
                    cur_frm.fields_dict.search_category.df.options = r.message;
                    cur_frm.set_value('search_category', null);
                    cur_frm.refresh_field("search_category");

                    cur_frm.fields_dict.search_model.df.options = ''
                    cur_frm.set_value('search_model', null);
                    cur_frm.refresh_field("search_model");

                    cur_frm.fields_dict.search_color.df.options = ''
                    cur_frm.set_value('search_color', null);
                    cur_frm.refresh_field("search_color");

                }

            }
        })
    },
    search_category: function (frm) {
        frappe.call({
            method: "car_sale.api.get_model_name",
            args: {
                search_template: cur_frm.doc.search_template,
                search_category: cur_frm.doc.search_category
            },
            callback: function (r) {
                if (r.message) {
                    cur_frm.fields_dict.search_model.df.options = r.message;
                    cur_frm.set_value('search_model', null);
                    cur_frm.refresh_field("search_model");
                }

            }
        })
    },
    search_model: function (frm) {
        frappe.call({
            method: "car_sale.api.get_color_name",
            args: {
                search_template: cur_frm.doc.search_template,
                search_category: cur_frm.doc.search_category,
                search_model: cur_frm.doc.search_model
            },
            callback: function (r) {
                if (r.message) {
                    cur_frm.fields_dict.search_color.df.options = r.message;
                    cur_frm.refresh_field("search_color");
                }

            }
        })
    },
    add: function (frm) {
        if (cur_frm.doc.search_group == undefined || cur_frm.doc.search_group == '') {
            frappe.msgprint(__("Field Group cannot be empty"));
            return;
        } else if (cur_frm.doc.search_template == undefined || cur_frm.doc.search_template == '') {
            frappe.msgprint(__("Field Brand cannot be empty"));
            return;
        } else if (cur_frm.doc.search_category == undefined || cur_frm.doc.search_category == '') {
            frappe.msgprint(__("Field Category cannot be empty"));
            return;
        } else if (cur_frm.doc.search_model == undefined || cur_frm.doc.search_model == '') {
            frappe.msgprint(__("Field Model cannot be empty"));
            return;
        } else if (cur_frm.doc.search_color == undefined || cur_frm.doc.search_color == '') {
            frappe.msgprint(__("Field Color cannot be empty"));
            return;
        }

        frappe.call({
            method: "car_sale.api.get_search_item_name",
            args: {
                search_template: cur_frm.doc.search_template,
                search_category: cur_frm.doc.search_category,
                search_model: cur_frm.doc.search_model,
                search_color: cur_frm.doc.search_color,
            },
            callback: function (r) {
                if (r.message) {
                    if (r.message[0]) {

                        if (cur_frm.doc.custom_card_item[0]) {
                            if (cur_frm.doc.custom_card_item[0].item_code == undefined) {
                                cur_frm.doc.custom_card_item.splice(cur_frm.doc.custom_card_item[0], 1)
                            }
                        }

                        var child = cur_frm.add_child("custom_card_item");
                        frappe.model.set_value(child.doctype, child.name, "item_code", r.message[0])
                        cur_frm.refresh_field("custom_card_item")

                        cur_frm.set_value('search_group', null);

                        cur_frm.fields_dict.search_template.df.options = ''
                        cur_frm.set_value('search_template', null);
                        cur_frm.refresh_field("search_template");

                        cur_frm.fields_dict.search_category.df.options = ''
                        cur_frm.set_value('search_category', null);
                        cur_frm.refresh_field("search_category");

                        cur_frm.fields_dict.search_model.df.options = ''
                        cur_frm.set_value('search_model', null);
                        cur_frm.refresh_field("search_model");

                        cur_frm.fields_dict.search_color.df.options = ''
                        cur_frm.set_value('search_color', null);
                        cur_frm.refresh_field("search_color")
                    }
                }
            }
        })
    },
    add_serial_no_item: function (cur_frm) {
        if (cur_frm.doc.search_serial_no && (cur_frm.doc.serial_no_item != undefined || cur_frm.doc.serial_no_item != '')) {
            if ((cur_frm.doc.custom_card_item[0]) && (cur_frm.doc.custom_card_item[0].item_code == undefined || cur_frm.doc.custom_card_item[0].item_code == '' || cur_frm.doc.custom_card_item[0].item_code == null)) {
                cur_frm.doc.custom_card_item.splice(cur_frm.doc.custom_card_item[0], 1)
            }

            // for serial_no with similar item code and warehouse, increase qty and append serail_no
            var caught = false;
            var no_of_items = cur_frm.doc.custom_card_item.length;
    
            if (no_of_items != 0) {
                for (var i = 0; i < cur_frm.doc["custom_card_item"].length; i++) {
                    let d=cur_frm.doc["custom_card_item"][i]
                    if (d.item_code == cur_frm.doc.serial_no_item && (d.warehouse== undefined || d.warehouse== ''|| d.serial_no==undefined || d.serial_no=='')) {
                        caught = false;
                        cur_frm.get_field("custom_card_item").grid.grid_rows[i].remove();
                        cur_frm.refresh_field("custom_card_item")
                    }               
                    else if (d.item_code == cur_frm.doc.serial_no_item && d.warehouse== cur_frm.doc.serial_no_warehouse) {
                        caught = true;
                        var qty=d.qty+1;
                        frappe.model.set_value(d.doctype, d.name, "qty",qty)
                        d.serial_no  += `\n` +  cur_frm.doc.search_serial_no
                    }
                }
            }
    
            // if item not found then add new item
            if (!caught){
                var child = cur_frm.add_child("custom_card_item");
                frappe.model.set_value(child.doctype, child.name, "item_code", cur_frm.doc.serial_no_item)
                frappe.model.set_value(child.doctype, child.name, "serial_no", cur_frm.doc.search_serial_no)
                $.extend(child, {
                    "warehouse": cur_frm.doc.serial_no_warehouse
                });   
            }
            cur_frm.refresh_field("custom_card_item")

            cur_frm.set_value('search_serial_no', undefined);
            cur_frm.set_value('serial_no_item', undefined);
            cur_frm.set_value('serial_no_warehouse', undefined);
            cur_frm.refresh_field("search_serial_no")
            cur_frm.refresh_field("serial_no_item")
            cur_frm.refresh_field("serial_no_warehouse")
        } else {
            frappe.msgprint(__("Select appropriate serial no."));
            return;
        }

    }
});
//car search code