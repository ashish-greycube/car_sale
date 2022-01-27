from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'individual_car_entry_reference',
		'non_standard_fieldnames': {
			# 'Serial No': 'individual_car_entry_reference',
			# 'Sales Invoice':'sales_invoice_reference'
		},
		'transactions': [
			{
				'label': _('Serial No'),
				'items': ['Serial No']
			},
			{
				'label': _('Journal Entry'),
				'items': ['Journal Entry']
			},			
			{
				'label': _('Sales Invoice'),
				'items': ['Sales Invoice']
			}	
		]
	}