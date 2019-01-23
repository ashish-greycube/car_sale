//item template name
//--------------------------

frappe.call({
    method: "car_sale.api.get_template_name",
    callback: function (r) {
        cur_frm.fields_dict.search_template.df.options = r.message;
        cur_frm.refresh_field("search_template");
    }
})

frappe.ui.form.on('Sales Invoice', {
	search_template: function(frm){
        frappe.call({
            method: "car_sale.api.get_category_name",
            args: { search_template: cur_frm.doc.search_template },
            callback: function (r) {
                cur_frm.fields_dict.search_category.df.options = r.message;
                cur_frm.refresh_field("search_category");
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
                cur_frm.fields_dict.search_model.df.options = r.message;
                cur_frm.refresh_field("search_model");
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
                cur_frm.fields_dict.search_color.df.options = r.message;
                cur_frm.refresh_field("search_color");
            }
        })
    },
    add: function(frm){
        if (cur_frm.doc.search_template == undefined || cur_frm.doc.search_template == '') 
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
            args: { search_template: cur_frm.doc.search_template,
                search_category:cur_frm.doc.search_category,
                search_model:cur_frm.doc.search_model,
                search_color:cur_frm.doc.search_color,
             },
            callback: function (r) {
                console.log(r.message)
                var child = cur_frm.add_child("items");
                frappe.model.set_value(child.doctype, child.name, "item_code", r.message[0][0])
                cur_frm.refresh_field("items")
            }
        })
    },


});