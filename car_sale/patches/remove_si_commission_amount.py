import frappe


def execute():
    frappe.reload_doc('accounts', 'doctype', 'sales_invoice')
    if frappe.db.exists("Custom Field", "Sales Invoice-commission_amount"):
	    frappe.delete_doc("Custom Field", "Sales Invoice-commission_amount")
