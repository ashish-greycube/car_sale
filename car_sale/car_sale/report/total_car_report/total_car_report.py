# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def csv_to_columns(csv_str):
    props = ["label", "fieldname", "fieldtype", "options", "width"]
    return [
        zip(props, [x.strip() for x in col.split(",")])
        for col in csv_str.split("\n")
        if col.strip()
    ]

def get_columns(filters=None):
    return csv_to_columns(
        """
Item Name,item_name,Data,,230
Warehouse,warehouse,,,160
Color,car_color_cf,,,70
Model,car_model_cf,,,70
Qty,qty,Int,,70
"""
    )

def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters=None):

    data = frappe.db.sql(
        """SELECT 
	tsn.item_name ,
	tsn.warehouse,
	tsn.car_color_cf ,
	tsn.car_model_cf ,
	count(tsn.name) qty
from
	`tabSerial No` as tsn
{conditions}
	and tsn.reservation_status in ('Available', 'Showroom Car', 'Available Individual') 
group by
     tsn.item_name ,
     tsn.warehouse,
     tsn.car_color_cf ,
     tsn.car_model_cf""".format(
            conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
    )

    return data
def get_conditions(filters=None):
    conditions = []
    if filters.get("item_code"):
        conditions += ["tsn.item_code = %(item_code)s"]
    if filters.get("warehouse"):
        conditions += ["tsn.warehouse = %(warehouse)s"]
    if filters.get("color"):
        conditions += ["tsn.car_color_cf = %(color)s"]
    if filters.get("model"):
        conditions += ["tsn.car_model_cf = %(model)s"]
    return conditions and " where " + " and ".join(conditions) or " where 1=1 "	