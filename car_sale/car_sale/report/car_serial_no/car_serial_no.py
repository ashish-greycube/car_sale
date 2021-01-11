# -*- coding: UTF-8 -*-
# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr

def execute(filters=None):
	columns, data = [], []
	columns=get_column()
	data = get_car_serial_no(filters)
	if data:
		total_row=get_count_of_serial_no(data,columns)
		data.append(total_row)
	return columns, data

def get_column():
	return [
		_("ItemName") + "::220",
		_("SerialNo") + ":Link/Serial No:100",
		_("Status") + "::70",
		_("PurchaseRate") + ":Currency:90",
		_("Warehouse") + ":Link/Warehouse:80",
		_("Supplier") + ":Link/Supplier:120",
		_("PINV_STE") + "::150",
		_("DateOfPurchase") + "::70",
		_("BookReference") + "::150",
		_("SalesPerson") + ":Link/Sales Person:90"
	]

def get_count_of_serial_no(data,columns):
	total_row = ['']*len(columns)
	count=0
	for d in data:
			if d[1]:
				count=+count+1
	total_row[1] = cstr(count)
	total_row[0] = '<b>TOTAL :</b>'
	return total_row

def get_car_serial_no(filters):
	if filters=={}:
		filters.update({"supplier": filters.get("supplier"),"warehouse":filters.get("warehouse"),"serialno":filters.get("serialno"),"Status":filters.get("Status"),"Color":filters.get("Color"),"model":filters.get("model"),"Category":filters.get("Category"),"Brand":filters.get("Brand")})
	else:
		if filters.get("supplier")==None:
			filters.update({"supplier": filters.get("supplier")})
		if filters.get("warehouse")==None:
			filters.update({"warehouse": filters.get("warehouse")})
		if filters.get("serialno")==None:
			filters.update({"serialno": filters.get("serialno")})
		if filters.get("Status")==_("اختر الحالة"):
			filters.update({"Status": filters.get("Status")})
		if filters.get("Color")==_("اختر اللون"):
			filters.update({"Color": filters.get("Color")})
		if filters.get("model")==_("اختر الموديل"):
			filters.update({"model": filters.get("model")})
		if filters.get("Category")==_("اختر الفئة"):
			filters.update({"Category": filters.get("Category")})
		if filters.get("Brand")==_("اختر النوع"):
			filters.update({"Brand": filters.get("Brand")})

	return frappe.db.sql("""
SELECT 
ItemName,
SerialNo,
Status,
PurchaseRate,
Warehouse,
Supplier,
PINV_STE,
DateOfPurchase , 
BookReference,
SalesPerson FROM (SELECT 
TS.item_name as ItemName,
serial_no as SerialNo,
reservation_status as Status,
purchase_rate as PurchaseRate,
warehouse as Warehouse,
supplier as Supplier,
coalesce(original_purchase_doc_no_cf,purchase_document_no) AS PINV_STE,
purchase_date as DateOfPurchase , 
reserved_by_document as BookReference,
TS.sales_person as SalesPerson,
TI.variant_of AS Brand,
TI.item_group AS ItemGroup,
MAX(IF (TVA.attribute ='Color',TVA.attribute_value,'')) AS Color,
MAX(IF (TVA.attribute ='model',TVA.attribute_value,'')) AS model,
MAX(IF (TVA.attribute ='Category',TVA.attribute_value,'')) AS Category
FROM `tabSerial No` AS TS inner join 
tabItem AS TI ON 
TS.item_code = TI.item_code
INNER JOIN  `tabItem Variant Attribute` AS TVA
ON TVA.parent = TI.item_code
group by TS.sales_person, 
reserved_by_document, 
purchase_date, 
purchase_document_no,
supplier,
warehouse,
purchase_rate, 
reservation_status,
serial_no,
TS.item_name,
TI.variant_of,
TI.item_group) T 
WHERE  
1 = case when %(supplier)s IS NULL THEN 1 when ( T.Supplier = %(supplier)s ) then 1 ELSE 0 END
AND 1 = case when %(warehouse)s IS NULL THEN 1 when ( T.Warehouse = %(warehouse)s ) then 1 ELSE 0 END
AND 1 = case when %(serialno)s IS NULL THEN 1 when ( T.SerialNo= %(serialno)s ) then 1 ELSE 0 END
AND 1 = case when %(Status)s  ='اختر الحالة' THEN 1 when ( T.Status = %(Status)s ) then 1 ELSE 0 END
AND 1 = case when %(Color)s  ='اختر اللون' THEN 1 when ( T.Color = %(Color)s ) then 1 ELSE 0 END
AND 1= case when %(model)s ='اختر الموديل' THEN 1 when ( T.model = %(model)s )then 1 else 0 end
AND 1= case when %(Category)s ='اختر الفئة' then 1 when ( T.Category= %(Category)s) then 1 else 0 end
AND 1= case when %(Brand)s ='اختر النوع' then 1 when ( T.Brand = %(Brand)s) then 1 else 0 end
	""", filters, as_list=1)