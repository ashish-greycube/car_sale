{% include 'erpnext/selling/sales_common.js' %}

frappe.ui.form.on("Quotation", {
        items_on_form_rendered: function() {
            console.log('items_on_form_rendered')
            erpnext.setup_serial_no();
        }
})