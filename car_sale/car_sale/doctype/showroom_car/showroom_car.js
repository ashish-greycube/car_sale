// Copyright (c) 2020, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Showroom Car', {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Make Purchase Receipt'), function () {
				let serial_no_list = get_tree_options(frm.doc.showroom_car_item)
				if (serial_no_list.length == 0) {
					frappe.throw(__('There is no serial no in showroom car item table.'))
				}
				var d = new frappe.ui.Dialog({
					title: __('Make Purchase Receipt'),
					fields: [{
						label: "Select Serial No",
						fieldname: "serial_no",
						fieldtype: "Select",
						reqd: 1,
						options: serial_no_list
					}],

				});
				d.set_primary_action(__('Create'), function () {
					d.hide();
					var serial_no = d.get_value('serial_no');
					frappe.call({
						args: {
							"source_name": cur_frm.doc.name,
							"serial_no": serial_no
						},
						method: "car_sale.api.make_purchase_receipt_from_showroom_car",
						callback: function (r) {
							if (r.message) {
								var doc = frappe.model.sync(r.message)[0];
								frappe.set_route("Form", doc.doctype, doc.name);
							}
						}
					});
				});
				d.show();
			})
		}
	},
});
var get_tree_options = function (showroom_car_item) {
	let options = [];
	for (let index = 0; index < showroom_car_item.length; index++) {
		let row = showroom_car_item[index];
		let sn = row.serial_no.split('\n')
		if (sn.length) {
			$.each(sn, function (i, serial_no) {
				options.push(serial_no)
			})
		}
	}
	return options
}

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

                        if (cur_frm.doc.showroom_car_item[0]) {
                            if (cur_frm.doc.showroom_car_item[0].item_code == undefined) {
                                cur_frm.doc.showroom_car_item.splice(cur_frm.doc.showroom_car_item[0], 1)
                            }
                        }

                        var child = cur_frm.add_child("showroom_car_item");
                        frappe.model.set_value(child.doctype, child.name, "item_code", r.message[0])
                        cur_frm.refresh_field("showroom_car_item")

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
            if ((cur_frm.doc.showroom_car_item[0]) && (cur_frm.doc.showroom_car_item[0].item_code == undefined || cur_frm.doc.showroom_car_item[0].item_code == '' || cur_frm.doc.showroom_car_item[0].item_code == null)) {
                cur_frm.doc.showroom_car_item.splice(cur_frm.doc.showroom_car_item[0], 1)
            }

            // for serial_no with similar item code and warehouse, increase qty and append serail_no
            var caught = false;
            var no_of_items = cur_frm.doc.showroom_car_item.length;
    
            if (no_of_items != 0) {
                for (var i = 0; i < cur_frm.doc["showroom_car_item"].length; i++) {
                    let d=cur_frm.doc["showroom_car_item"][i]
                    if (d.item_code == cur_frm.doc.serial_no_item && (d.warehouse== undefined || d.warehouse== ''|| d.serial_no==undefined || d.serial_no=='')) {
                        caught = false;
                        cur_frm.get_field("showroom_car_item").grid.grid_rows[i].remove();
                        cur_frm.refresh_field("showroom_car_item")
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
                var child = cur_frm.add_child("showroom_car_item");
                frappe.model.set_value(child.doctype, child.name, "item_code", cur_frm.doc.serial_no_item)
                frappe.model.set_value(child.doctype, child.name, "serial_no", cur_frm.doc.search_serial_no)
                $.extend(child, {
                    "warehouse": cur_frm.doc.serial_no_warehouse
                });   
            }
            cur_frm.refresh_field("showroom_car_item")

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