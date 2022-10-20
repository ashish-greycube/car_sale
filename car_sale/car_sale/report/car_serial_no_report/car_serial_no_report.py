# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from distutils.log import debug
import frappe


def csv_to_columns(csv_str):
    props = ["label", "fieldname", "fieldtype", "options", "width"]
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
Plate No,registration_plate_no,,,110
Item Name,item_name,Data,,210
Model,car_model_cf,,,70
Color,car_color_cf,,,70
Car Status,reservation_status,,,120
Warehouse,warehouse,,,130
Purchase Invoice,purchase_invoice,Link,Purchase Invoice,110
Purchase Rate,purchase_rate,Currency,,110
Purchase Date,purchase_date,Date,,100
Supplier,supplier,Link,Supplier,130
Sales Invoice,sales_invoice,Link,Sales Invoice,110
Sales Rate,sales_rate,Currency,,120
Customer,customer,Link,Customer,100
Sales Date,sales_date,Date,,100
Booking No,booking_no,Link,Sales Order,100
Advance Amount,advance_amount,Currency,,120
"""
    )


def get_data(filters=None):

    data = frappe.db.sql(
        """
        select
	tsn .delivery_document_no sales_invoice ,
	tsn.delivery_date sales_date ,
	tsn.supplier ,
	tsn.customer ,
	tsii.rate ,
	tsn.reserved_by_document ,
	tsn.name serial_no ,
	tsn.registration_plate_no ,
	tsn.item_code ,
	tsn.item_name ,
	tsn.car_color_cf ,
	tsn.status ,
    tsn.warehouse,
	tsn.car_model_cf ,
	tsn.reservation_status ,
	tpi.name purchase_invoice ,
	tpi.posting_date purchase_date,
	tpii.rate ,
	tso.advance_paid as advance
from
	`tabSerial No` tsn
left outer join `tabPurchase Invoice Item` tpii on
	tpii.item_code = tsn.item_code
	and tpii.serial_no = tsn.name
left outer join `tabPurchase Invoice` tpi on
	tpi.name = tpii.parent
	and tpi.docstatus = 1
left outer join `tabSales Invoice Item` tsii on
	tsii.parent = tsn.delivery_document_no
	and tsii.item_code = tsn.item_code
	and tsii.serial_no = tsn.name
	and tsii.docstatus = 1
left outer join `tabSales Order` tso on
	tso.name = tsn.reserved_by_document
    {conditions}
    """.format(
            conditions=get_conditions(filters)
        ),
        filters,
        debug=True,
        as_dict=True,
    )

    return data


def get_conditions(filters=None):
    conditions = []
    if filters.get("item_code"):
        conditions += ["tsn.item_code = %(item_code)s"]
    if filters.get("customer"):
        conditions += ["tsi.customer = %(customer)s"]
    if filters.get("color"):
        conditions += ["tsn.car_color_cf = %(color)s"]
    if filters.get("model"):
        conditions += ["tsn.car_model_cf = %(model)s"]
    if filters.get("reservation_status"):
        conditions += ["tsn.reservation_status = %(reservation_status)s"]
    if filters.get("warehouse"):
        conditions += ["tsn.cse_warehouse_cf = %(warehouse)s"]

    return conditions and " where " + " and ".join(conditions) or ""
