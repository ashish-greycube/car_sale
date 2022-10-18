// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Car Sales Analysis Report"] = {
  filters: [
    {
      label: "Item Code",
      fieldname: "item_code",
      fieldtype: "Link",
      options: "Item",
    },
    {
      label: "Customer",
      fieldname: "customer",
      fieldtype: "Link",
      options: "Customer",
    },
    {
      fieldname: "Color",
      label: __("Color"),
      fieldtype: "Select",
    },
    {
      fieldname: "model",
      label: __("Model"),
      fieldtype: "Select",
    },
  ],
};
