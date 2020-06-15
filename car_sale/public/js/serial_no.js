frappe.ui.form.on('Serial No', {
    custom_card_exist_cf: function (frm) {
        if (['Delivered to Employee', 'Delivered to Customer','Delivered to Supplier'].includes(frm.doc.custom_card_exist_cf)) {    
            if (frm.doc.custom_card_exist_cf=='Delivered to Employee') {
                frm.set_value('doctype_cf', 'Employee')
            }else if(frm.doc.custom_card_exist_cf=='Delivered to Customer') {
                frm.set_value('doctype_cf', 'Customer')                
            }else if(frm.doc.custom_card_exist_cf=='Delivered to Supplier') {
                frm.set_value('doctype_cf', 'Supplier')                
            }
            frm.refresh_field('doctype_cf');
            frm.set_df_property('custom_card_given_to_cf', 'reqd', 1)
        }else{
            frm.set_value('doctype_cf', '');
            frm.set_value('custom_card_given_to_cf', '');
            frm.set_df_property('custom_card_given_to_cf', 'reqd', 0)
        }
    },
    refresh: function (frm) {

        function transfer_car() {
            var doc = cur_frm.doc;
            var args = {
                "item_code": doc.item_code,
                "qty": 1,
                "from_warehouse": doc.warehouse,
                "serial_no": doc.name,
                "basic_rate": doc.purchase_rate,
                "purpose": "Material Transfer",
                "do_not_save": 0
            }
            frappe.call({
                method: "erpnext.stock.doctype.stock_entry.stock_entry_utils.make_stock_entry",
                args: args,
                callback: function (r) {
                    if (r.message) {
                        var doclist = frappe.model.sync(r.message);
                        var stock_entry = doclist[0]
                        frappe.set_route("Form", stock_entry.doctype, stock_entry.name);
                        frappe.model.set_value(stock_entry.doctype, stock_entry.name, "with_transfer_cost", 1)
                        var item = stock_entry.items[0]
                        frappe.call({
                            doc: stock_entry,
                            method: "get_item_details",
                            args: item,
                            callback: function (r) {
                                if (r.message) {
                                    var d = item;
                                    var items_to_fill = ["uom", "stock_uom", "transfer_qty"]
                                    $.each(r.message, function (k, v) {
                                        if (items_to_fill.includes(k)) {
                                            d[k] = v;
                                        }
                                    });
                                }
                            }
                        });
                    }
                }
            })
        }

        var doc = cur_frm.doc;
        if (!doc.__islocal && doc.__onload && (doc.reservation_status == 'Available' || doc.reservation_status == 'Reserved')) {
            if (doc.reservation_status == 'Reserved') {
                get_logged_in_sales_person_and_set_transfer_button()
            }
            else{
                cur_frm.add_custom_button(__("Transfer"), transfer_car);
            }

            function get_logged_in_sales_person_and_set_transfer_button() {
                frappe.call({
                    method: "car_sale.api.get_sales_person_and_branch",
                    args: {
                        "user_email": frappe.session.user_email
                    },
                    callback: function (r) {
                        if (r.message) {
                            let logged_in_sales_person
                            logged_in_sales_person = r.message[0][0]
                            if (logged_in_sales_person == cur_frm.doc.sales_person) {
                                cur_frm.add_custom_button(__("Transfer"), transfer_car);
                            }
                        }
                    }
                })
            }
            
        }
    }
});