// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

// Item Name		Supplier		Customer			Color		Model
// Reservation Status		Warehouse
frappe.query_reports["Car Serial No Report"] = {
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
    {
      fieldname: "reservation_status",
      label: __("Reservation Status"),
      fieldtype: "Select",
      options: ["","Reserved","Available","Available Individual","Sold Out","Sold Individual","Showroom Car","Returned","Returned Individual","Available-Qty","Available-Card"]     
    },
    {
      fieldname: "warehouse",
      label: __("Warehouse"),
      fieldtype: "Link",
      options: "Warehouse",
    },
  ],
};
