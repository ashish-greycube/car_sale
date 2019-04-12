frappe.listview_settings['Expense Entry'] = {
	add_fields: ["docstatus"],
	get_indicator: function(doc) {
		if(doc.status == "Paid") {
			return [__("Paid"), "green", "status,=,'Paid'"];
		}else if(doc.status == "Draft") {
			return [__("Draft"), "red"];
        } 
	}
};