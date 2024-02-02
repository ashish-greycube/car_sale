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
			self.clear_table('iec_sales_person_commission_details')
			self.total_commission = total_commission

			query = """
				SELECT si.name, si.customer_name, si.sales_person_total_commission_per_car_cf, si.sales_person, sii.item_code, sii.item_name, sii.serial_no, sii.name AS sii_name,si.company
				FROM `tabSales Invoice` si
				INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
				WHERE si.sales_person = %(sales_person)s
				AND si.posting_date >= %(from_date)s
                AND si.posting_date <= %(to_date)s
				AND si.docstatus=1
				AND si.individual_car_entry_reference is NULL
				AND sii.serial_no is NOT NULL
				AND sii.name NOT IN(SELECT iecd.si_items_hex_name
        		FROM `tabInternal Employee Commission` iec
        		INNER JOIN `tabIEC Sales Person Detail` iecd ON iec.name = iecd.parent
        		WHERE iec.party = %(sales_person)s
          		AND iec.docstatus=1)
			"""

			result = frappe.db.sql(query, values=values, as_dict=True,debug=1)
			if result and len(result)>0:
				self.company=result[0].company
				for row in result:
					profit_for_party_sales_person = row.sales_person_total_commission_per_car_cf
					self.append('iec_sales_person_commission_details', {
						'sales_invoice': row.name,
						'item_code': row.item_code,
						'item_name': row.item_name,
						'serial_no': row.serial_no,
						'customer_name': row.customer_name,
						'profit_for_party':profit_for_party_sales_person,
						'si_items_hex_name':row.sii_name,
						'sales_person':row.sales_person
					})
					total_commission += profit_for_party_sales_person
				self.total_commission = total_commission

			#  individual car entry
			query2 = """
				SELECT si.name, si.customer_name, si.sales_person_total_commission_per_car_cf, si.sales_person, sii.item_code, sii.item_name, si.individual_car_entry_serial_no_cf, sii.name AS sii_name,si.company,
				si.individual_car_entry_reference
				FROM `tabSales Invoice` si
				INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
				WHERE si.sales_person = %(sales_person)s
				AND si.posting_date >= %(from_date)s
                AND si.posting_date <= %(to_date)s
				AND si.docstatus=1
				AND si.individual_car_entry_reference is NOT NULL
				AND sii.name NOT IN(SELECT iecd.si_items_hex_name
        		FROM `tabInternal Employee Commission` iec
        		INNER JOIN `tabIEC Sales Person Detail` iecd ON iec.name = iecd.parent
        		WHERE iec.party = %(sales_person)s
          		AND iec.docstatus=1)
			"""

			result2 = frappe.db.sql(query2, values=values, as_dict=True,debug=1)
			if result2 and len(result2)>0:
				self.company=result2[0].company
				for row in result2:
					profit_for_party_sales_person = row.sales_person_total_commission_per_car_cf
					self.append('iec_sales_person_commission_details', {
						'sales_invoice': row.name,
						'item_code': row.item_code,
						'item_name': row.item_name,
						'serial_no': row.individual_car_entry_serial_no_cf,
						'customer_name': row.customer_name,
						'profit_for_party':profit_for_party_sales_person,
						'si_items_hex_name':row.sii_name,
						'sales_person':row.sales_person
					})
					total_commission += profit_for_party_sales_person
				self.total_commission = self.total_commission + total_commission

			else:
				frappe.msgprint("No records found")	

		elif(self.calculate_for == "Sales Partner"):
			values = {'from_date':self.from_date,'to_date':self.to_date,'car_sales_partner_cf': self.party}
			self.clear_table('iec_sales_partner_commission_details')
			self.total_commission = total_commission

			query = """
				SELECT si.name, si.customer_name, si.car_sales_partner_cf, si.car_sales_partner_commission_rate_cf,sii.item_code, sii.item_name, sii.net_rate, sii.serial_no, sn.purchase_rate,SUM(IFNULL(ee.amount,0)) AS other_cost,si.company	
				FROM `tabSales Invoice` si
				INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
				INNER JOIN `tabSerial No` sn ON sn.name = sii.serial_no
				LEFT JOIN `tabExpenses Entry Detail` ee ON ee.serial_no = sii.serial_no and ee.docstatus=1
				WHERE si.car_sales_partner_cf = %(car_sales_partner_cf)s
				AND si.posting_date >= %(from_date)s
                AND si.posting_date <= %(to_date)s
				AND si.docstatus=1
				AND si.individual_car_entry_reference is NULL
				AND sii.name NOT IN(SELECT iecd.si_items_hex_name
        		FROM `tabInternal Employee Commission` iec
        		INNER JOIN `tabIEC Sales Partner Detail` iecd ON iec.name = iecd.parent
        		WHERE iec.party = %(car_sales_partner_cf)s
          		AND iec.docstatus=1)
			  	group by sii.serial_no
				
			"""
			result = frappe.db.sql(query, values=values, as_dict=True,debug=1)

			if result and len(result)>0:
				self.company=result[0].company
				for row in result:
						profit_computed = (row.net_rate or 0) - (row.purchase_rate or 0) - (row.other_cost or 0)
						profit_for_party_sales_partner = ((row.car_sales_partner_commission_rate_cf)*(profit_computed))/100
						self.append('iec_sales_partner_commission_details', {
							'sales_invoice': row.name,
							'item_code': row.item_code,
							'item_name': row.item_name,
							'serial_no': row.serial_no,
							'customer_name': row.customer_name,
							'sales_amount':row.net_rate,
							'cogs':row.purchase_rate,
							'profit':profit_computed,
							'profit_for_party':profit_for_party_sales_partner,
							'other_cost':row.other_cost,
							'sales_person':row.sales_person,				
						})
						total_commission += profit_for_party_sales_partner
				self.total_commission = total_commission

			# individual car stock entry
			query2 = """
				SELECT si.name, si.customer_name, si.car_sales_partner_cf, si.car_sales_partner_commission_rate_cf,sii.item_code, sii.item_name, sii.net_rate, si.individual_car_entry_serial_no_cf, 
				sn.purchase_rate, (SUM(IFNULL(ee.amount,0) )+SUM(IFNULL(iced.amount,0))) AS other_cost,si.company,si.individual_car_entry_reference
				FROM `tabSales Invoice` si
				INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
				INNER JOIN `tabSerial No` sn ON sn.name = si.individual_car_entry_serial_no_cf
				INNER JOIN `tabIndividual Car Expense Detail` iced ON si.individual_car_entry_reference = iced.parent
				LEFT JOIN `tabExpenses Entry Detail` ee ON ee.serial_no = si.individual_car_entry_serial_no_cf and ee.docstatus=1
				WHERE si.car_sales_partner_cf = %(car_sales_partner_cf)s
				AND si.posting_date >= %(from_date)s
                AND si.posting_date <= %(to_date)s
				AND si.docstatus=1
				AND si.individual_car_entry_reference is NOT NULL
				AND sii.name NOT IN(SELECT iecd.si_items_hex_name
        		FROM `tabInternal Employee Commission` iec
        		INNER JOIN `tabIEC Sales Partner Detail` iecd ON iec.name = iecd.parent
        		WHERE iec.party = %(car_sales_partner_cf)s
          		AND iec.docstatus=1)
			  	group by si.individual_car_entry_serial_no_cf
				
			"""
			result2 = frappe.db.sql(query2, values=values, as_dict=True,debug=1)

			if result2 and len(result2)>0:
				# self.company=result2[0].company
				for row in result2:
						profit_computed = (row.net_rate or 0) - (row.purchase_rate or 0) - (row.other_cost or 0)
						profit_for_party_sales_partner = ((row.car_sales_partner_commission_rate_cf)*(profit_computed))/100
						self.append('iec_sales_partner_commission_details', {
							'sales_invoice': row.name,
							'item_code': row.item_code,
							'item_name': row.item_name,
							'serial_no': row.individual_car_entry_serial_no_cf,
							'customer_name': row.customer_name,
							'sales_amount':row.net_rate,
							'cogs':row.purchase_rate,
							'profit':profit_computed,
							'profit_for_party':profit_for_party_sales_partner,
							'other_cost':row.other_cost,
							'sales_person':row.sales_person,				
						})
						total_commission += profit_for_party_sales_partner
				self.total_commission = self.total_commission + total_commission				
				
			else:
				frappe.msgprint("No records found")

		else:
			frappe.msgprint("Select sales person / sales partner first")
	
	def clear_table(self, table_name):
		self.set(table_name, [])

	def on_submit(self):
		self.create_journal_entry()

	def create_journal_entry(self):
		accounts = []
		if self.calculate_for == 'Sales Partner':
			sales_partner_commission_account_cf = frappe.get_value('Sales Partner', self.party, 'sales_partner_commission_account_cf')
			if not sales_partner_commission_account_cf:
				frappe.throw("Sales partner commission account is not set for the selected sales partner.")

			sales_partner_commission_expense_account_cf = frappe.db.get_value('Company', self.company, 'sales_partner_commission_expense_account_cf')			
			if not sales_partner_commission_expense_account_cf:
				frappe.throw("Sales partner commission expense account is not set for the company.")

			credit_account = sales_partner_commission_account_cf
			debit_account = sales_partner_commission_expense_account_cf
		
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
			sales_person_commission_payable_account_cf = frappe.get_value('Company', self.company, 'sales_person_commission_payable_account_cf')
			if not sales_person_commission_payable_account_cf:
				frappe.throw("Sales person commission payable account is not set for the company.")
			sales_person_party = frappe.get_value('Sales Person', self.party, 'employee')

			sales_person_commission_expense_account_cf = frappe.db.get_value('Company', self.company, 'sales_person_commission_expense_account_cf')			
			if not sales_person_commission_expense_account_cf:
				frappe.throw("Sales person commission expense account is not set for the company.")
		
			credit_account = sales_person_commission_payable_account_cf
			debit_account = sales_person_commission_expense_account_cf

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