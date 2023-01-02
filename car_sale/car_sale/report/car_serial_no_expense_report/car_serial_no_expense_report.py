# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from distutils.log import debug
import frappe
import erpnext


def csv_to_columns(csv_str):
    props = ["label", "fieldname", "fieldtype", "options", "width", "precision"]
    return [
        zip(props, [x.strip() for x in col.split(",")])
        for col in csv_str.split("\n")
        if col.strip()
    ]


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_columns(filters=None):
    return csv_to_columns(
        """
Serial No,serial_no,Link,Serial No,130
Item Name,item_name,Data,,210
Color,car_color_cf,,,70
Model,car_model_cf,,,70
Supplier,supplier,Link,Supplier,110,
Purchase Reference,purchase_invoice,Link,Purchase Invoice,100,
Purchase Date,purchase_date,Date,,100
Receive Rate,receive_rate,Currency,,120
Purchase Rate,cost_amount,Currency,,120
Plate No Cost,plate_no_cost,Currency,,100
Insurance Expense,insurance_expense,Currency,,100
Transfer Cost,transfer_cost,Currency,,100
Maintenance Cost,maintenance_cost,Currency,,100
Other Expense,other_expense,Currency,,100
Total Expense,total_expense,Currency,,110
Total Cost,total_cost,Currency,,110
"""
    )


def get_conditions(filters=None):
    conditions = []

    conditions += ["1=1"]

    if filters.get("item_code"):
        conditions += ["tsn.item_code = %(item_code)s"]
    if filters.get("customer"):
        conditions += ["tsi.customer = %(customer)s"]
    if filters.get("color"):
        conditions += ["tsn.car_color_cf = %(color)s"]
    if filters.get("model"):
        conditions += ["tsn.car_model_cf = %(model)s"]
    if filters.get("car_type"):
        car_type_filter = filters.get("car_type")
        if car_type_filter == "Individual Car":
            conditions += ["tsn.individual_car_entry_reference   IS NOT NULL "]
        elif car_type_filter == "Purchase Car":
            conditions += ["tsn.individual_car_entry_reference   IS  NULL "]
    return conditions and " where " + " and ".join(conditions) or ""


def get_data(filters=None):
    filters["company"] = erpnext.get_default_company()

    # TODO: logic for cost amount

    data = frappe.db.sql(
        """
    select 
	tsn.name serial_no ,
	tsn.item_code ,
	tsn.item_name ,
	tsn.car_color_cf ,
	tsn.car_model_cf ,
	tpi.supplier ,
	tpi.name as purchase_invoice,
	tpi.posting_date as purchase_date,
	CASE
		WHEN tsn.individual_car_entry_reference is not null THEN (
		select
			icse.receive_rate
		from
			`tabIndividual Car Stock Entry` icse
		left outer join `tabIndividual Car Expense Detail` iced on
			icse.name = iced.parent
		where
			icse.name = tsn.individual_car_entry_reference
		group by
			icse.name
)	END as receive_rate,	
	CASE
		WHEN tsn.individual_car_entry_reference is not null THEN (
		select
			icse.receive_rate + COALESCE(sum(iced.amount),0)
		from
			`tabIndividual Car Stock Entry` icse
		left outer join `tabIndividual Car Expense Detail` iced on
			icse.name = iced.parent
		where
			icse.name = tsn.individual_car_entry_reference
		group by
			icse.name
)
		ELSE tsn.purchase_rate
	END as cost_amount,
	exp.plate_no_cost ,
	exp.insurance_expense ,
	exp.transfer_cost ,
	exp.maintenance_cost ,
	exp.other_expense ,
	coalesce(COALESCE(exp.plate_no_cost,0) + COALESCE(exp.insurance_expense,0) + COALESCE(exp.transfer_cost,0) + COALESCE(exp.maintenance_cost,0) + COALESCE(exp.other_expense), 0) as total_expense,
	(COALESCE((SELECT total_expense),0) + COALESCE((SELECT cost_amount),0)) as total_cost 
from `tabSerial No` tsn
left outer join `tabPurchase Invoice Item` tpii on
	tpii.item_code = tsn.item_code
	and tpii.serial_no = tsn.name
    and tpii.docstatus = 1
left outer join `tabPurchase Invoice` tpi on
	tpi.name = tpii.parent
	and tpi.docstatus = 1
left outer join (
	select
		serial_no ,
		sum(case when expense_account in 
            (select car_plate_no_cost_account_cf from tabCompany where name = %(company)s) then amount else 0 end) plate_no_cost ,
		sum(case when expense_account in 
            (select car_insurance_expense_account_cf from tabCompany where name = %(company)s) then amount else 0 end) insurance_expense ,
		sum(case when expense_account in 
            (select car_transfer_cost_account_cf from tabCompany where name = %(company)s) then amount else 0 end) transfer_cost ,
		sum(case when expense_account in 
            (select car_maintenance_cost_account_cf from tabCompany where name = %(company)s) then amount else 0 end) maintenance_cost ,
		sum(case when expense_account in 
            (select car_other_expense_account_cf from tabCompany where name = %(company)s) then amount else 0 end) other_expense
	from
		(
		select
			teed.expense_account ,
			teed.amount ,
			teed.serial_no
		from
			`tabExpense Entry` tee
		inner join `tabExpenses Entry Detail` teed on
			teed.parent = tee.name
			and tee.docstatus = 1
			and teed.serial_no is not null
	union all
		select
			tjea.account ,
			tje.total_debit ,
			tjea.serial_no_cf
		from
			`tabJournal Entry` tje
		inner join `tabJournal Entry Account` tjea on
			tjea.parent = tje.name
			and tje.docstatus = 1
			and tjea.serial_no_cf is not null
	union all
		select
			tpii.expense_account ,
			tpii.amount ,
			tpii.serial_no
		from
			`tabPurchase Invoice` tpi
		inner join `tabPurchase Invoice Item` tpii on
			tpii.parent = tpi.name
			and tpi.docstatus = 1
			and tpii.serial_no is not null
        ) t
	group by
		serial_no	
	) exp on
	exp.serial_no = tsn.name 
          {conditions} 
    """.format(
            conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True
    )

    # for d in data:
    #     d["net_profit"] = (d.get("total_expense", 0) or 0) + (d.get("cost_amount") or 0)
    #     d["percentage"] = (
    #         (d.get("net_profit") or 0) * 100 / d.get("sales_amount")
    #         if d.get("sales_amount")
    #         else 0
    #     )

    return data
