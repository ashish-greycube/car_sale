// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Car Available Stock Inquiry"] = {
	"filters": [
		{
            "fieldname": "item_group",
            "label": __("Group"),
            "fieldtype": "Select",
			on_change: () => {
				var item_group = frappe.query_report.get_filter_value('item_group');
				if (item_group!='اختر المجموعة') {
                    frappe.call({
                        method: "car_sale.api.get_template_name",
                        args: {
                            search_group: item_group
                        },
                        async:false,
                        callback: function (r) {
                            if (r.message) {
								let attribute_name = 'brand'
                                let default_value='اختر النوع'
                                data=r.message
                                var attribute = frappe.query_report.get_filter(attribute_name);
                                data.unshift(default_value)
                                attribute.df.options = data;
                                attribute.df.default = data[0];
                                attribute.refresh();
                                attribute.set_input(attribute.df.default);
                               
                                //reset fields
                                all_dropdown_fields=[['Category','اختر الفئة'],['Color','اختر اللون'],['model','اختر الموديل']]
                                all_dropdown_fields.forEach(field => {
                                    let attribute_name = field[0]
                                    let default_value=field[1]
                                    var attribute = frappe.query_report.get_filter(attribute_name);
                                    attribute.df.options = default_value;
                                    attribute.df.default =default_value;
                                    attribute.refresh();
                                    attribute.set_input(attribute.df.default);
                              
                                });
                                      frappe.query_report.refresh();
                            }
                            else{
                                //reset fields
                                all_dropdown_fields=[['brand','اختر النوع'],['Category','اختر الفئة'],['Color','اختر اللون'],['model','اختر الموديل']]
                                all_dropdown_fields.forEach(field => {
                                    let attribute_name = field[0]
                                    let default_value=field[1]
                                    var attribute = frappe.query_report.get_filter(attribute_name);
                                    attribute.df.options = default_value;
                                    attribute.df.default =default_value;
                                    attribute.refresh();
                                    attribute.set_input(attribute.df.default);

                                });
                                frappe.query_report.refresh();
                            }
                        }
				
				}); 
        }else{
            frappe.query_report.refresh();
        }
    }
        },
        {
            "fieldname": "brand",
            "label": __("Brand"),
            "fieldtype": "Select",
			on_change: () => {
				var brand = frappe.query_report.get_filter_value('brand');
				if (brand!='اختر النوع') {
                    frappe.call({
                        method: "car_sale.api.get_category_name",
                        args: {
                            search_template: brand
                        },
                        async:false,
                        callback: function (r) {
                            console.log('brand')
                            console.log(r)
                            if (r.message) {
								let attribute_name = 'Category'
                                let default_value='اختر الفئة'
                                data=r.message
                                var attribute = frappe.query_report.get_filter(attribute_name);
                                data.unshift(default_value)
                                attribute.df.options = data;
                                attribute.df.default = data[0];
                                attribute.refresh();
                                attribute.set_input(attribute.df.default);
                                //reset fields
                                all_dropdown_fields=[['Color','اختر اللون'],['model','اختر الموديل']]
                                all_dropdown_fields.forEach(field => {
                                    let attribute_name = field[0]
                                    let default_value=field[1]
                                    var attribute = frappe.query_report.get_filter(attribute_name);
                                    attribute.df.options = default_value;
                                    attribute.df.default =default_value;
                                    attribute.refresh();
                                    attribute.set_input(attribute.df.default);
                                });
                                frappe.query_report.refresh();
                            }else{
                                //reset fields
                                all_dropdown_fields=[['Category','اختر الفئة'],['Color','اختر اللون'],['model','اختر الموديل']]
                                all_dropdown_fields.forEach(field => {
                                    let attribute_name = field[0]
                                    let default_value=field[1]
                                    var attribute = frappe.query_report.get_filter(attribute_name);
                                    attribute.df.options = default_value;
                                    attribute.df.default =default_value;
                                    attribute.refresh();
                                    attribute.set_input(attribute.df.default);
                                });  
                                frappe.query_report.refresh();                              
                            }
                        }
				
				}); 
        }else{
            frappe.query_report.refresh();
        }}
        },
        {
            "fieldname": "Category",
            "label": __("Category"),
            "fieldtype": "Select",
			on_change: () => {
                var Category = frappe.query_report.get_filter_value('Category');
                var brand = frappe.query_report.get_filter_value('brand');
				if (Category!='اختر الفئة' && brand!='اختر النوع') {
                    frappe.call({
                        method: "car_sale.api.get_model_name",
                        args: {
                            search_template: brand,
                            search_category: Category
                        },
                        async:false,
                        callback: function (r) {
                            if (r.message) {
								let attribute_name = 'model'
                                let default_value='اختر الموديل'
                                data=r.message
                                var attribute = frappe.query_report.get_filter(attribute_name);
                                data.unshift(default_value)
                                attribute.df.options = data;
                                attribute.df.default = data[0];
                                attribute.refresh();
                                attribute.set_input(attribute.df.default);
                                   //reset fields
                                   all_dropdown_fields=[['Color','اختر اللون']]
                                   all_dropdown_fields.forEach(field => {
                                       let attribute_name = field[0]
                                       let default_value=field[1]
                                       var attribute = frappe.query_report.get_filter(attribute_name);
                                       attribute.df.options = default_value;
                                       attribute.df.default =default_value;
                                       attribute.refresh();
                                       attribute.set_input(attribute.df.default);
                                   }); 
                                   frappe.query_report.refresh();
                            }else{
                                   //reset fields
                                   all_dropdown_fields=[['Color','اختر اللون'],['model','اختر الموديل']]
                                   all_dropdown_fields.forEach(field => {
                                       let attribute_name = field[0]
                                       let default_value=field[1]
                                       var attribute = frappe.query_report.get_filter(attribute_name);
                                       attribute.df.options = default_value;
                                       attribute.df.default =default_value;
                                       attribute.refresh();
                                       attribute.set_input(attribute.df.default);
                                   }); 
                                   frappe.query_report.refresh();                             
                            }
                        }
				
				}); 
        }else{
            frappe.query_report.refresh();
        }}
		},
        {
            "fieldname": "model",
            "label": __("Model"),
            "fieldtype": "Select",            
			on_change: () => {
                var model = frappe.query_report.get_filter_value('model');
                var Category = frappe.query_report.get_filter_value('Category');
                var brand = frappe.query_report.get_filter_value('brand');
				if (model!='اختر الموديل' && Category!='اختر الفئة' && brand!='اختر النوع') {
                    frappe.call({
                        method: "car_sale.api.get_color_name",
                        args: {
                            search_template: brand,
                            search_category: Category,
                            search_model: model
                        },
                        async:false,
                        callback: function (r) {
                            if (r.message) {
								let attribute_name = 'Color'
                                let default_value='اختر اللون'
                                data=r.message
                                var attribute = frappe.query_report.get_filter(attribute_name);
                                data.unshift(default_value)
                                attribute.df.options = data;
                                attribute.df.default = data[0];
                                attribute.refresh();
                                attribute.set_input(attribute.df.default);
                                frappe.query_report.refresh();
                            }else{
                                   //reset fields
                                   all_dropdown_fields=[['Color','اختر اللون'],['model','اختر الموديل']]
                                   all_dropdown_fields.forEach(field => {
                                       let attribute_name = field[0]
                                       let default_value=field[1]
                                       var attribute = frappe.query_report.get_filter(attribute_name);
                                       attribute.df.options = default_value;
                                       attribute.df.default =default_value;
                                       attribute.refresh();
                                       attribute.set_input(attribute.df.default);
                                   });     
                                   frappe.query_report.refresh();                         
                            }
                        }
				
				}); 
        }else{
            frappe.query_report.refresh();
        }}
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
            // let default_value='Select '+ attribute_name.charAt(0).toUpperCase() + attribute_name.slice(1)+'..'
            only_attribute_value.unshift(__(default_value))
			attribute.df.options = only_attribute_value;
            attribute.df.default = only_attribute_value[0];
            attribute.refresh();
            attribute.set_input(attribute.df.default);
        }
        function set_value_in_brand(attribute_name,data,default_value) {
            var attribute = frappe.query_report.get_filter(attribute_name);
            data.unshift(default_value)
            attribute.df.options = data;
            attribute.df.default = data[0];
            attribute.refresh();
            attribute.set_input(attribute.df.default);
        }
        report.page.add_inner_button(__("Clear Filters"), function() {
            frappe.query_report.set_filter_value('item_group','اختر المجموعة')
            all_dropdown_fields=[['brand','اختر النوع'],['Category','اختر الفئة'],['Color','اختر اللون'],['model','اختر الموديل']]
            all_dropdown_fields.forEach(field => {
                let attribute_name = field[0]
                let default_value=field[1]
                var attribute = frappe.query_report.get_filter(attribute_name);
                attribute.df.options = default_value;
                attribute.df.default =default_value;
                attribute.refresh();
                attribute.set_input(attribute.df.default);
            });           
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
                        async:true,
                        callback: function (r) {
                            if (r.message) {
                                let data = [];
                                data = r.message;
								let attribute_name = 'brand'
								let default_value='اختر النوع'
								set_value_in_brand(attribute_name, data,default_value)
								return frappe.call({
									method: "car_sale.api.get_item_group",
									args: {
										
									},
									async:true,
									callback: function (r) {
										if (r.message) {
											let data = [];
											data = r.message;
											let attribute_name = 'item_group'
											let default_value='اختر المجموعة'
											set_value_in_brand(attribute_name, data,default_value)
										}
									}
								});								

                            }
                        }
                    });
                }
            }
        });
    }
}
