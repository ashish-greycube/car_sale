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
            "fieldname": "Status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": ['اختر الحالة','Available', 'Reserved', 'Sold Out'],
            "default":'اختر الحالة'
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
        function set_value_in_dropdown(attribute_name, data,default_value) {
            filtered_attribute = filtered(data, attribute_name)
            let only_attribute_value = []
            only_attribute_value = get_only_attribute_value(filtered_attribute, only_attribute_value)
            var attribute = frappe.query_report.get_filter(attribute_name);
            // default_value='Select '+ attribute_name+'..'
            only_attribute_value.unshift(__(default_value))
            attribute.df.options = only_attribute_value;
            attribute.df.default = only_attribute_value[0];
            attribute.refresh();
            attribute.set_input(attribute.df.default);
        }
        function set_value_in_brand(attribute_name,data,default_value) {
            var attribute = frappe.query_report.get_filter(attribute_name);
            // let default_value=__("Select Brand..")
            data.unshift(default_value)
            attribute.df.options = data;
            attribute.df.default = data[0];
            attribute.refresh();
            attribute.set_input(attribute.df.default);
        }
        function clear_filter(filtername){
            var filter = frappe.query_report.get_filter(filtername);
            frappe.query_report.set_filter_value(filtername,'')
            filter.refresh()
        }
        report.page.add_inner_button(__("Clear Filters"), function() {
            list_of_filters=['supplier','warehouse','serialno']
            list_of_filters.forEach(clear_filter)
           
            // frappe.query_report.set_filter_value('Status',__("Select Status.."))
            // frappe.query_report.set_filter_value('Category', __("Select Category.."))
            // frappe.query_report.set_filter_value('Color', __("Select Color.."))
            // frappe.query_report.set_filter_value('model',__("Select model..")) 
            frappe.query_report.set_filter_value('Status','اختر الحالة')
            frappe.query_report.set_filter_value('Brand','اختر النوع')
            frappe.query_report.set_filter_value('Category', 'اختر الفئة')
            frappe.query_report.set_filter_value('Color', 'اختر اللون')
            frappe.query_report.set_filter_value('model','اختر الموديل')

        });
        
        return frappe.call({
            method: "car_sale.api.get_distinct_attributes_values",
            args: {},
            async:true,
            callback: function (r) {
                if (r.message) {
                    let data = [];
                    data = r.message
                    attribute_name = 'Color'
                    default_value='اختر اللون'
                    set_value_in_dropdown(attribute_name, data,default_value)
                    attribute_name = 'Category'
                    default_value='اختر الفئة'
                    set_value_in_dropdown(attribute_name, data,default_value)
                    attribute_name = 'model'
                    default_value='اختر الموديل'
                    set_value_in_dropdown(attribute_name, data,default_value)
                    return frappe.call({
                        method: "car_sale.api.get_template_name",
                        args: {
                            "search_group": "All Item Groups"
                        },
                        async:false,
                        callback: function (r) {
                            if (r.message) {
                                let data = [];
                                data = r.message;
                                attribute_name = 'Brand'
                                default_value='اختر النوع'
                                set_value_in_brand(attribute_name, data,default_value)
                            }
                        }
                    });
                }
            }
        });
    }
}