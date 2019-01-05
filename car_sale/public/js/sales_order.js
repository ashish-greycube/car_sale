
{% include 'erpnext/selling/sales_common.js' %}

frappe.ui.form.on("Sales Order", {


	setup: function(frm) {

        console.log('xxx')
        console.log(frm)
        frm.set_query('search_brand', function(doc) {
            console.log('YYY')
            console.log(doc)
            
            return {
                query: "car_sale.api.get_brand_name"
            }
        });


		frm.custom_make_buttons = {
			'Delivery Note': 'Delivery',
			'Sales Invoice': 'Invoice',
			'Material Request': 'Material Request',
			'Purchase Order': 'Purchase Order',
			'Project': 'Project'
		}
        frm.add_fetch('customer', 'tax_id', 'tax_id');


		// formatter for material request item
		frm.set_indicator_formatter('item_code',
            function(doc) { return (doc.stock_qty<=doc.delivered_qty) ? "green" : "orange" })

            // cur_frm.set_query('search_category', function(doc) {
            //     return {
            //         query: "car_sale.api.get_category_name"
            //     }
            // });
            // cur_frm.set_query('search_model', function(doc) {
            //     return {
            //         query: "car_sale.api.get_model_name"
            //     }
            // });
            // cur_frm.set_query('search_color', function(doc) {
            //     return {
            //         query: "car_sale.api.get_color_name"
            //     }
            // });


    }
})