// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Total Car Report"] = {
	"filters": [
		{
			label: "Item Code",
			fieldname: "item_code",
			fieldtype: "Link",
			options: "Item",
		  },
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		  },		
		{
			fieldname: "Color",
			fieldtype: "Link",
			label: __("Color"),
			options: "Car Color"
		  },
		  {
			fieldname: "model",
			fieldtype: "Link",
			label: __("Model"),
			options: "Car Model"
		  },
	]
};
