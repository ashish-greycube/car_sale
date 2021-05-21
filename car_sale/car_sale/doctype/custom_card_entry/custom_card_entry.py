# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from frappe.utils import cint,cstr
from frappe import _
from erpnext import get_default_company
from frappe.utils import get_link_to_form

class CustomCardEntry(Document):

	def on_submit(self):
		if self.from_doctype=='Purchase Order':
			self.match_serial_no_and_qty()
			self.auto_make_serial_nos()
		else:
			self.update_serial_no_status_from_custom_card()

	def match_serial_no_and_qty(self):
		for item in self.custom_card_item:
			if not frappe.get_cached_value('Item', item.item_code, 'has_serial_no'):
				continue
			if not item.serial_no:
				frappe.throw(_('Row #{0}: {1} does not have any serial number').format(frappe.bold(item.idx), frappe.bold(item.item_code)))
			if len(get_serial_nos(item.serial_no)) == item.qty:
				continue			
			frappe.throw(_('For item {0} at row {1}, count of serial numbers does not match with the quantity')
				.format(frappe.bold(item.item_code), frappe.bold(item.idx)))	

	def auto_make_serial_nos(self):
		created_numbers = []
		for item in self.custom_card_item:
			if frappe.get_cached_value('Item', item.item_code, 'has_serial_no')==1 and frappe.get_cached_value('Item', item.item_code, 'is_stock_item')==1:
				serial_nos = get_serial_nos(item.serial_no)
				for serial_no in serial_nos:
					sr = frappe.new_doc("Serial No")
					sr.serial_no=serial_no
					sr.item_code=item.item_code
					sr.company=get_default_company()
					sr.custom_card_exist_cf='Yes'
					sr.reservation_status='Available-Card'
					sr.custom_card_no_cf=self.name
					sr.save(ignore_permissions=True)
					created_numbers.append(sr.name)

		form_links = list(map(lambda d: get_link_to_form('Serial No', d), created_numbers))
		if len(form_links) == 1:
			frappe.msgprint(_("Serial No {0} created").format(form_links[0]))
		elif len(form_links) > 0:
			frappe.msgprint(_("The following serial numbers were created: <br> {0}").format(', '.join(form_links)))	

	def update_serial_no_status_from_custom_card(self):
		""" update serial no doc with details of Custom Card """
		custom_card_doc = self.name
		if custom_card_doc:
			for item in self.custom_card_item:
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
							sno.custom_card_exist='Yes'
							sno.save(ignore_permissions=True)
						elif len(serial_no)==0:
							pass
						else:
							# check for invalid serial number
							frappe.throw(_("{0} is invalid serial number").format(serial_no))		
