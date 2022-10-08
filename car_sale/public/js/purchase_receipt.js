frappe.ui.form.on("Purchase Receipt", {
	refresh: function(frm) {
		if(!frm.doc.is_return && frm.doc.status!="Closed") {
			if (frm.doc.docstatus == 0) {
                frm.add_custom_button(__('Custom Card Entry'), function() {
                    erpnext.utils.map_current_doc({
                        method: "car_sale.api.make_purchase_receipt_from_custom_card_entry",
                        source_doctype: "Custom Card Entry",
                        target: frm,
                        date_field: "transaction_date",
                        setters: {
                            supplier: me.frm.doc.supplier || undefined,
                        },
                        get_query_filters: {
                            docstatus: 1,
                        }
                    })
                }, __("Get items from")); 
            }
        }
    },
    before_save: function (frm) {
        return make_color_model_mandatory_for_serialized_items(frm)
    }    
})

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