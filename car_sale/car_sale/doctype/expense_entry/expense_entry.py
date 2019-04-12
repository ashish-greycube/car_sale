# -*- coding: utf-8 -*-
# Copyright (c) 2019, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cstr
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController

class ExpenseEntry(AccountsController):
	def validate(self):
		self.set_status()
		self.validate_empty_accounts_table()
		if not self.title:
			self.title = self.get_title()

	def set_status(self):
		self.status = {
			"0": "Draft",
			"1": "Submitted",
			"2": "Cancelled"
		}[cstr(self.docstatus or 0)]

		if self.status == "Draft":
			self.status = "Draft"
		else:
			self.status = "Paid"
			

	def on_submit(self):
		self.make_gl_entries()
		self.set_status()

	def on_cancel(self):
		self.make_gl_entries(cancel=True)
		self.set_status()

	def get_title(self):
		if not self.expenses_entry_detail[0].expense_account:
			frappe.throw(_("Expense account is required in table"))
		return self.expenses_entry_detail[0].expense_account

	def validate_empty_accounts_table(self):
		if not self.get('expenses_entry_detail'):
			frappe.throw(_("Expense Entry table cannot be blank."))

	def make_gl_entries(self, cancel = False):
		gl_entries = self.get_gl_entries()
		make_gl_entries(gl_entries, cancel)

	def get_gl_entries(self):

		gl_entry = []
		self.validate_empty_accounts_table()
		self.validate_account_details()

		gl_payment_remarks=''
		if self.payment_remarks:
			gl_payment_remarks+=self.payment_remarks
		if self.reference_no:
			gl_payment_remarks+=' Reference #'+self.reference_no
		if self.reference_date:
			gl_payment_remarks+=' Dated '+cstr(self.reference_date)
		
		payable_amount = 0
		
		# expense entries


		
		for data in self.expenses_entry_detail:
			gl_expense_remarks=''
			for repeat in self.expenses_entry_detail:
				if data.expense_account==repeat.expense_account and data.idx!=repeat.idx:
					if repeat.expense_remarks:
						gl_expense_remarks=' '+gl_expense_remarks+ repeat.expense_remarks
					if repeat.serial_no:
						gl_expense_remarks=gl_expense_remarks+' Serial No#'+repeat.serial_no
				elif data.expense_account==repeat.expense_account and data.idx==repeat.idx:
					if repeat.expense_remarks:
						gl_expense_remarks=repeat.expense_remarks
					if repeat.serial_no:
						gl_expense_remarks=gl_expense_remarks+' Serial No#'+repeat.serial_no

			print data.idx
			print gl_expense_remarks
			gl_entry.append(
				self.get_gl_dict({
					"account": data.expense_account,
					"debit": data.amount,
					"debit_in_account_currency": data.amount,
					"cost_center": data.cost_center,
					"remarks":gl_expense_remarks
				})
			)
			payable_amount+=data.amount

		if payable_amount and self.paid_from_account:
		# payment entry
			gl_entry.append(
				self.get_gl_dict({
					"account": self.paid_from_account,
					"credit": payable_amount,
					"credit_in_account_currency": payable_amount,
					"against": ",".join([d.expense_account for d in self.expenses_entry_detail]),
					"against_voucher_type": self.doctype,
					"against_voucher": self.name,
					"remarks":gl_payment_remarks
				})
			)
		return gl_entry

	def validate_account_details(self):
		if not self.paid_from_account:
			frappe.throw(_("Please set default paid from account for the company {0}").format(getlink("Company",self.company)))

		for data in self.expenses_entry_detail:
			print data
			if not data.expense_account:
				frappe.throw(_("Expense account is required for {0} row").format(data.idx))
			if not data.cost_center:
				frappe.throw(_("Cost center is required for {0} row").format(data.idx))
			if not data.amount:
				frappe.throw(_("Amount is required for {0} row").format(data.idx))
			if  flt(data.amount)==0:
				frappe.throw(_("Amount can't be {0} for {1} row").format(data.amount,data.idx))

