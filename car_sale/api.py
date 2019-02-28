from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import (cstr, validate_email_add, cint,flt, comma_and, has_gravatar, now, getdate, nowdate)
from frappe.model.mapper import get_mapped_doc
import frappe, json
from erpnext.controllers.selling_controller import SellingController
from frappe.contacts.address_and_contact import load_address_and_contact
from erpnext.accounts.party import set_taxes
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.party import get_party_account_currency
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
import datetime

# Lead to Quotation

@frappe.whitelist()
def make_quotation_for_customer(source_name,target_doc=None):
	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
		quotation = frappe.get_doc(target)

		company_currency = frappe.db.get_value("Company", quotation.company, "default_currency")
		party_account_currency = get_party_account_currency("Customer", quotation.customer,
			quotation.company) if quotation.customer else company_currency

		quotation.currency = party_account_currency or company_currency

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(quotation.currency, company_currency,
				quotation.transaction_date)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=quotation.company)
		if taxes.get('taxes'):
			quotation.update(taxes)

		# quotation.quotation_to = "Lead"
		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		quotation.run_method("set_other_charges")
		
	def update_quotation(source_doc, target_doc, source_parent):
		target_doc.quotation_to = "Customer"
		target_doc.linked_lead=source_doc.name
		
		if source_doc.customer:
			if source_doc.transaction_type=='Bank Funded':
				# target_doc.customer=source_doc.bank_name
				# target_doc.sub_customer=source_doc.customer
				target_doc.customer=get_customernamingseries(source_doc.bank_name)
				target_doc.sub_customer=get_customernamingseries(source_doc.customer)
				
			else:
				# target_doc.customer=source_doc.customer
				target_doc.customer=get_customernamingseries(source_doc.customer)
		else:
			if source_doc.organization_lead==0 and source_doc.transaction_type=='Cash':
				# target_doc.customer=source_doc.lead_name
				target_doc.customer=get_customernamingseries(source_doc.lead_name)
			elif source_doc.organization_lead==1 and source_doc.transaction_type=='Cash':
				# target_doc.customer=source_doc.company_name
				target_doc.customer=get_customernamingseries(source_doc.company_name)
			elif source_doc.organization_lead==0 and source_doc.transaction_type=='Bank Funded':
				# target_doc.customer=source_doc.bank_name
				# target_doc.sub_customer=source_doc.lead_name
				target_doc.customer=get_customernamingseries(source_doc.bank_name)
				target_doc.sub_customer=get_customernamingseries(source_doc.lead_name)
			elif source_doc.organization_lead==1 and source_doc.transaction_type=='Bank Funded':
				# target_doc.customer=source_doc.bank_name
				# target_doc.sub_customer=source_doc.company_name
				target_doc.customer=get_customernamingseries(source_doc.bank_name)
				target_doc.sub_customer=get_customernamingseries(source_doc.company_name)
	def update_sales_team(obj, target, source_parent):
		target.sales_person = source_parent.sales_person
		target.allocated_percentage= 100
		target.car_sale_incentives=frappe.get_value('Sales Person', source_parent.sales_person, 'incentive')
	table_maps={
			"Lead": 
			{"doctype": "Quotation",
			"field_map": 
			{"name": "lead","customer":"lead_name","transaction_date":"date"},
			"postprocess": update_quotation
			},
			"Inquiry Item": 
			{"doctype": "Quotation Item",
			"field_map": {"name":"quotation_item","parent": "against_inquiry_item","uom": "stock_uom"},
			"add_if_empty": True
			},
			"Sales Team":
			{"doctype": "Sales Team",
			"postprocess": update_sales_team,
			"add_if_empty": True
			}
		}
	target_doc = get_mapped_doc("Lead",source_name,table_maps, target_doc,set_missing_values)
	# target_doc.quotation_to = "Lead"
	target_doc.save(ignore_permissions=True)

	source_lead = frappe.get_doc('Lead', source_name)
	source_lead.linked_quotation=target_doc.name
	# source_lead.set_status(update=True,status='Quotation')
	source_lead.save(ignore_permissions=True)

	return target_doc
@frappe.whitelist()
def get_incentive_of_sales_person(sales_person):
	incentives=frappe.get_value('Sales Person',sales_person, 'incentive')
	return incentives if incentives else None
# Lead to Customer
@frappe.whitelist()
def make_customer_from_lead(doc):
	doc=frappe._dict(json.loads(doc))
	sales_person=doc.sales_team[0]['sales_person']
	incentives=doc.sales_team[0]['car_sale_incentives']
	print incentives
	print 'incentives'
	#check existing contact
	contact_name = frappe.db.get_value('Contact',{'mobile_no': doc.mobile_no}, 'name')
	if contact_name:
		#existing contact
		print 'duplicate'
	else:
		#new contact
		if doc.organization_lead==1:
			customer_type='Company'
			customer_name=doc.company_name
			customer = frappe.new_doc("Customer")
			customer.customer_type=customer_type
			customer.lead_name=doc.name
			customer.customer_group=doc.customer_group
			customer.territory=doc.territory
			customer.customer_name=customer_name
			# customer.default_sales_partner=doc.sales_person
			customer.append('sales_team',{"sales_person":sales_person,"allocated_percentage":100,"car_sale_incentives":incentives})
			customer.insert(ignore_permissions=True)
			args={
				'name':doc.lead_name,
				'mobile_no':doc.mobile_no,
				'email_id':doc.email_id,
				'doctype':"Customer",
				'link_name':customer.name
				}
			contact=make_contact(args)
			customer.customer_primary_contact=contact.name
			customer.mobile_no=contact.mobile_no
			customer.email_id=contact.email_id
			customer.save(ignore_permissions=True)
	
		else:
			customer_type='Individual'
			customer_name=doc.lead_name
		# create contact and customer
			customer = frappe.new_doc("Customer")
			customer.customer_type=customer_type
			customer.lead_name=doc.name
			customer.customer_group=doc.customer_group
			customer.territory=doc.territory
			customer.customer_name=customer_name
			# customer.default_sales_partner=doc.sales_person
			customer.append('sales_team',{"sales_person":sales_person,"allocated_percentage":100,"car_sale_incentives":incentives})
			print customer.sales_team[0].sales_person
			print customer.sales_team[0].allocated_percentage
			print customer.sales_team[0].car_sale_incentives
			customer.insert(ignore_permissions=True)
			primary_contact=get_customer_primary_contact(customer.name)
			customer.customer_primary_contact=primary_contact['name']
			customer.mobile_no=primary_contact['mobile_no']
			customer.email_id=primary_contact['email_id']
			customer.save(ignore_permissions=True)
			print customer
		return

#Helpler function for creating contact
def make_contact(args, is_primary_contact=1):
	contact = frappe.get_doc({
		'doctype': 'Contact',
		'first_name': args.get('name'),
		'mobile_no': args.get('mobile_no'),
		'email_id': args.get('email_id'),
		'is_primary_contact': is_primary_contact,
		'links': [{
			'link_doctype': args.get('doctype'),
			'link_name': args.get('link_name')
		}]
	}).insert()
	return contact



def get_customer_primary_contact(customer):
	return frappe.db.sql("""
		select `tabContact`.name, `tabContact`.mobile_no, `tabContact`.email_id from `tabContact`, `tabDynamic Link`
			where `tabContact`.name = `tabDynamic Link`.parent and `tabDynamic Link`.link_name = %(customer)s
			and `tabDynamic Link`.link_doctype = 'Customer' and `tabContact`.is_primary_contact = 1
		""", {
			'customer': customer
		},as_dict=True)[0]

# Helper function for JS
@frappe.whitelist()
def get_existing_customer(mobile_no):
	existing_customer= frappe.db.sql("""
		select st.sales_person,cust.customer_group,
			cust.customer_type,
			cust.customer_name,
			cust.name,
			RTRIM(concat(cont.first_name,' ',ifnull(cont.last_name,'')))as person_name,
			cont.email_id,
			cont.mobile_no
		from `tabCustomer` cust 
        inner join `tabSales Team` st
        on cust.name=st.parent
		inner join `tabContact` cont
		on cust.customer_primary_contact=cont.name
		where st.idx=1
        and st.parenttype='Customer'
        and cont.mobile_no= %(mobile_no)s
		""", {
			'mobile_no': mobile_no
		},as_dict=True)
	if existing_customer:
		frappe.msgprint(_("Existing Contact").format(existing_customer[0]['customer_name']),indicator='green', alert=1)
	else:
		frappe.msgprint(_("New Contact"),indicator='red', alert=1)

	return existing_customer[0] if existing_customer else None

@frappe.whitelist()
def get_bank_name(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name from `tabCustomer`
where 
docstatus<2 
and bank_customer=1""",as_list=True)

@frappe.whitelist()
def get_branch_of_sales_partner(sales_partner=None):
	if sales_partner:
		return frappe.db.sql("""select branch from `tabSales Partner`
where 
docstatus<2 
and name=%s""",sales_partner,as_list=True)[0][0]
	else:
		return None


@frappe.whitelist()
def get_branch_of_sales_person(sales_person=None):
	if sales_person:
		return frappe.db.sql("""select branch from `tabSales Person`
where 
docstatus<2 
and name=%s""",sales_person,as_list=True)[0][0]
	else:
		return None



@frappe.whitelist()
def get_item_details(item_code):
	item = frappe.db.sql("""select item_name, stock_uom, image, description, item_group, brand
		from `tabItem` where name = %s""", item_code, as_dict=1)
	return {
		'item_name': item and item[0]['item_name'] or '',
		'uom': item and item[0]['stock_uom'] or '',
		'description': item and item[0]['description'] or '',
		'image': item and item[0]['image'] or '',
		'item_group': item and item[0]['item_group'] or '',
		'brand': item and item[0]['brand'] or ''
	}

@frappe.whitelist()
def get_sales_person_and_branch(user_email):
	sales_partner= frappe.db.sql("""select name,branch from `tabSales Person`
where
is_group=0
and user_id=%(user_email)s
	""",{
			'user_email': user_email
		},as_list=True)
	return sales_partner if sales_partner else None

# Update status : Lead to Sales Order
@frappe.whitelist()
def update_lead_status_from_sales_order(self,method):
	if self.linked_lead:
		name_of_linked_lead=self.linked_lead
		lead=frappe.get_doc("Lead",name_of_linked_lead)

		if lead.linked_sales_order== None or lead.linked_sales_order=='':
			print name_of_linked_lead
			print 'name_of_linked_lead'
			lead.db_set('linked_sales_order', self.name)
	
		if cstr(lead.status) in ['Lead','Open','Sales Inquiry','Quotation','Converted']:
			lead.db_set('status', 'Ordered')
	else:
		get_quotation= frappe.db.sql("""select distinct(soitem.prevdoc_docname) as quotation_name
	from `tabSales Order` so 
	inner join `tabSales Order Item` soitem 
	on so.name=soitem.parent 
	where soitem.prevdoc_docname is not null
	and so.name=%s
	order by soitem.modified desc
	limit 1""", self.name, as_list=1)
		if get_quotation:
			quotation_name=get_quotation[0][0]
			lead_name=frappe.get_value("Quotation",quotation_name,'linked_lead')
			if lead_name:
				lead=frappe.get_doc("Lead",lead_name)
				if cstr(lead.status) in ['Lead','Open','Sales Inquiry','Quotation','Converted']:
					lead.db_set('status', 'Ordered')



# Update Status : Lead to Quotation
@frappe.whitelist()
def update_lead_status_from_quotation(self,method):
	if self.linked_lead:
		lead=frappe.get_doc("Lead",self.linked_lead)
		if cstr(lead.status) in ['Lead','Open','Sales Inquiry','Converted']:
		# lead.status='Quotation'
		# lead.save(ignore_permissions=True)
			lead.db_set('status', 'Quotation')


def get_customernamingseries(customer_name):
	customernamingseries=frappe.db.sql("""select name from `tabCustomer` where customer_name=%s""",customer_name,as_list=True) 
	print customernamingseries
	if customernamingseries==None or customernamingseries==[] :
		customernamingseries=customer_name
		print customernamingseries
		print 'customernamingseries'
		return customernamingseries
	else:
		print customer_name
		print customernamingseries[0][0]
		print 'customernamingseries[0][0]'
		return customernamingseries[0][0] if customernamingseries else None

@frappe.whitelist()
def _make_sales_order(source_name, target_doc=None, ignore_permissions=True):
	# customer = _make_customer(source_name, ignore_permissions)

	def update_so(source_doc, target_doc, source_parent):
		#target_doc.quotation_to = "Customer"
		target_doc.linked_lead=source_doc.name
		target_doc.delivery_date=source_doc.date
		if source_doc.customer:
			if source_doc.transaction_type=='Bank Funded':
				# target_doc.customer=source_doc.bank_name
				# target_doc.sub_customer=source_doc.customer
				target_doc.customer=get_customernamingseries(source_doc.bank_name)
				target_doc.sub_customer=get_customernamingseries(source_doc.customer)
			else:
				# target_doc.customer=source_doc.customer
				target_doc.customer=get_customernamingseries(source_doc.customer)
		else:
			if source_doc.organization_lead==0 and source_doc.transaction_type=='Cash':
				# target_doc.customer=source_doc.lead_name
				target_doc.customer=get_customernamingseries(source_doc.lead_name)
			elif source_doc.organization_lead==1 and source_doc.transaction_type=='Cash':
				# target_doc.customer=source_doc.company_name
				target_doc.customer=get_customernamingseries(source_doc.company_name)
			elif source_doc.organization_lead==0 and source_doc.transaction_type=='Bank Funded':
				# target_doc.customer=source_doc.bank_name
				# target_doc.sub_customer=source_doc.lead_name
				target_doc.customer=get_customernamingseries(source_doc.bank_name)
				target_doc.sub_customer=get_customernamingseries(source_doc.lead_name)

			elif source_doc.organization_lead==1 and source_doc.transaction_type=='Bank Funded':
				# target_doc.customer=source_doc.bank_name
				# target_doc.sub_customer=source_doc.company_name
				target_doc.customer=get_customernamingseries(source_doc.bank_name)
				target_doc.sub_customer=get_customernamingseries(source_doc.company_name)

	def set_missing_values(source, target):
		# if customer:
		# 	target.customer = customer.name
		# 	target.customer_name = customer.customer_name
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")
		# target.save(ignore_permissions=True)

	def update_item(obj, target, source_parent):
		target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)
		target.delivery_date=source_parent.date

	def update_sales_team(obj, target, source_parent):
		target.sales_person = source_parent.sales_person
		target.allocated_percentage= 100
		target.car_sale_incentives=frappe.get_value('Sales Person', source_parent.sales_person, 'incentive')

	doclist = get_mapped_doc("Lead", source_name, {
			"Lead": 
			{"doctype": "Sales Order",
			"field_map": 
			{"name": "lead","customer":"lead_name","delivery_date":"date"},
			"postprocess": update_so
			},
			"Inquiry Item": 
			{"doctype": "Sales Order Item",
			"field_map": {"name":"sales_order_item","parent": "against_inquiry_item","uom": "stock_uom"},
			"postprocess": update_item,
			"add_if_empty": True
			},
			"Sales Team":
			{"doctype": "Sales Team",
			"postprocess": update_sales_team,
			"add_if_empty": True
			}
		}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	# postprocess: fetch shipping address, set missing values
	#doclist.save(ignore_permissions=True)


	return doclist

# Serail No: reserve from SO
@frappe.whitelist()
def update_serial_no_from_so(self,method):
	sales_order = None if (self.status not in ('Draft','To Deliver and Bill','To Bill','To Deliver','Completed')) else self.name
	if sales_order:
			if hasattr(self, 'workflow_state'):
				if self.workflow_state=='Cancelled':
					unreserve_serial_no_from_so_on_cancel(self,method)
				else:
					for item in self.items:
						# check for empty serial no
						if not item.serial_no:
							service_item=frappe.get_list('Item', filters={'item_code': item.item_code}, fields=['is_stock_item', 'is_sales_item', 'is_purchase_item'],)[0]
							if service_item.is_stock_item==0 and service_item.is_sales_item==1 and service_item.is_purchase_item==0:
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
								if serial_no and frappe.db.exists('Serial No', serial_no):
									#match item_code with serial number-->item_code
									sno_item_code=frappe.db.get_value("Serial No", serial_no, "item_code")
									if (cstr(sno_item_code) != cstr(item.item_code)):
										frappe.throw(_("{0} serial number is not valid for {1} item code").format(serial_no,item.item_code))
									#check if there is sales invoice against serial no
									sales_invoice = frappe.db.get_value("Serial No", serial_no, "sales_invoice")
									if sales_invoice and self.name != sales_invoice:
										frappe.throw(_("Serial Number: {0} is already referenced in Sales Invoice: {1}".format(
										serial_no, sales_invoice)))
					
									sno = frappe.get_doc('Serial No', serial_no)
									if sno.reservation_status=='Reserved' and (sno.reserved_by_document).startswith("SO-") :
										if sno.reserved_by_document!=self.name:
											frappe.throw(_("{0} is already reserved by {1} ,for Customer : {2} against Document No : {3}").format(sno.name,sno.sales_partner,sno.for_customer,sno.reserved_by_document))
									if sno.reservation_status=='Sold Out':
										frappe.throw(_("It is sold out"))
									sno.reservation_status='Reserved'
									sno.sales_partner=self.sales_partner
									sno.branch=self.sales_partner_branch
									sno.sales_partner_phone_no=self.sales_partner_phone_no
									sno.for_customer=self.customer
									sno.reserved_by_document = self.name
									sno.db_update()
								else:
									# check for invalid serial number
									frappe.throw(_("{0} is invalid serial number").format(serial_no))

@frappe.whitelist()
def update_serial_no_status_from_sales_invoice(self,method):
	""" update serial no doc with details of Sales Order """
	sales_invoice_doc = self.name
	if sales_invoice_doc:
		if self.update_stock==1:
			for item in self.items:
				# check for empty serial no
				if not item.serial_no:
					service_item=frappe.get_list('Item', filters={'item_code': item.item_code}, fields=['is_stock_item', 'is_sales_item', 'is_purchase_item'],)[0]
					print service_item
					if service_item.is_stock_item==0 and service_item.is_sales_item==1 and service_item.is_purchase_item==0:
						pass
						print 'pass'
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
						print 'serial_no'
						print serial_no
						if serial_no and frappe.db.exists('Serial No', serial_no):
							#match item_code with serial number-->item_code
							sno_item_code=frappe.db.get_value("Serial No", serial_no, "item_code")
							if (cstr(sno_item_code) != cstr(item.item_code)):
								frappe.throw(_("{0} serial number is not valid for {1} item code").format(serial_no,item.item_code))
							#check if there is sales invoice against serial no
							# sales_invoice = frappe.db.get_value("Serial No", serial_no, "sales_invoice")
							# if sales_invoice and self.name != sales_invoice:
							# 	frappe.throw(_("Serial Number: {0} is already referenced in Sales Invoice: {1}".format(
							# 	serial_no, sales_invoice)))
							#check if there is delivery_document_no against serial no
							delivery_document_no = frappe.db.get_value("Serial No", serial_no, "delivery_document_no")
							if delivery_document_no and self.name != delivery_document_no:
								frappe.throw(_("Serial Number: {0} is already referenced in Delivery Document No: {1}".format(
								serial_no, delivery_document_no)))	
							sno = frappe.get_doc('Serial No', serial_no)
							# if sno.reservation_status=='Reserved' and sno.reserved_by_document!="" :
							# 	frappe.throw(_("{0} is already reserved by {1} ,for Customer : {2} against Document No : {3}").format(sno.name,sno.sales_partner,sno.for_customer,sno.reserved_by_document))
							if sno.reservation_status=='Sold Out':
								frappe.throw(_("It is sold out"))					
							sno.reservation_status='Sold Out'
							sno.sales_partner=self.sales_partner
							#sno.branch=self.sales_partner_branch
							#sno.sales_partner_phone_no=self.sales_partner_phone
							sno.for_customer=self.customer
							# sno.reserved_by_document = ''
							sno.db_update()
						else:
							# check for invalid serial number
							frappe.throw(_("{0} is invalid serial number").format(serial_no))


@frappe.whitelist()
def update_serial_no_status_from_delivery_note(self,method):
	""" update serial no doc with details of Sales Order """
	delivery_note = self.name
	if delivery_note:
		for item in self.items:
			# check for empty serial no
			if not item.serial_no:
				frappe.throw(_("Row {0}: {1} Serial numbers required for Item {2}. You have provided None.".format(
					item.idx, item.qty, item.item_code)))
			# match item qty and serial no count
			serial_nos = item.serial_no
			si_serial_nos = set(get_serial_nos(serial_nos))
			if item.serial_no and cint(item.qty) != len(si_serial_nos):
				frappe.throw(_("Row {0}: {1} Serial numbers required for Item {2}. You have provided {3}.".format(
					item.idx, item.qty, item.item_code, len(si_serial_nos))))

			for serial_no in item.serial_no.split("\n"):
				if serial_no and frappe.db.exists('Serial No', serial_no):
					#match item_code with serial number-->item_code
					sno_item_code=frappe.db.get_value("Serial No", serial_no, "item_code")
					if (cstr(sno_item_code) != cstr(item.item_code)):
						frappe.throw(_("{0} serial number is not valid for {1} item code").format(serial_no,item.item_code))
					#check if there is sales invoice against serial no
					# sales_invoice = frappe.db.get_value("Serial No", serial_no, "sales_invoice")
					# if sales_invoice and self.name != sales_invoice:
					# 	frappe.throw(_("Serial Number: {0} is already referenced in Sales Invoice: {1}".format(
					# 	serial_no, sales_invoice)))
					#check if there is delivery_document_no against serial no
					delivery_document_no = frappe.db.get_value("Serial No", serial_no, "delivery_document_no")
					if delivery_document_no and self.name != delivery_document_no:
						frappe.throw(_("Serial Number: {0} is already referenced in Delivery Document No: {1}".format(
						serial_no, delivery_document_no)))	
					sno = frappe.get_doc('Serial No', serial_no)
					# if sno.reservation_status=='Reserved' and sno.reserved_by_document!="" :
					# 	frappe.throw(_("{0} is already reserved by {1} ,for Customer : {2} against Document No : {3}").format(sno.name,sno.sales_partner,sno.for_customer,sno.reserved_by_document))
					if sno.reservation_status=='Sold Out':
						frappe.throw(_("It is sold out"))					
					sno.reservation_status='Sold Out'
					sno.sales_partner=self.sales_partner
					#sno.branch=self.sales_partner_branch
					#sno.sales_partner_phone_no=self.sales_partner_phone
					sno.for_customer=self.customer
					# sno.reserved_by_document = ''
					sno.db_update()
				else:
					# check for invalid serial number
					frappe.throw(_("{0} is invalid serial number").format(serial_no))

@frappe.whitelist()
def unreserve_serial_no_from_so_on_cancel(self,method):
	sales_order = self.name
	if sales_order:
		for item in self.items:
			# check for empty serial no
			if not item.serial_no:
				pass
			else:
				for serial_no in item.serial_no.split("\n"):
					if serial_no and frappe.db.exists('Serial No', serial_no):
						#match item_code with serial number-->item_code
						sno_item_code=frappe.db.get_value("Serial No", serial_no, "item_code")
						if (cstr(sno_item_code) != cstr(item.item_code)):
							#frappe.throw(_("{0} serial number is not valid for {1} item code").format(serial_no,item.item_code))
							pass
						#check if there is sales invoice against serial no
						sales_invoice = frappe.db.get_value("Serial No", serial_no, "sales_invoice")
						if sales_invoice and self.name != sales_invoice:
							pass
						sno = frappe.get_doc('Serial No', serial_no)
						if (sno.reserved_by_document == self.name):
							sno.reservation_status='Available'
							sno.sales_partner=None
							sno.sales_partner_phone_no=None
							sno.branch=None
							sno.for_customer=None
							sno.reserved_by_document = None
							sno.db_update()
					else:
						# check for invalid serial number
						# frappe.throw(_("{0} is invalid serial number").format(serial_no))
						pass
@frappe.whitelist()
def auto_unreserve_serial_no_from_quotation_on_expiry():
	expired_quotation_list=frappe.get_all('Quotation', filters = [["valid_till", ">", datetime.date(1900, 1, 1)],["valid_till", "<", getdate(nowdate())]], fields=['name'])
	
	print expired_quotation_list
	if expired_quotation_list:
		for quotation_name in expired_quotation_list:
			quotation = frappe.get_doc('Quotation', quotation_name)
			print quotation
			if quotation:
				unreserve_serial_no_from_quotation(self=quotation,method=None,auto_run=1)

@frappe.whitelist()
def unreserve_serial_no_from_quotation(self,method,auto_run=0):
	""" update serial no doc with details of Sales Order """
	print ('unreserve_serial_no_from_quotation')
	print cint(self.reserve_above_items)
	print  self.status
	print self.docstatus
	if auto_run==1:
		self.reserve_above_items=0
	quotation = None if (cint(self.reserve_above_items)==1 or self.status in ('Lost','Ordered') or self.docstatus ==0) else self.name
	if quotation:
		print 'inside unreserve_serial_no_from_quotation'
		for item in self.items:
			# check for empty serial no
			if not item.serial_no:
				pass
			else:
				# match item qty and serial no count
				for serial_no in item.serial_no.split("\n"):
					print serial_no
					if serial_no and frappe.db.exists('Serial No', serial_no):
						#match item_code with serial number-->item_code
						sno_item_code=frappe.db.get_value("Serial No", serial_no, "item_code")
						if (cstr(sno_item_code) != cstr(item.item_code)):
							# frappe.throw(_("{0} serial number is not valid for {1} item code").format(serial_no,item.item_code))
							pass
						#check if there is sales invoice against serial no
						sales_invoice = frappe.db.get_value("Serial No", serial_no, "sales_invoice")
						if sales_invoice and self.name != sales_invoice:
							pass
						sno = frappe.get_doc('Serial No', serial_no)
						if (sno.reserved_by_document == self.name):
							sno.reservation_status='Available'
							sno.sales_partner=None
							sno.sales_partner_phone_no=None
							sno.branch=None
							sno.for_customer=None
							sno.reserved_by_document = None
							sno.db_update()
							self.db_set('reserve_above_items',0)
					else:
						# check for invalid serial number
						# frappe.throw(_("{0} is invalid serial number").format(serial_no))
						pass

@frappe.whitelist()
def update_serial_no_from_quotation(self,method):
	""" update serial no doc with details of Sales Order """
	quotation = None if (cint(self.reserve_above_items)==0 or self.status in ('Lost','Cancelled') ) else self.name
	if quotation:
		for item in self.items:
			# check for empty serial no
			if not item.serial_no:
				frappe.throw(_("Row {0}: {1} Serial numbers required for Item {2}. You have provided None.".format(
					item.idx, item.qty, item.item_code)))
			# match item qty and serial no count
			serial_nos = item.serial_no
			si_serial_nos = set(get_serial_nos(serial_nos))
			if item.serial_no and cint(item.qty) != len(si_serial_nos):
				frappe.throw(_("Row {0}: {1} Serial numbers required for Item {2}. You have provided {3}.".format(
					item.idx, item.qty, item.item_code, len(si_serial_nos))))

			for serial_no in item.serial_no.split("\n"):
				if serial_no and frappe.db.exists('Serial No', serial_no):
					#match item_code with serial number-->item_code
					sno_item_code=frappe.db.get_value("Serial No", serial_no, "item_code")
					if (cstr(sno_item_code) != cstr(item.item_code)):
						frappe.throw(_("{0} serial number is not valid for {1} item code").format(serial_no,item.item_code))
					#check if there is sales invoice against serial no
					sales_invoice = frappe.db.get_value("Serial No", serial_no, "sales_invoice")
					if sales_invoice and self.name != sales_invoice:
						frappe.throw(_("Serial Number: {0} is already referenced in Sales Invoice: {1}".format(
						serial_no, sales_invoice)))
	
					sno = frappe.get_doc('Serial No', serial_no)
					if sno.reservation_status=='Reserved' and sno.reserved_by_document!="" :
						frappe.throw(_("{0} is already reserved by {1} ,for Customer : {2} against Document No : {3}").format(sno.name,sno.sales_partner,sno.for_customer,sno.reserved_by_document))
					if sno.reservation_status=='Sold Out':
						frappe.throw(_("It is sold out"))
					sno.reservation_status='Reserved'
					sno.sales_partner=self.sales_partner
					sno.branch=self.sales_partner_branch
					sno.sales_partner_phone_no=self.sales_partner_phone
					sno.for_customer=self.customer
					sno.reserved_by_document = self.name
					sno.db_update()
				else:
					# check for invalid serial number
					frappe.throw(_("{0} is invalid serial number").format(serial_no))
# search related

@frappe.whitelist()
def get_color_name(search_template,search_category,search_model):
	return frappe.db.sql("""select distinct(att.attribute_value)
from `tabItem` as item 
inner join 
`tabItem Variant Attribute` as att
on item.name=att.parent 
where att.attribute ='Color'
and item.name IN
(select item.name
from `tabItem` as item 
inner join 
`tabItem Variant Attribute` as att
on item.name=att.parent 
where att.attribute_value =%s
and att.attribute ='Model'
and item.name IN
(select item.name
from `tabItem` as item 
inner join 
`tabItem Variant Attribute` as att
on item.name=att.parent 
where
item.variant_based_on='Item Attribute'
and item.has_variants=0
and item.docstatus < 2
and att.attribute_value =%s
and att.attribute ='Category'
and item.variant_of=(
select name from `tabItem` 
where item_name=%s)
)
)
order by att.attribute_value
""",(search_model,search_category,search_template),as_list=True)



@frappe.whitelist()
def get_model_name(search_template,search_category):
	return frappe.db.sql("""select distinct(att.attribute_value)
from `tabItem` as item 
inner join 
`tabItem Variant Attribute` as att
on item.name=att.parent 
and att.attribute='Model'
where item.name IN
(select item.name
from `tabItem` as item 
inner join 
`tabItem Variant Attribute` as att
on item.name=att.parent 
where
item.variant_based_on='Item Attribute'
and item.has_variants=0
and item.docstatus < 2
and att.attribute_value = %s
and item.variant_of=(
select name from `tabItem` 
where item_name=%s)) order by att.attribute_value desc""",(search_category,search_template),as_list=True)

@frappe.whitelist()
def get_category_name(search_template):
	return frappe.db.sql("""select distinct(att.attribute_value)
from `tabItem` as item 
inner join 
`tabItem Variant Attribute` as att
on item.name=att.parent 
where
item.variant_based_on='Item Attribute'
and item.has_variants=0
and item.docstatus < 2
and att.attribute='Category'
and item.variant_of IN (
select name from `tabItem` 
where item_name=%s) order by att.attribute_value """ ,search_template,as_list=True)

@frappe.whitelist()
def get_item_group():
	item_group=frappe.db.sql("""select name 
	from `tabItem Group` where is_group=0 and docstatus < 2""",as_list=True) 
	return item_group if item_group else None


@frappe.whitelist()
def get_template_name(search_group):
	cond = "1=1"
	item_groups = []
	if search_group:
		item_groups.extend([search_group.name for search_group in get_child_nodes('Item Group', search_group)])
		cond = "item_group in (%s)"%(', '.join(['%s']*len(item_groups)))

		print 'get_template_name'
		print item_groups
	template_name=frappe.db.sql("""select distinct(item_name) 
	from `tabItem` where has_variants=1 and docstatus < 2 and {cond}
		""".format(cond=cond), tuple(item_groups), as_list=1)
	return template_name if template_name else None

def get_child_nodes(group_type, root):
	print (group_type, root)
	lft, rgt = frappe.db.get_value(group_type, root, ["lft", "rgt"])
	return frappe.db.sql(""" Select name, lft, rgt from `tab{tab}` where
			lft >= {lft} and rgt <= {rgt} order by lft""".format(tab=group_type, lft=lft, rgt=rgt), as_dict=1)

@frappe.whitelist()
def get_search_item_name(search_template,search_category,search_model,search_color):
	get_search_item_name=frappe.db.sql("""select item.name
from `tabItem` as item 
inner join 
`tabItem Variant Attribute` as att
on item.name=att.parent 
where att.attribute_value =%s
and att.attribute ='Color'
and item.name IN
(select item.name
from `tabItem` as item 
inner join 
`tabItem Variant Attribute` as att
on item.name=att.parent 
where att.attribute_value =%s
and att.attribute ='Model'
and item.name IN
(select item.name
from `tabItem` as item 
inner join 
`tabItem Variant Attribute` as att
on item.name=att.parent 
where
item.variant_based_on='Item Attribute'
and item.has_variants=0
and item.docstatus < 2
and att.attribute_value =%s
and att.attribute ='Category'
and item.variant_of=(
select name from `tabItem` 
where item_name=%s
)
)
)
""",(search_color,search_model,search_category,search_template),as_list=True)
	return get_search_item_name[0] if get_search_item_name else None