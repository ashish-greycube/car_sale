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
			"fieldname": "car_sales_partner_cf",
			"fieldtype": "Link",
			"options": "Sales Partner",
			"width": 100,
		},
		{
			"label": _("Sales Partner Commission Rate"),
			"fieldname": "car_sales_partner_commission_rate_cf",
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

	sales_person_entries = frappe.db.sql(
		"""
		SELECT
			si.name AS si_name, si.sales_person, si.car_sales_partner_cf, si.sales_person_total_commission, si.car_sales_partner_commission_rate_cf, iec.name AS iec_name, iec.total_commission, je.name AS je_name, je.total_credit AS je_total
		FROM
			`tabInternal Employee Commission` iec
		INNER JOIN
			`tabIEC Sales Person Detail` iespd ON
			iec.name=iespd.parent
		LEFT JOIN
			 `tabSales Invoice` si  ON si.name=iespd.sales_invoice and si.sales_person = iec.party
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
	sales_partner_entries = frappe.db.sql(
		"""
		SELECT
			si.name AS si_name, si.sales_person, si.car_sales_partner_cf, si.sales_person_total_commission, si.car_sales_partner_commission_rate_cf, iec.name AS iec_name, iec.total_commission, je.name AS je_name, je.total_credit AS je_total
		FROM
			`tabInternal Employee Commission` iec
		INNER JOIN
			`tabIEC Sales Partner Detail` iespd ON
			iec.name=iespd.parent
		LEFT JOIN
			 `tabSales Invoice` si  ON si.name=iespd.sales_invoice and si.car_sales_partner_cf = iec.party
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
	if len(sales_person_entries)>0:
		for sales_person in sales_person_entries:
			sales_partner_entries.append(sales_person)
	return sales_partner_entries

# def get_conditions(filters):
# 	conditions = ""

# 	if filters.get("from_date"):
# 		conditions += " and si.posting_date >= %(from_date)s"
# 	if filters.get("to_date"):
# 		conditions += " and si.posting_date <= %(to_date)s"
	
# 	return conditions

