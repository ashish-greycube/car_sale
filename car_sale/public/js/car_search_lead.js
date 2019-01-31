frappe.ui.form.on(cur_frm.doctype, {
    search_group: function(frm){
        if (cur_frm.doc.search_group) {
            frappe.call({
                method: "car_sale.api.get_template_name",
                args: { search_group: cur_frm.doc.search_group },
                callback: function (r) {
                    if (r.message) {
                        cur_frm.fields_dict.search_template.df.options = r.message;
                        cur_frm.set_value('search_template', null);
                        cur_frm.refresh_field("search_template");
    
                        
                    }else{
                        cur_frm.fields_dict.search_template.df.options = '';
                        cur_frm.set_value('search_template', null);
                        cur_frm.refresh_field("search_template");
    
                    }
    
                    cur_frm.fields_dict.search_category.df.options =''
                    cur_frm.set_value('search_category', null);
                    cur_frm.refresh_field("search_category");
    
                    cur_frm.fields_dict.search_model.df.options =''
                    cur_frm.set_value('search_model', null);
                    cur_frm.refresh_field("search_model");
    
                    cur_frm.fields_dict.search_color.df.options=''
                    cur_frm.set_value('search_color', null);
                    cur_frm.refresh_field("search_color");
    
                }
            })
            
        }
        else{
            cur_frm.fields_dict.search_template.df.options = '';
            cur_frm.set_value('search_template', null);
            cur_frm.refresh_field("search_template");

        }
    },
	search_template: function(frm){
        frappe.call({
            method: "car_sale.api.get_category_name",
            args: { search_template: cur_frm.doc.search_template },
            callback: function (r) {
                if (r.message) {
                    cur_frm.fields_dict.search_category.df.options = r.message;
                    cur_frm.set_value('search_category', null);
                    cur_frm.refresh_field("search_category");

                    cur_frm.fields_dict.search_model.df.options =''
                    cur_frm.set_value('search_model', null);
                    cur_frm.refresh_field("search_model");

                    cur_frm.fields_dict.search_color.df.options=''
                    cur_frm.set_value('search_color', null);
                    cur_frm.refresh_field("search_color");
                    
                }

            }
        })
    },
    search_category: function(frm){
        frappe.call({
            method: "car_sale.api.get_model_name",
            args: { search_template: cur_frm.doc.search_template,
                search_category:cur_frm.doc.search_category
             },
            callback: function (r) {
                if (r.message){
                    cur_frm.fields_dict.search_model.df.options = r.message;
                    cur_frm.set_value('search_model', null);
                    cur_frm.refresh_field("search_model");
                }

            }
        })
    },
    search_model: function(frm){
        frappe.call({
            method: "car_sale.api.get_color_name",
            args: { search_template: cur_frm.doc.search_template,
                search_category:cur_frm.doc.search_category,
                search_model:cur_frm.doc.search_model
             },
            callback: function (r) {
                if (r.message) {
                    cur_frm.fields_dict.search_color.df.options = r.message;
                    cur_frm.refresh_field("search_color");                  
                }

            }
        })
    },
    add: function(frm){
        if (cur_frm.doc.search_group == undefined || cur_frm.doc.search_group == '') 
        {
            frappe.msgprint(__("Field Group cannot be empty"));
            return;
        }
        else if (cur_frm.doc.search_template == undefined || cur_frm.doc.search_template == '') 
        {
            frappe.msgprint(__("Field Brand cannot be empty"));
            return;
        }else if (cur_frm.doc.search_category == undefined || cur_frm.doc.search_category == '') 
        {
            frappe.msgprint(__("Field Category cannot be empty"));
            return;
        }
        else if(cur_frm.doc.search_model == undefined || cur_frm.doc.search_model == '')
        {
            frappe.msgprint(__("Field Model cannot be empty"));
            return;
        } 
        else if(cur_frm.doc.search_color == undefined || cur_frm.doc.search_color == '')
        {
            frappe.msgprint(__("Field Color cannot be empty"));
            return;
        } 

        frappe.call({
            method: "car_sale.api.get_search_item_name",
            args: { 
                search_template: cur_frm.doc.search_template,
                search_category:cur_frm.doc.search_category,
                search_model:cur_frm.doc.search_model,
                search_color:cur_frm.doc.search_color,
             },
            callback: function (r) {
                if (r.message) {
                    if (r.message[0]) {

                        // if (cur_frm.doc.inquiry_item[0]) {
                        //     if (cur_frm.doc.inquiry_item[0].item_code==undefined) {
                        //         cur_frm.doc.inquiry_item.splice(cur_frm.doc.inquiry_item[0], 1)
                        //     }
                        // }

                        var child = cur_frm.add_child("inquiry_item");
                        frappe.model.set_value(child.doctype, child.name, "item_code", r.message[0])
                        cur_frm.refresh_field("inquiry_item")

                        cur_frm.set_value('search_group', null);

                        cur_frm.fields_dict.search_template.df.options = ''
                        cur_frm.set_value('search_template', null);
                        cur_frm.refresh_field("search_template");

                        cur_frm.fields_dict.search_category.df.options = ''
                        cur_frm.set_value('search_category', null);
                        cur_frm.refresh_field("search_category");

                        cur_frm.fields_dict.search_model.df.options =''
                        cur_frm.set_value('search_model', null);
                        cur_frm.refresh_field("search_model");

                        cur_frm.fields_dict.search_color.df.options=''
                        cur_frm.set_value('search_color', null);
                        cur_frm.refresh_field("search_color")
                    }
                }
            }
        })
    },
});