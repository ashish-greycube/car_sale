# -*- coding: utf-8 -*-
# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form,flt
from frappe.utils.data import getdate, nowdate

class InternalEmployeeCommission(Document):
    
	def get_commission_details(self):

		total_commission = 0

		if(self.calculate_for =="Sales Person"):
			values = {'from_date':self.from_date,'to_date':self.to_date,'sales_person': self.party}
			self.clear_table('commission_details')

			query = """
				SELECT si.name, si.customer_name, si.sales_person_total_commission, si.sales_person, sii.item_name, sii.serial_no, sii.name AS sii_name
				FROM `tabSales Invoice` si
				INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
				WHERE si.sales_person = %(sales_person)s
				AND si.posting_date >= %(from_date)s
                AND si.posting_date <= %(to_date)s
				AND sii.name NOT IN(SELECT iecd.si_items_hex_name
        		FROM `tabInternal Employee Commission` iec
        		INNER JOIN `tabInternal Employee Commission Detail` iecd ON iec.name = iecd.parent
        		WHERE iec.party = %(sales_person)s
          		AND iec.docstatus=1)
			"""
			
			result = frappe.db.sql(query, values=values, as_dict=True,debug=1)

			
			for row in result:
				profit_for_party_sales_person = row.sales_person_total_commission
				self.append('commission_details', {
					'sales_invoice': row.name,
					'item_name': row.item_name,
					'serial_no': row.serial_no,
					'customer_name': row.customer_name,
					'profit_for_party':profit_for_party_sales_person,
					'si_items_hex_name':row.sii_name,
					'sales_person':row.sales_person
				})
				total_commission += profit_for_party_sales_person
			self.total_commission = total_commission
				

		elif(self.calculate_for == "Sales Partner"):

			values = {'from_date':self.from_date,'to_date':self.to_date,'sales_partner': self.party}
			self.clear_table('commission_details')

			query = """
				SELECT si.name, si.customer_name, si.sales_person, si.commission_rate, sii.item_name, sii.rate, sii.serial_no, sn.purchase_rate, SUM(ee.amount) AS other_cost	
				FROM `tabSales Invoice` si
				INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
				INNER JOIN `tabSerial No` sn ON sn.name = sii.serial_no
				LEFT JOIN `tabExpenses Entry Detail` ee ON ee.serial_no = sii.serial_no
				WHERE si.sales_partner = %(sales_partner)s
				AND si.posting_date >= %(from_date)s
                AND si.posting_date <= %(to_date)s
				AND sii.name NOT IN(SELECT iecd.si_items_hex_name
        		FROM `tabInternal Employee Commission` iec
        		INNER JOIN `tabInternal Employee Commission Detail` iecd ON iec.name = iecd.parent
        		WHERE iec.party = %(sales_partner)s
          		AND iec.docstatus=1)
				
			"""

			result = frappe.db.sql(query, values=values, as_dict=True,debug=1)

			if result:

				for row in result:
						profit_computed = (row.rate or 0) - (row.purchase_rate or 0 - row.other_cost or 0)
						profit_for_party_sales_partner = (row.commission_rate)*(profit_computed)
						self.append('commission_details', {
							'sales_invoice': row.name,
							'item_name': row.item_name,
							'serial_no': row.serial_no,
							'customer_name': row.customer_name,
							'sales_amount':row.rate,
							'cogs':row.purchase_rate,
							'profit':profit_computed,
							'profit_for_party':profit_for_party_sales_partner,
							'other_cost':row.other_cost,
							'sales_person':row.sales_person,				
						})
						total_commission += profit_for_party_sales_partner
				self.total_commission = total_commission
			else:
				frappe.msgprint("No records found")

		else:
			frappe.msgprint("Select sales person / sales partner first")

	
	
	
	
	
	def clear_table(self, commission_details):
		self.set(commission_details, [])

	def on_submit(self):
		self.create_journal_entry()

	def create_journal_entry(self):
		accounts = []
		sales_partner_commission_account = frappe.get_value('Sales Partner', self.party, 'sales_partner_commission_account_cf')
		sales_partner_commission_expense_account = frappe.db.get_value('Company', self.company, 'sales_partner_commission_expense_account_cf')
		
		sales_person_commission_account = frappe.get_value('Company', self.company, 'sales_person_commission_payable_account_cf')
		sales_person_commission_expense_account = frappe.db.get_value('Company', self.company, 'sales_person_commission_expense_account_cf')
		sales_person_party = frappe.get_value('Sales Person', self.party, 'employee')
		
		
		
		
		if self.calculate_for == 'Sales Partner':
			if not sales_partner_commission_account:
				frappe.throw("Sales Partner Commission Account not set for the selected Sales Partner.")
			
			if not sales_partner_commission_expense_account:
				frappe.throw("Sales Partner Commission Expense Account not set for the Company.")

			credit_account = sales_partner_commission_account
			debit_account = sales_partner_commission_expense_account
		
		# credit
			accounts.append({
				"account": credit_account,
				"credit_in_account_currency": self.total_commission,
			})
			# debit
			accounts.append({
				"account": debit_account,
				"debit_in_account_currency": self.total_commission,			
			})			
			
			journal_entry = frappe.new_doc('Journal Entry')
			journal_entry.voucher_type = 'Journal Entry'
			journal_entry.posting_date = getdate(nowdate())
			journal_entry.set("accounts", accounts)
			journal_entry.internal_employee_commission_ref_cf=self.name
			journal_entry.save(ignore_permissions=True)				
			journal_entry.submit()	
			msg = _('Journal Entry {} is created'.format(frappe.bold(get_link_to_form('Journal Entry', journal_entry.name))))
			frappe.msgprint(msg)

		elif self.calculate_for == 'Sales Person':

			if not sales_person_commission_account:
				frappe.throw("Sales Person Commission Account not set for the selected Person.")
			
			if not sales_person_commission_expense_account:
				frappe.throw("Sales Person Commission Expense Account not set for the Company.")
		
			credit_account = sales_person_commission_account
			debit_account = sales_person_commission_expense_account

			# credit
			accounts.append({
				"account": credit_account,
				"credit_in_account_currency": self.total_commission,
				'party_type': 'Employee',
				'party': sales_person_party
			})
			# debit
			accounts.append({
				"account": debit_account,
				"debit_in_account_currency": self.total_commission,
				'party_type': 'Employee',
				'party': sales_person_party				
			})

			journal_entry = frappe.new_doc('Journal Entry')
			journal_entry.voucher_type = 'Journal Entry'
			journal_entry.posting_date = getdate(nowdate())
			journal_entry.set("accounts", accounts)
			journal_entry.internal_employee_commission_ref_cf=self.name
			journal_entry.save(ignore_permissions=True)				
			journal_entry.submit()	
			msg = _('Journal Entry {} is created'.format(frappe.bold(get_link_to_form('Journal Entry', journal_entry.name))))
			frappe.msgprint(msg)

	def on_cancel(self):
		self.unlink_journal_entry()

	def unlink_journal_entry(self):
		journal_entry = frappe.get_doc("Journal Entry", {"internal_employee_commission_ref_cf": self.name})
		
		if journal_entry:
			journal_entry.cancel()
			frappe.msgprint(_("Associated Journal Entry {0} is canceled.".format(get_link_to_form('Journal Entry', journal_entry.name))))
		else:
			frappe.msgprint(_("No associated Journal Entry found for this Internal Employee Commission."))