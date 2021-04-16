from __future__ import unicode_literals
from frappe import _

def get_data(data):
	non_standard_fieldnames=data['non_standard_fieldnames']
	non_standard_fieldnames['Car Stock Entry']='po_reference'
	non_standard_fieldnames['Custom Card Entry']='po_reference'
	# internal_links['Task']=['items', 'task_cf']
	# data['internal_links']=internal_links 

	transactions=data['transactions']
	transactions[0].update({'label': _('Related'),
				'items': ['Purchase Receipt', 'Purchase Invoice', 'Car Stock Entry','Custom Card Entry']})
	data['transactions']=transactions

	return data
