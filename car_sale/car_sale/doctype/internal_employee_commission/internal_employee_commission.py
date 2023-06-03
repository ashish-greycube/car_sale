# -*- coding: utf-8 -*-
# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InternalEmployeeCommission(Document):
    
	def get_commission_details(self):

		
		# sales_person = self.party
		# query = """
        #     SELECT si.name, si.customer_name, si.sales_person, sii.item_name, sii.serial_no
        #     FROM `tabSales Invoice` si
        #     INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        #     WHERE si.sales_person = %s
        # """
	
		# result = frappe.db.sql(query,(sales_person), as_dict=True)

		

		if(self.calculate_for =="Sales Person"):
			values = {'from_date':self.from_date,'to_date':self.to_date,'sales_person': self.party}
			self.clear_table('commission_details')

			query = """
				SELECT si.name, si.customer_name, si.search_serial_no, si.sales_person_total_commission, si.sales_person, sii.item_name
				FROM `tabSales Invoice` si
				INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
				WHERE si.sales_person = %(sales_person)s
				AND si.posting_date >= %(from_date)s
                AND si.posting_date <= %(to_date)s
			"""

			result = frappe.db.sql(query, values=values, as_dict=True)


			for row in result:
					self.append('commission_details', {
						'sales_invoice': row.name,
						'item_name': row.item_name,
						'serial_no': row.search_serial_no,
						'customer_name': row.customer_name,
						'profit_for_party':row.sales_person_total_commission,
						'sales_person':row.sales_person
						
					})

		elif(self.calculate_for == "Sales Partner"):

			values = {'from_date':self.from_date,'to_date':self.to_date,'sales_partner': self.party}
			self.clear_table('commission_details')

			query = """
				SELECT si.name, si.customer_name, si.search_serial_no, si.sales_person, si.commission_rate, sii.item_name, sii.rate, sn.purchase_rate, SUM(ee.amount) AS other_cost	
				FROM `tabSales Invoice` si
				INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
				INNER JOIN `tabSerial No` sn ON sn.name = si.search_serial_no
				LEFT JOIN `tabExpenses Entry Detail` ee ON ee.serial_no = si.search_serial_no
				WHERE si.sales_partner = %(sales_partner)s
				AND si.posting_date >= %(from_date)s
                AND si.posting_date <= %(to_date)s
				
			"""

			result = frappe.db.sql(query, values=values, as_dict=True)


			for row in result:
					profit_computed = row.rate - row.purchase_rate - row.other_cost
					profit_for_party_sales_partner = (row.commission_rate)*(profit_computed)
					self.append('commission_details', {
						'sales_invoice': row.name,
						'item_name': row.item_name,
						'serial_no': row.search_serial_no,
						'customer_name': row.customer_name,
						'sales_amount':row.rate,
						'cogs':row.purchase_rate,
						'profit':profit_computed,
						'profit_for_party':profit_for_party_sales_partner,
						'other_cost':row.other_cost,
						'sales_person':row.sales_person,
						
					})
		else:
			frappe.msgprint("Select sales person / sales partner first")

	def clear_table(self, commission_details):
		self.set(commission_details, [])

