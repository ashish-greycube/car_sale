# -*- coding: utf-8 -*-
# Copyright (c) 2019, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import erpnext
from frappe.model.document import Document
from erpnext.controllers.accounts_controller import get_taxes_and_charges

class WarrantyCardIssued(Document):
	def on_submit(self):
		pi=self.make_purchase_invoice()
		print('pi'*100,pi)
		form_link = frappe.utils.get_link_to_form("Purchase Invoice", pi)
		message = _("Purchase Invoice  {0}, is created and submitted.").format(frappe.bold(form_link))
		frappe.msgprint(message)		



	def make_purchase_invoice(self):
		default_purchase_taxes_and_charges_template=frappe.db.get_list('Purchase Taxes and Charges Template', filters={
    												'is_default': ['=', '1']})
		if default_purchase_taxes_and_charges_template:
			default_purchase_taxes_and_charges_template=default_purchase_taxes_and_charges_template[0].name
			taxes = get_taxes_and_charges('Purchase Taxes and Charges Template',default_purchase_taxes_and_charges_template)

		pi = frappe.new_doc("Purchase Invoice")
		pi.posting_date = frappe.utils.today()
		pi.posting_time = frappe.utils.nowtime()
		pi.update_stock = 0
		pi.is_paid = 0


		pi.company = erpnext.get_default_company()
		pi.supplier = self.supplier
		pi.warranty_card_issued=self.name
		# pi.currency = args.currency or "INR"
		# pi.conversion_rate = args.conversion_rate or 1
		# pi.is_return = args.is_return
		# pi.return_against = args.return_against
		# pi.is_subcontracted = args.is_subcontracted or "No"
		pi.taxes_and_charges=default_purchase_taxes_and_charges_template or ''
		# pi.supplier_warehouse = args.supplier_warehouse or "_Test Warehouse 1 - _TC"

		pi.append("items", {
			"item_code": self.warranty_card_item,
			# "warehouse": args.warehouse or "_Test Warehouse - _TC",
			"qty": 1,
			"description":self.serial_no,
			# "received_qty": args.received_qty or 0,
			# "rejected_qty": args.rejected_qty or 0,
			"rate": self.rate,
			# 'expense_account': args.expense_account or '_Test Account Cost for Goods Sold - _TC',
			"conversion_factor": 1.0,
			# "serial_no":self.serial_no,
			# "stock_uom": "_Test UOM",
			# "cost_center": args.cost_center or "_Test Cost Center - _TC",
			# "project": args.project,
			# "rejected_warehouse": args.rejected_warehouse or "",
			# "rejected_serial_no": args.rejected_serial_no or "",
			# "asset_location": args.location or ""
		})
		for tax in taxes:
			pi.append("taxes", tax)
			
		pi.run_method("set_missing_values")
		pi.run_method("calculate_taxes_and_totals")
		pi.save(ignore_permissions=True)
		pi.submit()
		return pi.name		
