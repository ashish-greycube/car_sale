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
		self.purchase_invoice=pi
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
		pi.taxes_and_charges=default_purchase_taxes_and_charges_template or ''

		pi.append("items", {
			"item_code": self.warranty_card_item,
			"qty": 1,
			"description":self.serial_no,
			"rate": self.rate,
			"conversion_factor": 1.0,
		})
		for tax in taxes:
			pi.append("taxes", tax)
			
		pi.run_method("set_missing_values")
		pi.run_method("calculate_taxes_and_totals")
		pi.save(ignore_permissions=True)
		pi.submit()
		return pi.name		
