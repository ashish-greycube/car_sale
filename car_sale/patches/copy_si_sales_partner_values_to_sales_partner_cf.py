from __future__ import unicode_literals
import frappe

def execute():
	print('copying existing values of sp to new sp..')
	frappe.reload_doc('accounts', 'doctype', 'sales_invoice')

	# update all existing sp to new sp
	frappe.db.sql("update `tabSales Invoice` set car_sales_partner_cf=sales_partner,car_sales_partner_commission_rate_cf=commission_rate")
