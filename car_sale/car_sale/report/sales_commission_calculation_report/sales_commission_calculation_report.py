# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import add_months, nowdate
from frappe.utils import getdate
from frappe.utils import flt,add_days,cint


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	data = get_entries(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": _("Sales Invoice"),
			"fieldname": "si_name",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 90,
		},
		{
			"label": _("Sales Person"),
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"options": "Sales Person",
			"width": 100,
		},
		{
			"label": _("Sales Person Total Commission"),
			"fieldname": "sales_person_total_commission",
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"label": _("Sales Partner"),
			"fieldname": "sales_partner",
			"fieldtype": "Link",
			"options": "Sales Partner",
			"width": 100,
		},
		{
			"label": _("Sales Partner Commission Rate"),
			"fieldname": "commission_rate",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("IEC"),
			"fieldname": "iec_name",
			"fieldtype": "Link",
			"options": "Internal Employee Commission",
			"width": 90,
		},
		{
			"label": _("IEC Total Commission"),
			"fieldname": "total_commission",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": _("Associated Journal Entry"),
			"fieldname": "je_name",
			"fieldtype": "Link",
			"options":"Journal Entry",
			"width": 170,
		},
		{
			"label": _("Journal Entry Total Credit/Debit"),
			"fieldname": "je_total",
			"fieldtype": "Currency",
			"width": 130,
		},
	]
	return columns

def get_entries(filters):
	# conditions = get_conditions(filters)

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if not (from_date and to_date):
		frappe.throw(_("Please specify both from date and to date."))

	entries = frappe.db.sql(
		"""
		SELECT
			si.name AS si_name, si.sales_person, si.sales_partner, si.sales_person_total_commission, si.commission_rate, iec.name AS iec_name, iec.total_commission, je.name AS je_name, je.total_credit AS je_total
		FROM
			`tabSales Invoice` si
		LEFT JOIN
			`tabInternal Employee Commission` iec ON si.sales_person = iec.party OR si.sales_partner = iec.party
		LEFT JOIN
			`tabJournal Entry` je ON iec.name = je.internal_employee_commission_ref_cf
		WHERE
			si.docstatus = 1
			AND iec.docstatus = 1
			AND je.docstatus = 1
			AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
			ORDER BY
			si.name DESC
		""",
		{"from_date": getdate(from_date), "to_date": getdate(to_date)},
		as_dict=True
	)

	return entries

# def get_conditions(filters):
# 	conditions = ""

# 	if filters.get("from_date"):
# 		conditions += " and si.posting_date >= %(from_date)s"
# 	if filters.get("to_date"):
# 		conditions += " and si.posting_date <= %(to_date)s"
	
# 	return conditions

