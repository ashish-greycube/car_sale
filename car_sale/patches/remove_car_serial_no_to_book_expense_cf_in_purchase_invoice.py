import frappe


def execute():
    frappe.reload_doc('accounts', 'doctype', 'purchase_invoice')
    if frappe.db.exists("Custom Field", "Purchase Invoice-car_serial_no_to_book_expense_cf"):
	    frappe.delete_doc("Custom Field", "Purchase Invoice-car_serial_no_to_book_expense_cf")
