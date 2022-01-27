# -*- coding: utf-8 -*-
# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form,flt
from frappe.utils.data import getdate, nowdate

class IndividualCarStockEntry(Document):
	def on_submit(self):
		if self.status not in ['Car Sold Out','Car Returned']:
			frappe.throw(_(" Status should be either 'Car Sold Out' or 'Car Returned'"))

	def create_sales_invoice(self):
		default_sales_invoice_naming_series = frappe.db.get_value('Company', self.company, 'default_sales_invoice_naming_series')
		cost_center = frappe.db.get_value('Company', self.company, 'cost_center')
		default_commission_item = frappe.db.get_value('Company', self.company, 'default_commission_item')
		default_car_individual_receivable_account = frappe.db.get_value('Company', self.company, 'default_car_individual_receivable_account')
		customer= self.customer_seller if self.commission_paid_by =='Seller' else self.customer_buyer

		total_expense=0
		for expense in self.individual_car_expense_detail:
			total_expense+=expense.amount		

		if self.commission_paid_by =='Seller':
			customer= self.customer_seller
		elif self.commission_paid_by =='Buyer':
			customer= self.customer_buyer
		rate=self.sale_rate-self.receive_rate-total_expense

		si = frappe.new_doc('Sales Invoice')
		si.naming_series=default_sales_invoice_naming_series
		si.customer=customer
		si.due_date=getdate(nowdate())
		si.cost_center=cost_center
		si.debit_to=default_car_individual_receivable_account
		row = si.append('items', {})		
		row.item_code=default_commission_item
		row.qty=1
		row.rate=rate

		si.flags.ignore_permissions = True
		si.ignore_pricing_rule = 1
		si.update_stock=0
		si.individual_car_entry_reference=self.name
		si.run_method("set_missing_values")
		si.run_method("set_po_nos")
		si.run_method("calculate_taxes_and_totals")		
		si.save()		
		self.sales_invoice_reference=si.name		
		msg = _('Sales Invoice {} is created'.format(frappe.bold(get_link_to_form('Sales Invoice',si.name))))
		frappe.msgprint(msg)		

	

	def create_other_journal_entry(self):
		accounts = []
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")
		default_car_individual_receivable_account = frappe.db.get_value('Company', self.company, 'default_car_individual_receivable_account')
		default_creditors_account= frappe.db.get_value('Company', self.company, 'default_creditors_account')

		total_expense=0
		for expense in self.individual_car_expense_detail:
			total_expense+=expense.amount		

		debit_amount=0
		credit_amount=0
		if self.commission_paid_by =='Seller':
			debit_amount=self.sale_rate
			credit_amount=self.sale_rate-total_expense
		elif self.commission_paid_by =='Buyer':
			debit_amount=self.receive_rate+total_expense
			credit_amount=self.receive_rate
		
		# debit
		accounts.append({
			"account": default_car_individual_receivable_account,
			"debit_in_account_currency": flt(debit_amount, precision),
			'party_type':'Customer',
			'party':self.customer_buyer				
		})			
		# credit
		accounts.append({
		"account": default_car_individual_receivable_account,
		"credit_in_account_currency": flt(credit_amount, precision),
		'party_type':'Customer',
		'party':self.customer_seller
		})

		if total_expense>0:
		# credit
			for expense in self.individual_car_expense_detail:
				accounts.append({
					"account": default_creditors_account,
					"credit_in_account_currency": flt(expense.amount, precision),
					'party_type':'Supplier',
					'party':expense.supplier				
				})		

		customer= self.customer_seller if self.commission_paid_by =='Seller' else self.customer_buyer
		user_remark=_('Car Stock Entry {0} \n Commission Paid by {1} \n Commission Paid by {2} \n Receive Rate {3} \n Sale Rate {4} \n Expense {5}'
		.format(self.name,self.commission_paid_by,customer,self.receive_rate,self.sale_rate,total_expense))
		
		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.voucher_type = 'Journal Entry'
		journal_entry.user_remark =user_remark
		journal_entry.company = self.company
		journal_entry.posting_date = getdate(nowdate())
		journal_entry.set("accounts", accounts)
		journal_entry.individual_car_entry_reference=self.name
		journal_entry.individual_car_entry_type='Other'
		journal_entry.save(ignore_permissions = True)				
		# journal_entry.submit()	
		msg = _('Other Journal Entry {} is created'.format(frappe.bold(get_link_to_form('Journal Entry',journal_entry.name))))
		frappe.msgprint(msg)			

	def create_payment_journal_entry(self):
		amount=self.sale_rate
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

		debit_account=frappe.db.sql("""SELECT acct.default_account FROM `tabMode of Payment` mode INNER JOIN `tabMode of Payment Account` acct ON mode.name=acct.parent
																		where mode.name= %s
																		and acct.company = %s
																		order by acct.idx ASC 
																		LIMIT 1""",(self.mode_of_payment,self.company), as_list=1)
		if debit_account and debit_account[0][0]:
					default_debit_account=debit_account[0][0]

		default_car_individual_receivable_account = frappe.db.get_value('Company', self.company, 'default_car_individual_receivable_account')

		accounts = []

		# debit entry
		accounts.append({
			"account": default_debit_account,
			"debit_in_account_currency": flt(amount, precision),
		})		

		# credit entry
		accounts.append({
			"account": default_car_individual_receivable_account,
			"credit_in_account_currency": flt(amount, precision),
			'party_type':'Customer',
			'party':self.customer_buyer
		})
		customer= self.customer_seller if self.commission_paid_by =='Seller' else self.customer_buyer
		user_remark=_('Car Stock Entry {0} \n Commission Paid by {1} \n Commission Paid by {2} \n Receive Rate {3} \n Sale Rate {4}'
		.format(self.name,self.commission_paid_by,customer,self.receive_rate,self.sale_rate))
		
		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.voucher_type = 'Journal Entry'
		journal_entry.user_remark =user_remark
		journal_entry.company = self.company
		journal_entry.posting_date = getdate(nowdate())
		journal_entry.set("accounts", accounts)
		journal_entry.individual_car_entry_reference=self.name
		journal_entry.individual_car_entry_type='Payment'
		journal_entry.save(ignore_permissions = True)				
		# journal_entry.submit()	
		msg = _('Payment Journal Entry {} is created'.format(frappe.bold(get_link_to_form('Journal Entry',journal_entry.name))))
		frappe.msgprint(msg)

	# def validate(self):
	# 	if self.status!='Car Received' and self.docstatus==0:
	# 		frappe.throw(_(" Status should be 'Car Received'"))

	def on_update(self):		
		if self.status=='Car Received' and self.docstatus==0:
			if not frappe.db.exists("Serial No", self.serial_no_data):
				sr = frappe.new_doc("Serial No")
				sr.serial_no=self.serial_no_data
				sr.item_code=self.item_code
				sr.item_name= frappe.db.get_value('Item',self.item_code, 'item_name')
				# sr.status='Available-Individual'
				sr.reservation_status='Available Individual'
				sr.individual_car_entry_date=self.entry_date
				sr.individual_car_entry_reference=self.name
				sr.customer_seller=self.customer_seller
				sr.customer_buyer=self.customer_buyer
				sr.save(ignore_permissions=True)
				self.generated_serial_no=sr.name
				msg = _('Serial No {} is created'.format(frappe.bold(get_link_to_form('Serial No',sr.name))))
				frappe.msgprint(msg)
			else:
				if not self.generated_serial_no:
						self.generated_serial_no=self.serial_no_data				
		if self.docstatus==1 and self.generated_serial_no:
			if self.status=='Car Sold Out':
				frappe.db.set_value('Serial No', self.generated_serial_no, { 'reservation_status': 'Sold Individual', 'individual_car_return_date': self.selling_or_return_date})
			elif self.status=='Car Returned':
				frappe.db.set_value('Serial No', self.generated_serial_no, { 'reservation_status': 'Returned Individual',   'individual_car_return_date': self.selling_or_return_date})
