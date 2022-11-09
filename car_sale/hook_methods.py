# -*- coding: utf-8 -*-
# Copyright (c) 2021, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_migrate():
    custom_fields = [
        {
        "doctype": "Custom Field",
        "dt": "Customer",
        "fieldname": "phone_no_cf",
        "fieldtype": "Data",
        "insert_after": "image",
        "label": "Phone No",
        "name": "Customer-phone_no_cf",
        "options": "Phone",
        },     
        {
        "doctype": "Custom Field",
        "dt": "Customer",
        "fieldname": "id_no_cf",
        "fieldtype": "Data",
        "insert_after": "phone_no_cf",
        "label": "ID No",
        "name": "Customer-id_no_cf",
        },           
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
        },
    ]

    for d in custom_fields:
        if not frappe.get_meta(d["dt"]).has_field(d["fieldname"]):
            frappe.get_doc(d).insert()

    add_car_sales_report_custom_fields()


def add_car_sales_report_custom_fields():
    print("Creating custom fields for Car Sales Analysis Report")
    custom_fields = {
        "Company": [
            dict(
                fieldtype="Section Break",
                fieldname="sb_car_default_acccounts",
                label="Car Default Accounts Section",
                insert_after="parent_company",
                translatable=0,
            ),
            dict(
                fieldtype="Link",
                fieldname="car_plate_no_cost_account_cf",
                label="Car Plate No Cost Account",
                insert_after="sb_car_default_acccounts",
                options="Account",
            ),
            dict(
                fieldtype="Link",
                fieldname="car_insurance_expense_account_cf",
                label="Car Insurance Expense Account",
                insert_after="car_plate_no_cost_account_cf",
                options="Account",
            ),
            dict(
                fieldtype="Link",
                fieldname="car_transfer_cost_account_cf",
                label="Car Transfer Cost Account",
                insert_after="car_insurance_expense_account_cf",
                options="Account",
            ),
            dict(
                fieldtype="Link",
                fieldname="car_maintenance_cost_account_cf",
                label="Car Maintenance Cost Account",
                insert_after="car_transfer_cost_account_cf",
                options="Account",
            ),
            dict(
                fieldtype="Link",
                fieldname="car_other_expense_account_cf",
                label="Car Other Expense Account",
                insert_after="car_maintenance_cost_account_cf",
                options="Account",
            ),
        ],
        "Journal Entry Account": [
            dict(
                fieldtype="Link",
                fieldname="serial_no_cf",
                label="Serial No",
                options="Serial No",
                translatable=0,
            ),
        ],
    }

    create_custom_fields(custom_fields)
