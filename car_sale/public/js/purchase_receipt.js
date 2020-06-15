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
    }


})
