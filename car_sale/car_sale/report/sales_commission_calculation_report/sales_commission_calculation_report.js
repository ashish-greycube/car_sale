// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Commission Calculation Report"] = {
	"filters": [
		{
			"label":"From Date",
			"fieldname":"from_date",
			"fieldtype":"Date",
		},
		{
			"label":"To Date",
			"fieldname":"to_date",
			"fieldtype":"Date",
			"default": frappe.datetime.get_today()
		},

	]
};
