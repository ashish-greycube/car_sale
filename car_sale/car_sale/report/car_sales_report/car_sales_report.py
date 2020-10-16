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
	data = get_car_sales_analysis(filters)
	if data:
		total_row=get_count_of_serial_no(data,columns)
		data.append(total_row)
	return columns, data

def get_column():
	return [
		_("CostCenter") + ":Link/Cost Center:40",
		_("ID") + ":Link/Sales Invoice:120",
		_("Date") + ":Date:80",
		_("SerialNo") + ":Link/Serial No:90",
		_("ItemCode") + ":Link/Item:150",
		_("CustomerID") + ":Link/Customer:120",
		_("CustomerName") + ":Data:90",
		_("TotalSelling") + ":Currency:90",
		_("SalesPerson") + ":Link/Sales Person:90"
	]

def get_count_of_serial_no(data,columns):
	# total_row is actually column position
	total_row = ['']*len(columns)
	count=0
	for d in data:
			if d[3]:
				count=+count+1
			total_row[7] = flt(total_row[7]) + flt(d[7])
	total_row[3] = cstr(count)
	total_row[0] = '<b>TOTAL :</b>'
	return total_row


def get_car_sales_analysis(filters):
	if filters=={}:
		filters.update({"from_date": filters.get("from_date"),"to_date":filters.get("to_date"),
		"serial_no":filters.get("serial_no"),"cost_center":filters.get("cost_center"),
		"sales_person":filters.get("sales_person"),
		"customer_name":filters.get("customer_name"),
		"item_group":filters.get("item_group"),
		"brand":filters.get("brand"),
		"Category":filters.get("Category"),
		"Color":filters.get("Color"),"model":filters.get("model")})
		if filters.get("item_group")=='Select Group..':
			filters.update({"item_group": None})
		if filters.get("brand")=='Select Brand..':
			filters.update({"brand": None})
		if filters.get("Category")=='Select Category..':
			filters.update({"Category": None})
		if filters.get("Color")=='Select Color..':
			filters.update({"Color": None})
		if filters.get("model")=='Select Model..':
			filters.update({"model": None})
	else:
		if filters.get("from_date")==None:
			filters.update({"from_date": filters.get("from_date")})
		if filters.get("to_date")==None:
			filters.update({"to_date": filters.get("to_date")})
		if filters.get("serial_no")==None:
			filters.update({"serial_no": filters.get("serial_no")})
		if filters.get("cost_center")==None:
			filters.update({"cost_center": filters.get("cost_center")})
		if filters.get("sales_person")==None:
			filters.update({"sales_person": filters.get("sales_person")})
		if filters.get("customer_name")==None:
			filters.update({"customer_name": filters.get("customer_name")})
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


	car_sales= frappe.db.sql("""select

A.CostCenter,

A.ID,

A.Date,

A.SerialNo,

A.ItemCode,

A.CustomerID,

A.CustomerName,

A.TotalSelling,

A.SalesPerson,

A.Color,

A.Model,

A.Category

from

(SELECT

SI.cost_center AS CostCenter,

SI.name as ID,

SI.posting_date as Date,

SN.serial_no as SerialNo,

SIT.item_code as ItemCode,

SIT.item_name as ItemName,

SI.customer as CustomerID,

SI.customer_name as CustomerName,

SN.purchase_rate as PurchaseRate,

SN.plate_cost AS PlateCost,

SIT.base_net_amount as TotalSelling,

SI.sales_person as SalesPerson ,

SI.tax_id as TaxID,

TI.variant_of AS Brand,

TI.item_group AS ItemGroup,

MAX(IF (TVA.attribute ='Color',TVA.attribute_value,'')) AS Color,

MAX(IF (TVA.attribute ='model',TVA.attribute_value,'')) AS Model,

MAX(IF (TVA.attribute ='Category',TVA.attribute_value,'')) AS Category

from `tabSales Invoice` AS SI

INNER join `tabSales Invoice Item` as SIT

              ON     SIT.parent = SI.name  and SI.docstatus = 1

INNER JOIN `tabItem` TI

               ON TI.item_code = SIT.item_code

INNER JOIN  `tabItem Variant Attribute` AS TVA

              ON TVA.parent = TI.item_code

INNER JOIN `tabSerial No` AS SN

             ON FIND_IN_SET(SN.serial_no, REPLACE(SIT.serial_no, '\n', ',' )) > 0

WHERE

SI.posting_date >= %(from_date)s and SI.posting_date <= %(to_date)s

AND 1= case when %(serial_no)s IS NULL then 1 when ( SN.serial_no= %(serial_no)s) then 1 else 0 end

AND 1= case when %(cost_center)s IS NULL then 1 when ( SI.cost_center= %(cost_center)s) then 1 else 0 end

AND 1= case when %(sales_person)s IS NULL then 1 when ( SI.sales_person= %(sales_person)s) then 1 else 0 end

AND 1= case when %(customer_name)s IS NULL then 1 when ( SI.customer = %(customer_name)s) then 1 else 0 end

AND 1= case when %(item_group)s ='اختر المجموعة' then 1 when ( TI.item_group= %(item_group)s) then 1 else 0 end

AND 1= case when %(brand)s ='اختر النوع' then 1 when ( TI.variant_of= %(brand)s) then 1 else 0 end

group by

SI.cost_center,

SI.name,

SI.posting_date,

SN.serial_no,

SI.customer,

SI.customer_name,

SN.purchase_rate,

SN.plate_cost,

SIT.base_net_amount,

SI.sales_person,

SI.tax_id,

TI.variant_of,

TI.item_group

) A

       LEFT  JOIN

       (SELECT sum(transfer_cost) AS TransferCost, SED.serial_no   from `tabStock Entry` AS SE INNER JOIN `tabStock Entry Detail` AS SED

       ON SE.name = SED.parent AND SE.with_transfer_cost = 1 and SE.docstatus = 1 group by SED.serial_no) B

       ON A.SerialNo = B.serial_no

       LEFT  JOIN (select

       TWI.serial_no,

       TPI.rate as GaureenteeCardCost

       from  `tabWarranty Card Issued` AS TWI

       INNER JOIN `tabPurchase Invoice Item` TPI

       ON TWI.purchase_invoice = TPI.parent

       AND TWI.name in (REPLACE(TPI.description,"|",","))

       group by TWI.serial_no

       ) C

       ON A.SerialNo = C.serial_no    

       LEFT  JOIN

                     (select

                     sum(EED.amount) as ServiceCost,

                     EED.serial_no

                     from `tabExpenses Entry Detail` as EED

                     INNER JOIN `tabExpense Entry` as EE

                     ON EE.name = EED.parent and EE.docstatus = 1

                     group by EED.serial_no) D

       ON A.SerialNo = D.serial_no    

       group by A.SerialNo 

        having

1 = case when %(Color)s ='اختر اللون' THEN 1 when ( A.Color = %(Color)s ) then 1 ELSE 0 END

       AND 1= case when %(model)s ='اختر الموديل' THEN 1 when ( A.Model = %(model)s )then 1 else 0 end

       AND 1= case when %(Category)s ='اختر الفئة' then 1 when ( A.Category= %(Category)s) then 1 else 0 end""", filters, as_list=1)


	return car_sales