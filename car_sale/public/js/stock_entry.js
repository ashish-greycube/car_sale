frappe.ui.form.on('Stock Entry', {
    before_save: function (frm) {
        if (frm.doc.purpose=='Material Receipt') {
             return make_color_model_mandatory_for_serialized_items(frm)
        }
    },    
    refresh: function (frm) {
        if (frm.doc.with_transfer_cost == 1) {
            frm.set_df_property("transferred_by_supplier", "reqd", 1);
            if (frm.doc.transfer_cost == 0.00) {
                frm.doc.transfer_cost = ''
            }
            frm.set_df_property("transfer_cost", "reqd", 1);
        } else {
            frm.set_df_property("transferred_by_supplier", "reqd", 0);
            frm.set_df_property("transfer_cost", "reqd", 0);
        }
    },
    with_transfer_cost: function (frm) {
        if (frm.doc.with_transfer_cost == 1) {
            frm.set_df_property("transferred_by_supplier", "reqd", 1);
            if (frm.doc.transfer_cost == 0.00) {
                frm.doc.transfer_cost = ''
            }
            frm.set_df_property("transfer_cost", "reqd", 1);
        } else {
            frm.set_df_property("transferred_by_supplier", "reqd", 0);
            frm.set_df_property("transfer_cost", "reqd", 0);
        }
    },
    add_serial_no_item: function (frm) {
        if (cur_frm.doc.search_serial_no && (cur_frm.doc.serial_no_item != undefined || cur_frm.doc.serial_no_item != '')) {
            if ((cur_frm.doc.items[0]) && (cur_frm.doc.items[0].item_code == undefined || cur_frm.doc.items[0].item_code == '' || cur_frm.doc.items[0].item_code == null)) {
                cur_frm.doc.items.splice(cur_frm.doc.items[0], 1)
            }
            var child = cur_frm.add_child("items");
            $.extend(child, {
                "item_code": cur_frm.doc.serial_no_item
            });
            $.extend(child, {
                "serial_no": cur_frm.doc.search_serial_no
            });
            $.extend(child, {
                "s_warehouse": cur_frm.doc.serial_no_warehouse
            });
            $.extend(child, {
                "t_warehouse": cstr(cur_frm.doc.t_warehouse)
            });
            var args = {
                'item_code': cur_frm.doc.serial_no_item,
                'warehouse': cstr(cur_frm.doc.serial_no_warehouse),
                'transfer_qty': 1,
                'serial_no': cur_frm.doc.search_serial_no,
                'bom_no': undefined,
                'expense_account': undefined,
                'cost_center': undefined,
                'company': cur_frm.doc.company,
                'qty': 1,
                'voucher_type': cur_frm.doc.doctype,
                'voucher_no': child.name,
                'allow_zero_valuation': 1,
            };
            return frappe.call({
                doc: frm.doc,
                method: "get_item_details",
                args: args,
                callback: function (r) {
                    if (r.message) {
                        var d = child;
                        $.each(r.message, function (k, v) {
                            d[k] = v;
                        });
                        $.extend(child, {
                            "serial_no": cur_frm.doc.search_serial_no
                        });
                        refresh_field("items");
                        cur_frm.set_value('search_serial_no', undefined);
                        cur_frm.set_value('serial_no_item', undefined);
                        cur_frm.set_value('serial_no_warehouse', undefined);
                        cur_frm.refresh_field("search_serial_no")
                        cur_frm.refresh_field("serial_no_item")
                        cur_frm.refresh_field("serial_no_warehouse")
                    }
                }
            });
        } else {
            frappe.msgprint(__("Select appropriate serial no."));
            return;
        }
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