# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from frappe.utils import cint,cstr
from frappe import _


class ShowroomCar(Document):


	def on_submit(self):
		self.create_serial_no_if_not_exist()
		self.update_reservation_status_from_showroom_car()

	def create_serial_no_if_not_exist(self):
		if self.showroom_car_item:
			for item in self.showroom_car_item:
				# check for empty serial no
				if not item.serial_no:
					service_item=frappe.get_list('Item', filters={'item_code': item.item_code}, fields=['is_stock_item', 'is_sales_item', 'is_purchase_item'],)[0]
					if service_item.is_stock_item==0 and service_item.is_sales_item==1 :
						pass
					else:
						frappe.throw(_("Row {0}: {1} Serial numbers required for Item {2}. You have provided None.".format(
							item.idx, item.qty, item.item_code)))
				else:
					# match item qty and serial no count
					serial_nos = item.serial_no
					si_serial_nos = set(get_serial_nos(serial_nos))
					if item.serial_no and cint(item.qty) != len(si_serial_nos):
						frappe.throw(_("Row {0}: {1} Serial numbers required for Item {2}. You have provided {3}.".format(
							item.idx, item.qty, item.item_code, len(si_serial_nos))))
					for serial_no in item.serial_no.split("\n"):
						if serial_no and frappe.db.exists('Serial No', serial_no) :
							#match item_code with serial number-->item_code
							sno_item_code=frappe.db.get_value("Serial No", serial_no, "item_code")
							if (cstr(sno_item_code) != cstr(item.item_code)):
								frappe.throw(_("{0} serial number is not valid for {1} item code").format(serial_no,item.item_code))
						elif len(serial_no)==0:
							pass
						else:
							# create serial number
							# New Serial No cannot have Warehouse. Warehouse must be set by Stock Entry or Purchase Receipt
							doc = frappe.new_doc('Serial No')
							doc.serial_no = serial_no
							doc.item_code=item.item_code
							doc.custom_card_exist_cf='No'
							doc.reservation_status='Showroom Car'
							# doc.warehouse=item.warehouse
							doc.serial_no_details='This is a showroom car.'
							doc.insert()	
							frappe.msgprint(_("{0} is created for item {1}").format("<a href='#Form/Serial No/{0}'>Serial No {0}</a>".format(doc.name),item.item_name))						


	def update_reservation_status_from_showroom_car(self):
		showroom_car_doc = self.name
		if showroom_car_doc:
			for item in self.showroom_car_item:
				# check for empty serial no
				if not item.serial_no:
					service_item=frappe.get_list('Item', filters={'item_code': item.item_code}, fields=['is_stock_item', 'is_sales_item', 'is_purchase_item'],)[0]
					if service_item.is_stock_item==0 and service_item.is_sales_item==1 :
						pass
					else:
						frappe.throw(_("Row {0}: {1} Serial numbers required for Item {2}. You have provided None.".format(
							item.idx, item.qty, item.item_code)))
				else:
					# match item qty and serial no count
					serial_nos = item.serial_no
					si_serial_nos = set(get_serial_nos(serial_nos))
					if item.serial_no and cint(item.qty) != len(si_serial_nos):
						frappe.throw(_("Row {0}: {1} Serial numbers required for Item {2}. You have provided {3}.".format(
							item.idx, item.qty, item.item_code, len(si_serial_nos))))
					for serial_no in item.serial_no.split("\n"):
						if serial_no and frappe.db.exists('Serial No', serial_no) :
							#match item_code with serial number-->item_code
							sno_item_code=frappe.db.get_value("Serial No", serial_no, "item_code")
							if (cstr(sno_item_code) != cstr(item.item_code)):
								frappe.throw(_("{0} serial number is not valid for {1} item code").format(serial_no,item.item_code))
							#check if there is delivery_document_no against serial no
							delivery_document_no = frappe.db.get_value("Serial No", serial_no, "delivery_document_no")
							if delivery_document_no and self.name != delivery_document_no:
								frappe.throw(_("Serial Number: {0} is already referenced in Delivery Document No: {1}".format(
								serial_no, delivery_document_no)))	
							sno = frappe.get_doc('Serial No', serial_no)
							if sno.reservation_status=='Sold Out':
								frappe.throw(_("It is sold out"))
							if sno.reservation_status=='Returned':
								frappe.throw(_("It is a returned showroom car"))								
							sno.reservation_status='Showroom Car'
							sno.save(ignore_permissions=True)
						elif len(serial_no)==0:
							pass
						else:
							# check for invalid serial number
							frappe.throw(_("{0} is invalid serial number").format(serial_no))		
