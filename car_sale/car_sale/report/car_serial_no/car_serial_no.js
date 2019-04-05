frappe.query_reports["Car Serial No"] = {
    "filters": [{
            "fieldname": "supplier",
            "label": __("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier"
        },
        {
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse"
        },
        {
            "fieldname": "serialno",
            "label": __("Serial No"),
            "fieldtype": "Link",
            "options": "Serial No"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": ['Available', 'Reserved', 'Sold Out']
        },

        {
            "fieldname": "Brand",
            "label": __("Brand"),
            "fieldtype": "Select"
        },
        {
            "fieldname": "Category",
            "label": __("Category"),
            "fieldtype": "Select"
        },
        {
            "fieldname": "model",
            "label": __("Model"),
            "fieldtype": "Select"
        },
        {
            "fieldname": "Color",
            "label": __("Color"),
            "fieldtype": "Select"
        }
    ],
    "onload": function (report) {

        function filtered(data, attribute_name) {
            let filtered = [];
            filtered = data.filter(e => e.attribute.localeCompare(attribute_name) == 0);
            return filtered
        }
        function get_only_attribute_value(filtered, only_attribute_value) {
            for (var i = 0; i < filtered.length; i++) {
                only_attribute_value.push(filtered[i].attribute_value);
            }
            return only_attribute_value
        }
        function set_value_in_dropdown(attribute_name, data) {
            filtered_attribute = filtered(data, attribute_name)
            let only_attribute_value = []
            only_attribute_value = get_only_attribute_value(filtered_attribute, only_attribute_value)
            var attribute = frappe.query_report.get_filter(attribute_name);
            attribute.df.options = only_attribute_value;
            attribute.refresh();
        }
        function set_value_in_brand(attribute_name,data) {
            var attribute = frappe.query_report.get_filter(attribute_name);
            attribute.df.options = data;
            attribute.refresh();
        }
        function clear_filter(filtername){
            console.log(filtername)
            var filter = frappe.query_report.get_filter(filtername);
            frappe.query_report.set_filter_value(filtername,'')
            filter.refresh()
        }
        report.page.add_inner_button(__("Clear Filters"), function() {
            list_of_filters=['supplier','warehouse','serialno','status','Brand','Category','model','Color']
            list_of_filters.forEach(clear_filter)

		});
        return frappe.call({
            method: "car_sale.api.get_distinct_attributes_values",
            args: {},
            callback: function (r) {
                if (r.message) {
                    let data = [];
                    data = r.message
                    console.log(r.message)
                    attribute_name = 'Color'
                    set_value_in_dropdown(attribute_name, data)
                    attribute_name = 'Category'
                    set_value_in_dropdown(attribute_name, data)
                    attribute_name = 'model'
                    set_value_in_dropdown(attribute_name, data)
                    return frappe.call({
                        method: "car_sale.api.get_template_name",
                        args: {
                            "search_group": "All Item Groups"
                        },
                        callback: function (r) {
                            if (r.message) {
                                let data = [];
                                data = r.message;
                                attribute_name = 'Brand'
                                set_value_in_brand(attribute_name, data)
                            }
                        }
                    });
                }
            }
        });
    }
}