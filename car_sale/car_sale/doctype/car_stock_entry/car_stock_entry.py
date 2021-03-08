# -*- coding: utf-8 -*-
# Copyright (c) 2021, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import cstr,get_link_to_form
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
class CarStockEntry(Document):

	def get_PO_items_detail(self,po_reference):
		items = frappe.db.sql('''
					select POI.item_code as item_code,sum(qty) as qty from `tabPurchase Order` PO
					inner join `tabPurchase Order Item` POI
					on PO.name=POI.parent
					where PO.name=%s
					and PO.docstatus!=2
					group by POI.item_code
					order by POI.item_code
		''', (po_reference), as_dict=True)

		return items		

	def get_existing_CSE_items(self,po_reference):
		items = frappe.db.sql('''
					select CSED.item_code as item_code,sum(CSED.qty) as qty from 
					`tabCar Stock Entry` CSE inner join
					`tabCar Stock Entry Detail` CSED
					on CSE.name=CSED.parent
					where 
					CSE.entry_type='Receipt'
					and CSE.po_reference=%s
					and CSED.docstatus !=2
					and CSE.name !=%s
					group by CSED.item_code
		''', (po_reference,self.name), as_dict=True)

		return items

	def validate(self):
		CSE_items=self.get_existing_CSE_items(self.po_reference)
		PO_items=self.get_PO_items_detail(self.po_reference)
		# check if any extra item
		if PO_items:
			for row_item in self.items:
				found_item=False
				for po_item in PO_items:
					if row_item.item_code==po_item.item_code:
						found_item=True
						if row_item.qty>po_item.qty:
							frappe.throw(_('Row #{0}: item {1} is having qty {2}. It should be not be more than {3}').format(
								frappe.bold(row_item.idx), frappe.bold(row_item.item_code),frappe.bold(row_item.qty),frappe.bold(po_item.qty)))
						break
				if found_item==False:
					frappe.throw(_('Row #{0}: item {1} doesnot exist in purchase order. Please remove it').format(frappe.bold(row_item.idx), frappe.bold(row_item.item_code)))

		# check if CSE qty across all CSE is within PO qty limit
		if CSE_items:
			for row_item in self.items:
				for cse_item in CSE_items:
					if row_item.item_code==cse_item.item_code:
						new_qty=row_item.qty+cse_item.qty
						for po_item in PO_items:
							if row_item.item_code==po_item.item_code:
								expected_qty=po_item.qty-cse_item.qty
								if new_qty>po_item.qty:
									frappe.throw(_('Row #{0}: item {1} entered qty is {2}. It should be not be more than {3}').format(
										frappe.bold(row_item.idx), frappe.bold(row_item.item_code),frappe.bold(row_item.qty),frappe.bold(expected_qty)))	
								else:								
									break
						break
		self.match_serial_no_and_qty()

	def item_exists_in_SO(item_code):
		return frappe.db.sql("""select item_code from `tabSales Order` as SO
								inner join `tabSales Order Item` as SOI
								on SO.name=SOI.parent
								where SOI.item_code = %(item_code)s
								and SO.docstatus in (0,1)
			""", {
				'item_code': item_code
			},as_dict=True)[0]		

	def change_serial_no_status(self):
		for item in self.items:
			serial_nos = get_serial_nos(item.serial_no)
			for serial_no in serial_nos:
				reservation_status=frappe.db.get_value('Serial No', serial_no, 'reservation_status')
				if reservation_status =='Available-Qty':
					frappe.db.set_value('Serial No', serial_no, 'reservation_status','Returned')
					frappe.msgprint(_('Row #{0}: item {1} with serial no {2}, reservation status is changed to Returned from Available-Qty')
						.format(frappe.bold(item.idx),frappe.bold(item.item_code),frappe.bold(serial_no)))					
				elif reservation_status not in ['Reserved', 'Sold Out', 'Available']:
					frappe.db.set_value('Serial No', serial_no, 'reservation_status','Returned')
					frappe.msgprint(_("Row #{0}: item {1} with serial no {2}, reservation status is changed to Returned as reservation status is not in 'Reserved', 'Sold Out', 'Available'")
						.format(frappe.bold(item.idx),frappe.bold(item.item_code),frappe.bold(serial_no)))						
				elif not item_exists_in_SO(item.item_code):
					frappe.db.set_value('Serial No', serial_no, 'reservation_status','Returned')
					frappe.msgprint(_("Row #{0}: item {1} with serial no {2}, reservation status is changed to Returned as item is not in any draft or submit state Sales Order.")
						.format(frappe.bold(item.idx),frappe.bold(item.item_code),frappe.bold(serial_no)))						
				else:
					frappe.throw(_('Row #{0}: item {1} , serial no {2} doesnot meet criteria. <br> Hence it cannot be returned.').format(frappe.bold(item.idx), frappe.bold(item.item_code), frappe.bold(serial_no)))

	def on_submit(self):
		if self.entry_type=='Receipt':
			self.match_serial_no_and_qty()
			self.validate_serial_no_status()	
			self.auto_make_serial_nos()
			
		elif self.entry_type =='Return':
			self.match_serial_no_and_qty()
			self.change_serial_no_status()

	def match_serial_no_and_qty(self):
		for item in self.items:
			if not frappe.get_cached_value('Item', item.item_code, 'has_serial_no'):
				continue
			if not item.serial_no:
				frappe.throw(_('Row #{0}: {1} does not have any serial number').format(frappe.bold(item.idx), frappe.bold(item.item_code)))
			if len(get_serial_nos(item.serial_no)) == item.qty:
				continue
			frappe.throw(_('For item {0} at row {1}, count of serial numbers does not match with the quantity')
				.format(frappe.bold(item.item_code), frappe.bold(item.idx)))		

	def validate_serial_no_status(self):
		for item in self.items:
			serial_nos = get_serial_nos(item.serial_no)
			for serial_no in serial_nos:
				if frappe.db.exists("Serial No", serial_no):
					reservation_status=frappe.db.get_value('Serial No', serial_no, 'reservation_status')
					if reservation_status =='Returned':	
						frappe.db.set_value('Serial No', serial_no, 'status','Available-Qty')
						frappe.msgprint(_('Row #{0}: item {1} with serial no {2}, reservation status is changed to Available-Qty from Returned')
						.format(frappe.bold(item.idx),frappe.bold(item.item_code),frappe.bold(serial_no)))					
					else:	
						frappe.throw(_("Row No:{0}, Serial No : <b>{1}</b> is an existing serial no and its reservation status is not return. Please enter unique serial no.")
							.format(item.idx,serial_no))
					

	def auto_make_serial_nos(self):
		for item in self.items:
			if frappe.get_cached_value('Item', item.item_code, 'has_serial_no')==1 and frappe.get_cached_value('Item', item.item_code, 'is_stock_item')==1:
				serial_nos = get_serial_nos(item.serial_no)
				created_numbers = []
				for serial_no in serial_nos:
					if not frappe.db.exists("Serial No", serial_no):
						sr = frappe.new_doc("Serial No")
						sr.serial_no=serial_no
						sr.item_code=item.item_code
						sr.company=self.company
						sr.custom_card_exist_cf='No'
						sr.reservation_status='Available-Qty'
						sr.cse_warehouse_cf= self.warehouse
						sr.save(ignore_permissions=True)
						created_numbers.append(sr.name)

		form_links = list(map(lambda d: get_link_to_form('Serial No', d), created_numbers))
		if len(form_links) == 1:
			frappe.msgprint(_("Serial No {0} created").format(form_links[0]))
		elif len(form_links) > 0:
			frappe.msgprint(_("The following serial numbers were created: <br> {0}").format(', '.join(form_links)))		

