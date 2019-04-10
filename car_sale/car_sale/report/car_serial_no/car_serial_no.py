# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns=get_column()
	data = get_car_serial_no(filters)
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


def get_car_serial_no(filters):
	print 'before'
	print filters
	if filters=={}:
		filters.update({"supplier": filters.get("supplier"),"warehouse":filters.get("warehouse"),"serialno":filters.get("serialno"),"Status":filters.get("Status"),"Color":filters.get("Color"),"Model":filters.get("Model"),"Category":filters.get("Category"),"Brand":filters.get("Brand")})
	else:
		if filters.get("supplier")==None:
			filters.update({"supplier": filters.get("supplier")})
		if filters.get("warehouse")==None:
			filters.update({"warehouse": filters.get("warehouse")})
		if filters.get("serialno")==None:
			filters.update({"serialno": filters.get("serialno")})
		if filters.get("Status")=='Select Status..':
			filters.update({"Status": filters.get("Status")})
		if filters.get("Color")=='Select Color..':
			filters.update({"Color": filters.get("Color")})
		if filters.get("Model")=='Select Model..':
			filters.update({"Model": filters.get("Model")})
		if filters.get("Category")=='Select Category..':
			filters.update({"Category": filters.get("Category")})
		if filters.get("Brand")=='Select Brand..':
			filters.update({"Brand": filters.get("Brand")})
	print 'after'
	print filters

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
 SalesPerson FROM ( SELECT 
TS.item_name as ItemName,
serial_no as SerialNo,
reservation_status as Status,
purchase_rate as PurchaseRate,
warehouse as Warehouse,
supplier as Supplier,
purchase_document_no AS PINV_STE,
purchase_date as DateOfPurchase , 
reserved_by_document as BookReference,
sales_partner as SalesPerson,
TI.variant_of AS Brand,
TI.item_group AS ItemGroup,
MAX(IF (TVA.attribute ='Color',TVA.attribute_value,'')) AS Color,
MAX(IF (TVA.attribute ='Model',TVA.attribute_value,'')) AS Model,
MAX(IF (TVA.attribute ='Category',TVA.attribute_value,'')) AS Category
FROM `tabSerial No` AS TS inner join 
tabItem AS TI ON 
TS.item_code = TI.item_code
INNER JOIN  `tabItem Variant Attribute` AS TVA
ON TVA.parent = TI.item_code
group by sales_partner, 
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
AND 1 = case when %(Status)s  ='Select Status..' THEN 1 when ( T.Status = %(Status)s ) then 1 ELSE 0 END
AND 1 = case when %(Color)s  ='Select Color..' THEN 1 when ( T.Color = %(Color)s ) then 1 ELSE 0 END
AND 1= case when %(Model)s ='Select Model..' THEN 1 when ( T.Model = %(Model)s )then 1 else 0 end
AND 1= case when %(Category)s ='Select Category..' then 1 when ( T.Category= %(Category)s) then 1 else 0 end
AND 1= case when %(Brand)s ='Select Brand..' then 1 when ( T.Brand = %(Brand)s) then 1 else 0 end
	""", filters, as_list=1)