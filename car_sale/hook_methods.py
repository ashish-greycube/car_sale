# -*- coding: utf-8 -*-
# Copyright (c) 2021, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import make_records


def after_migrate():
    custom_fields =[
 {
  "doctype": "Custom Field",
  "dt": "Journal Entry",
  "fieldname": "individual_car_entry_reference",
  "fieldtype": "Link",
  "insert_after": "user_remark",
  "label": "Individual Car Entry Reference",
  "name": "Journal Entry-individual_car_entry_reference",
  "options": "Individual Car Stock Entry",
 },
 {
  "doctype": "Custom Field",
  "dt": "Journal Entry",
  "fieldname": "individual_car_entry_type",
  "fieldtype": "Data",
  "hidden": 1,
  "insert_after": "individual_car_entry_reference",
  "label": "individual_car_entry_type",
  "name": "Journal Entry-individual_car_entry_type",
 },
 {
  "doctype": "Custom Field",
  "dt": "Company",
  "fieldname": "default_sales_invoice_naming_series",
  "fieldtype": "Data",
  "insert_after": "sales_monthly_history",
  "label": "Default Sales Invoice Naming Series",
  "name": "Company-default_sales_invoice_naming_series",
 },
 {
  "doctype": "Custom Field",
  "dt": "Company",
  "fieldname": "default_commission_item",
  "fieldtype": "Link",
  "insert_after": "default_sales_invoice_naming_series",
  "label": "Default Commission Item",
  "name": "Company-default_commission_item",
  "options": "Item",
 },
 {
  "doctype": "Custom Field",
  "dt": "Company",
  "fieldname": "default_car_individual_receivable_account",
  "fieldtype": "Link",
  "insert_after": "unrealized_exchange_gain_loss_account",
  "label": "Default Car Individual Receivable Account",
  "name": "Company-default_car_individual_receivable_account",
  "options": "Account",
 },
 {
  "doctype": "Custom Field",
  "dt": "Company",
  "fieldname": "default_creditors_account",
  "fieldtype": "Link",
  "insert_after": "default_car_individual_receivable_account",
  "label": "Default Creditors Account",
  "name": "Company-default_creditors_account",
  "options": "Account",
 },
 {
  "doctype": "Custom Field",
  "dt": "Serial No",
  "fieldname": "individual_car_detail_sb_cf",
  "fieldtype": "Section Break",
  "insert_after": "status",
  "label": "Individual Car Detail",
  "name": "Serial No-individual_car_detail_sb_cf",
 },
 {
  "doctype": "Custom Field",
  "dt": "Serial No",
  "fieldname": "individual_car_entry_date",
  "fieldtype": "Date",
  "insert_after": "individual_car_detail_sb_cf",
  "label": "Individual Car Entry Date",
  "name": "Serial No-individual_car_entry_date",
 },
 {
  "doctype": "Custom Field",
  "dt": "Serial No",
  "fieldname": "individual_car_entry_reference",
  "fieldtype": "Link",
  "insert_after": "individual_car_entry_date",
  "label": "Individual Car Entry Reference",
  "name": "Serial No-individual_car_entry_reference",
  "options": "Individual Car Stock Entry",
 },
 {
  "doctype": "Custom Field",
  "dt": "Serial No",
  "fieldname": "customer_seller",
  "fieldtype": "Link",
  "insert_after": "individual_car_entry_reference",
  "label": "Customer Seller",
  "name": "Serial No-customer_seller",
  "options": "Customer",
 },
 {
  "doctype": "Custom Field",
  "dt": "Serial No",
  "fieldname": "customer_buyer",
  "fieldtype": "Link",
  "insert_after": "customer_seller",
  "label": "Customer Buyer",
  "name": "Serial No-customer_buyer",
  "options": "Customer",
 },
 {
  "doctype": "Custom Field",
  "dt": "Serial No",
  "fieldname": "individual_car_return_date",
  "fieldtype": "Date",
  "insert_after": "customer_buyer",
  "label": "Individual Car Return/Selling Date",
  "name": "Serial No-individual_car_return_date",
 },
 {
  "doctype": "Custom Field",
  "dt": "Sales Invoice",
  "fieldname": "individual_car_entry_reference",
  "fieldtype": "Link",
  "insert_after": "is_discounted",
  "label": "Individual Car Entry Reference",
  "name": "Sales Invoice-individual_car_entry_reference",
  "options": "Individual Car Stock Entry",
 }
]
	
    for d in custom_fields:
        if not frappe.get_meta(d["dt"]).has_field(d["fieldname"]):
            frappe.get_doc(d).insert()