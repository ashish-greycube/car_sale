import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_field = {
		"Purchase Invoice": [
			{
				"fieldname": "car_serial_no_to_book_expense_cf",
				"label": "Car Serial No",
				"fieldtype": "Link",
				"insert_after": "warranty_card_issued",
				"description":"Used to book expense, it should be present in PI item",
				"options":"Serial No",
				"is_custom_field":1,
				"is_system_generated":0,
				"allow_on_submit":1,
				"translatable":0,
				"no_copy":1
			},			
		]
	}
		   
	print('creating fields create_car_serial_no_to_book_expense_cf_in_purchase_invoice..')
	create_custom_fields(custom_field, update=True)