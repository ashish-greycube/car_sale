# -*- coding: UTF-8 -*-
# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,cstr

def execute(filters=None):
	columns, data = [], []
	columns=get_column()
	data = get_car_available_stock_inquiry(filters)
	return columns, data

def get_column():

    return [
        {"label": _("Car Name"), 'width': 250, "fieldname": "CarName", 'fieldtype': 'Link/Item'},
		{"label":_("Warehouse"), 'width': 170, "fieldname": "Warehouse", 'fieldtype': 'Link/Warehouse'},
		{"label": _("Qty"), 'width': 41, "fieldname": "Quantity", 'fieldtype': 'Int'},
        {"label": _("Selling Rate"), 'width': 100, "fieldname": "SellingRate", 'fieldtype': 'Int'}
    ]

def get_car_available_stock_inquiry(filters):
	if filters.get("item_group")==None:
		filters.update({"item_group": _("اختر المجموعة")})
	if filters.get("brand")==None:
		filters.update({"brand": _("اختر النوع")})
	if filters.get("Category")==None:
		filters.update({"Category": _("اختر الفئة")})
	if filters.get("Color")==None:
		filters.update({"Color": _("اختر اللون")})
	if filters.get("model")==None:
		filters.update({"model": _("اختر الموديل")})

	car_available= frappe.db.sql("""SELECT

T.CarName,

T.Warehouse,

count(T.serial_no) as Quantity,

T.SellingRate

FROM

( SELECT

       TS.item_name as CarName,

       TS.warehouse as Warehouse,

       TS.serial_no,

       IFNULL(TIP.price_list_rate,0) AS SellingRate,

       TI.variant_of,

       TI.item_group,

       MAX(IF (TVA.attribute ='Color',TVA.attribute_value,'')) AS Color,

       MAX(IF (TVA.attribute ='model',TVA.attribute_value,'')) AS Model,

       MAX(IF (TVA.attribute ='Category',TVA.attribute_value,'')) AS Category

FROM `tabSerial No` AS TS inner join

        `tabItem` AS TI ON

       TS.item_code = TI.item_code

INNER JOIN  `tabItem Variant Attribute` AS TVA

              ON TVA.parent = TI.item_code

LEFT JOIN `tabItem Price` TIP

              ON TS.item_code = TIP.item_code

              AND TIP.selling = 1 and TIP.price_list = 'Standard Selling'

WHERE

       TS.reservation_status  = 'Available'

       and TS.warehouse is not null

       and 1= case when %(brand)s ='اختر النوع' then 1 when ( TI.variant_of= %(brand)s) then 1 else 0 end

       and 1= case when %(item_group)s ='اختر المجموعة' then 1 when ( TI.item_group= %(item_group)s) then 1 else 0 end

group by

       TS.item_name,

       TS.warehouse,

       TS.serial_no,

       TI.variant_of,

       TI.item_group

) T

 WHERE

       1 = case when %(Color)s ='اختر اللون' THEN 1 when ( T.Color = %(Color)s ) then 1 ELSE 0 END

       AND 1= case when %(model)s ='اختر الموديل' THEN 1 when ( T.Model = %(model)s )then 1 else 0 end

       AND 1= case when %(Category)s ='اختر الفئة' then 1 when ( T.Category= %(Category)s) then 1 else 0 end

group by

       T.CarName,

       T.Warehouse,

       T.SellingRate""", filters, as_list=1)


	return car_available