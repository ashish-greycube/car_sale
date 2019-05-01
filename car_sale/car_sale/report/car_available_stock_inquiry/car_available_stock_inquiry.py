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
		_("Car Name") + ":Link/Item:200",
		_("Warehouse") + ":Link/Warehouse:100",
		_("Quantity") + ":Int:40",
		_("Selling Rate") + ":Currency:100"
	]

def get_car_available_stock_inquiry(filters):
	print '-------------before'
	print filters
	# if filters=={}:
	# 	filters.update({"from_date": filters.get("from_date"),"to_date":filters.get("to_date"),
	# 	"serial_no":filters.get("serial_no"),"cost_center":filters.get("cost_center"),
	# 	"sales_person":filters.get("sales_person"),
	# 	"customer_name":filters.get("customer_name"),
	# 	"item_group":filters.get("item_group"),
	# 	"brand":filters.get("brand"),
	# 	"Category":filters.get("Category"),
	# 	"Color":filters.get("Color"),"model":filters.get("model")})
	# 	if filters.get("item_group")=='Select Group..':
	# 		filters.update({"item_group": None})
	# 	if filters.get("brand")=='Select Brand..':
	# 		filters.update({"brand": None})
	# 	if filters.get("Category")=='Select Category..':
	# 		filters.update({"Category": None})
	# 	if filters.get("Color")=='Select Color..':
	# 		filters.update({"Color": None})
	# 	if filters.get("model")=='Select Model..':
	# 		filters.update({"model": None})
	# else:
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

T.Quantity,

T.SellingRate

FROM ( SELECT

TS.item_name as CarName,

TS.warehouse as Warehouse,

count(serial_no) as Quantity,

TIP.price_list_rate AS SellingRate,

TI.variant_of,

TI.item_group,

MAX(IF (TVA.attribute ='Color',TVA.attribute_value,'')) AS Color,

MAX(IF (TVA.attribute ='model',TVA.attribute_value,'')) AS Model,

MAX(IF (TVA.attribute ='Category',TVA.attribute_value,'')) AS Category

FROM `tabSerial No` AS TS inner join

tabItem AS TI ON

TS.item_code = TI.item_code

INNER JOIN `tabItem Price` TIP ON

TS.item_code = TIP.item_code

AND selling = 1 and price_list = 'Standard Selling'

INNER JOIN  `tabItem Variant Attribute` AS TVA

ON TVA.parent = TI.item_code

WHERE

reservation_status  = 'Available'

and warehouse is not null

and 1= case when %(brand)s ='اختر النوع' then 1 when ( TI.variant_of= %(brand)s) then 1 else 0 end

and 1= case when %(item_group)s ='اختر المجموعة' then 1 when ( TI.item_group= %(item_group)s) then 1 else 0 end

group by

warehouse,

serial_no,

TS.item_name,

TI.variant_of,

TI.item_group
) T
 WHERE

1 = case when %(Color)s ='اختر اللون' THEN 1 when ( T.Color = %(Color)s ) then 1 ELSE 0 END

AND 1= case when %(model)s ='اختر الموديل' THEN 1 when ( T.Model = %(model)s )then 1 else 0 end

AND 1= case when %(Category)s ='اختر الفئة' then 1 when ( T.Category= %(Category)s) then 1 else 0 end""", filters, as_list=1)


	print car_available
	return car_available