from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import (cstr, validate_email_add, cint,flt, comma_and, has_gravatar, now, getdate, nowdate)
from frappe.model.mapper import get_mapped_doc
import frappe, json
from erpnext.controllers.selling_controller import SellingController
from erpnext import get_default_company
from frappe.contacts.address_and_contact import load_address_and_contact
from erpnext.accounts.party import set_taxes
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.party import get_party_account_currency
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
import datetime
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.contacts.doctype.address.address import get_company_address
from erpnext.selling.doctype.quotation.quotation import _make_customer
from frappe.utils.xlsxutils import handle_html
from frappe import scrub
import ast
from frappe.utils import get_link_to_form



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
				target_doc.party_name=target_doc.customer
				target_doc.sub_customer=get_customernamingseries(source_doc.customer)
				
			else:
				# target_doc.customer=source_doc.customer
				target_doc.customer=get_customernamingseries(source_doc.customer)
				target_doc.party_name=target_doc.customer
		else:
			if source_doc.organization_lead==0 and source_doc.transaction_type=='Cash':
				# target_doc.customer=source_doc.lead_name
				target_doc.customer=get_customernamingseries(source_doc.lead_name)
				target_doc.party_name=target_doc.customer
			elif source_doc.organization_lead==1 and source_doc.transaction_type=='Cash':
				# target_doc.customer=source_doc.company_name
				target_doc.customer=get_customernamingseries(source_doc.company_name)
				target_doc.party_name=target_doc.customer
			elif source_doc.organization_lead==0 and source_doc.transaction_type=='Bank Funded':
				# target_doc.customer=source_doc.bank_name
				# target_doc.sub_customer=source_doc.lead_name
				target_doc.customer=get_customernamingseries(source_doc.bank_name)
				target_doc.party_name=target_doc.customer
				target_doc.sub_customer=get_customernamingseries(source_doc.lead_name)
			elif source_doc.organization_lead==1 and source_doc.transaction_type=='Bank Funded':
				# target_doc.customer=source_doc.bank_name
				# target_doc.sub_customer=source_doc.company_name
				target_doc.customer=get_customernamingseries(source_doc.bank_name)
				target_doc.party_name=target_doc.customer
				target_doc.sub_customer=get_customernamingseries(source_doc.company_name)
	def update_sales_team(obj, target, source_parent):
		target.sales_person = source_parent.sales_person
		target.allocated_percentage= 100
		target.car_sale_incentives=frappe.get_value('Sales Person', source_parent.sales_person, 'commission_per_car')
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
	incentives=frappe.get_value('Sales Person',sales_person, 'commission_per_car')
	return incentives if incentives else None
# Lead to Customer
@frappe.whitelist()
def make_customer_from_lead(doc):
	doc=frappe._dict(json.loads(doc))
	#check existing contact
	contact_name = frappe.db.get_value('Contact',{'mobile_no': doc.mobile_no}, 'name')
	if contact_name:
		#existing contact, i.e. duplicate
		pass
	else:
		#new contact
		if doc.organization_lead==1:
			customer_type='Company'
			customer_name=doc.company_name
			customer = frappe.new_doc("Customer")
			customer.is_internal_customer=0
			customer.represents_company=''
			customer.customer_type=customer_type
			customer.lead_name=doc.name
			customer.car_customer_source=doc.car_customer_source
			customer.customer_group=doc.customer_group
			customer.territory=doc.territory
			customer.customer_name=customer_name
			customer.national_id_cf=doc.national_id_cf
			# customer.default_sales_partner=doc.sales_person
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
			customer.is_internal_customer=0
			customer.represents_company=''
			customer.customer_type=customer_type
			customer.lead_name=doc.name
			customer.car_customer_source=doc.car_customer_source
			customer.customer_group=doc.customer_group
			customer.territory=doc.territory
			customer.customer_name=customer_name
			customer.national_id_cf=doc.national_id_cf
			# customer.default_sales_partner=doc.sales_person
			customer.save(ignore_permissions=True)
			primary_contact=get_customer_primary_contact(customer.name)
			customer.customer_primary_contact=primary_contact['name']
			customer.mobile_no=primary_contact['mobile_no']
			customer.email_id=primary_contact['email_id']
			customer.save(ignore_permissions=True)
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
		select cust.customer_group,
			cust.customer_type,
			cust.customer_name,
			cust.name,
			cust.car_customer_source,
			cust.territory,
			RTRIM(concat(cont.first_name,' ',ifnull(cont.last_name,'')))as person_name,
			cont.email_id,
			cont.mobile_no,
			cust.national_id_cf
		from `tabCustomer` cust 
		inner join `tabContact` cont
		on cust.customer_primary_contact=cont.name
		where 
		cont.mobile_no=%(mobile_no)s
		""", {
			'mobile_no': mobile_no
		},as_dict=True)
	if existing_customer:
		frappe.msgprint(_("Existing Contact").format(existing_customer[0]['customer_name']),indicator='green', alert=1)
	else:
		frappe.msgprint(_("New Contact"),indicator='red', alert=1)

	return existing_customer[0] if existing_customer else None

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_bank_name(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name,customer_name from `tabCustomer`
where 
docstatus<2 
and bank_customer=1""",as_list=True)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_warranty_card_item(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name from `tabItem`
where 
docstatus<2 
and item_group=1""",as_list=True)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_non_bank_customer(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name from `tabCustomer`
where 
docstatus<2 
and bank_customer=0""",as_list=True)




@frappe.whitelist()
def is_customer_a_bank(customer=None):
	if customer:
		return frappe.db.sql("""select bank_customer from `tabCustomer`
where 
docstatus<2 
and name=%s""",customer,as_list=True)[0][0]
	else:
		return None


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
def get_waranty_card_items_for_PI(supplier,posting_date):
	warranty_item = frappe.db.sql("""select 
-- group_concat('card::',warranty_card_number,',serial--',serial_no SEPARATOR '|') as description,
group_concat(warranty_card_number SEPARATOR '|') as description,
count(warranty_card_number) as qty,
warranty_card_item
from `tabWarranty Card Issued`
where purchase_invoice is null
and sales_invoice is not null
and docstatus=1
and supplier = %s
and issued_date <= %s
group by warranty_card_item""",(supplier,posting_date), as_dict=1)
	return warranty_item if warranty_item else None


@frappe.whitelist()
def car_transferred_items_for_PI(supplier,posting_date):
	transferred_item = frappe.db.sql("""select  
group_concat(SED.serial_no SEPARATOR '|') as description,
(select default_item_for_car_transfer from `tabCompany`
where name = (select value from `tabSingles` where doctype='Global Defaults' and field='default_company'))
as default_item_for_car_transfer,
sum(SED.qty) as qty,
SE.transfer_cost as transfer_cost,
SED.item_name,
SE.name as stock_entry
from `tabStock Entry` SE
inner join `tabStock Entry Detail` SED
on SE.name=SED.parent
where 
SE.transfer_purchase_invoice is null
and SE.docstatus=1
and SE.transferred_by_supplier = %s
and SE.posting_date <= %s
group by SE.name,SED.item_name
order by SE.name""",(supplier,posting_date), as_dict=1)
	return transferred_item if transferred_item else None


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
	sales_person= frappe.db.sql("""select name,branch,commission_per_car,source,customer_group from `tabSales Person`
where
is_group=0
and user_id=%(user_email)s
	""",{
			'user_email': user_email
		},as_list=True)
	return sales_person if sales_person else None

@frappe.whitelist()
def get_sales_person_and_branch_and_costcenter(user_email):
	sales_person= frappe.db.sql("""select sp.name,sp.branch, sp.commission_per_car, b.cost_center 
from `tabSales Person` as sp
inner join `tabBranch` as b
on sp.branch=b.name
where
sp.is_group=0
and sp.user_id=%(user_email)s
	""",{
			'user_email': user_email
		},as_list=True)
	return sales_person if sales_person else None


@frappe.whitelist()
def get_branch_and_costcenter(name):
	sales_person= frappe.db.sql("""select sp.branch, sp.commission_per_car, b.cost_center 
from `tabSales Person` as sp
inner join `tabBranch` as b
on sp.branch=b.name
where
sp.is_group=0
and sp.name=%(name)s
	""",{
			'name': name
		},as_list=True)
	return sales_person if sales_person else None


@frappe.whitelist()
def update_warranty_card_issued(self,method):
# It is called both on submit and cancel of PI
	company = get_default_company()
	default_item_for_car_transfer=frappe.get_value('Company', company, 'default_item_for_car_transfer')
	if self.docstatus==1:
	# submitted
		for item in self.items:
			# item.description of PI items stores serial no.
			# based on serial no update SE with PI reference
			if item.description:
				item_group=frappe.get_value('Item', item.item_code, 'item_group')
				if item.item_code==default_item_for_car_transfer:
					description=item.description
					serial_no_list=handle_html(description.split("|"))
					x=ast.literal_eval(serial_no_list)
					serial_no_list = [n.strip() for n in x]					
					for serial_no in serial_no_list:
						doc = frappe.get_doc('Stock Entry', item.stock_entry_for_car_transfer)
						doc.transfer_purchase_invoice=self.name
						doc.save(ignore_permissions=True)
						frappe.msgprint(_('Stock Entry {0} is updated with purchase invoice reference {1}').format(
								frappe.bold(get_link_to_form('Stock Entry', doc.name)),frappe.bold(self.name)))              
	elif self.docstatus==2:
	# cancelled
		# delink PI reference from 'Warranty Card Issued
		if self.warranty_card_issued:
			doc = frappe.get_doc('Warranty Card Issued', self.warranty_card_issued)
			doc.purchase_invoice=None
			doc.save(ignore_permissions=True)
			frappe.msgprint(_('Warranty Card Issued {0} is updated. Purchase invoice {1} reference is removed').format(
					frappe.bold(get_link_to_form('Warranty Card Issued', doc.name)),frappe.bold(self.name))) 			

		for item in self.items:
			# item.description of PI items stores serial no.
			if item.description:
				if item.item_code==default_item_for_car_transfer:
				# based on serial no update SE to remove  PI reference
					description=item.description
					serial_no_list=handle_html(description.split("|"))
					x=ast.literal_eval(serial_no_list)
					serial_no_list = [n.strip() for n in x]					
					for serial_no in serial_no_list:
						doc = frappe.get_doc('Stock Entry', item.stock_entry_for_car_transfer)
						doc.transfer_purchase_invoice=None
						doc.save(ignore_permissions=True) 
						frappe.msgprint(_('Stock Entry {0} is updated. Purchase invoice {1} reference is removed').format(
								frappe.bold(get_link_to_form('Stock Entry', doc.name)),frappe.bold(self.name))) 						

# Update status : Lead to Sales Order
@frappe.whitelist()
def update_lead_status_from_sales_order(self,method):
	if self.linked_lead:
		name_of_linked_lead=self.linked_lead
		lead=frappe.get_doc("Lead",name_of_linked_lead)

		if lead.linked_sales_order== None or lead.linked_sales_order=='':
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
	if customernamingseries==None or customernamingseries==[] :
		customernamingseries=customer_name
		return customernamingseries
	else:
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
		target.car_sale_incentives=frappe.get_value('Sales Person', source_parent.sales_person, 'commission_per_car')

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

@frappe.whitelist()
def custom_logid_on_validate_of_so(self,method):
	validate_serial_no_for_eligible_service_items(self,method)
	update_serial_no_from_so(self,method)

def validate_serial_no_for_eligible_service_items(self,method):
	for item in self.items:
		is_serial_no_mandatory_in_sales_cf = frappe.db.get_value('Item', item.item_code, 'is_serial_no_mandatory_in_sales_cf')
		if is_serial_no_mandatory_in_sales_cf==1:
			if not item.serial_no_for_service_item_cf:
				frappe.throw(_("Row {0}: {1} Item  requires 'Serial No for Service Item' value. You have provided None.".format(
					frappe.bold(item.idx),frappe.bold(item.item_code))))				
				


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
									if sno.reservation_status=='Reserved' and frappe.db.exists("Sales Order", sno.reserved_by_document):
										if sno.reserved_by_document!=self.name:
											frappe.throw(_("{0} is already reserved by {1} ,for Customer : {2} against Document No : {3}").format(sno.name,sno.sales_person,sno.for_customer,sno.reserved_by_document))
									if sno.reservation_status=='Sold Out':
										frappe.throw(_("It is sold out"))
									if sno.reservation_status=='Available' or sno.reservation_status=='Showroom Car':
										sno.reservation_status='Reserved'
										if self.sales_person:
											sno.sales_person=self.sales_person
											sno.sales_person_phone_no=frappe.get_value('Sales Person', sno.sales_person, 'phone_no')
											sno.branch=self.sales_person_branch
										sno.for_customer=self.customer
										sno.reserved_by_document = self.name
										sno.save(ignore_permissions=True)
								else:
									# check for invalid serial number
									frappe.throw(_("{0} is invalid serial number").format(serial_no))

@frappe.whitelist()
def update_serial_no_status_from_sales_invoice(self,method):
	""" update serial no doc with details of Sales Order """
	sales_invoice_doc = self.name
	if sales_invoice_doc:
		if self.is_return == 1 and self.update_stock == 1:
			unreserve_serial_no_from_sales_invoice(self,method)
		elif self.is_return== 0 and self.update_stock == 1 :
			for item in self.items:
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
							# 	frappe.throw(_("{0} is already reserved by {1} ,for Customer : {2} against Document No : {3}").format(sno.name,sno.sales_person,sno.for_customer,sno.reserved_by_document))
							if sno.reservation_status=='Sold Out':
								frappe.throw(_("It is sold out"))
							sno.reservation_status='Sold Out'
							if self.sales_person:
								sno.sales_person=self.sales_person
								sno.sales_person_phone_no=frappe.get_value('Sales Person', sno.sales_person, 'phone_no')
								sno.branch=self.sales_person_branch                       
							sno.for_customer=self.customer
							# sno.reserved_by_document = ''
							sno.save(ignore_permissions=True)
						elif len(serial_no)==0:
							pass
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
			if item.serial_no and abs(cint(item.qty)) != len(si_serial_nos):
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
					# 	frappe.throw(_("{0} is already reserved by {1} ,for Customer : {2} against Document No : {3}").format(sno.name,sno.sales_person,sno.for_customer,sno.reserved_by_document))
					if sno.reservation_status=='Sold Out':
						frappe.throw(_("It is sold out"))					
					sno.reservation_status='Sold Out'
					if self.sales_person:
						sno.sales_person=self.sales_person
						sno.sales_person_phone_no=frappe.get_value('Sales Person', sno.sales_person, 'phone_no')
						sno.branch=self.sales_person_branch
					sno.for_customer=self.customer
					# sno.reserved_by_document = ''
					sno.save(ignore_permissions=True)
				else:
					# check for invalid serial number
					frappe.throw(_("{0} is invalid serial number").format(serial_no))

@frappe.whitelist()
def calculate_sales_person_total_commission(self,method):
	sales_invoice = self.name
	if sales_invoice:
		if self.sales_person:
			commission_per_car=self.commission_per_car
			sales_person_total_commission=0
			for item in self.items:
				is_stock_item=frappe.db.get_value("Item", item.item_code, "is_stock_item")
				is_sales_item=frappe.db.get_value("Item", item.item_code, "is_sales_item")
				has_serial_no=frappe.db.get_value("Item", item.item_code, "has_serial_no")
				if is_stock_item==1 and is_sales_item==1 and has_serial_no==1:
					sales_person_total_commission+=item.qty*commission_per_car
			self.sales_person_total_commission=sales_person_total_commission

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
						if ((self.docstatus == 0 or self.docstatus == 1 or self.docstatus == 2) and sno.reserved_by_document == self.name and sno.reservation_status=='Reserved'):
							sno.reservation_status='Available'
							sno.sales_person=None
							sno.sales_person_phone_no=None
							sno.branch=None
							sno.for_customer=None
							sno.reserved_by_document = None
							sno.save(ignore_permissions=True)
					else:
						# check for invalid serial number
						# frappe.throw(_("{0} is invalid serial number").format(serial_no))
						pass



@frappe.whitelist()
def unlink_so_from_other_doctype(self,method):
	frappe.db.sql("""update `tabSales Order` set sub_customer='',linked_lead='',sales_person='',sales_person_branch='' where name=%s""",self.name)
	frappe.db.sql("""update `tabLead` set status='Sales Inquiry',linked_sales_order='' where name=%s""",self.linked_lead)

@frappe.whitelist()
def unreserve_serial_no_from_sales_invoice(self,method):
	sales_invoice_doc = self.name
	if sales_invoice_doc and self.update_stock==1:
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
						sno = frappe.get_doc('Serial No', serial_no)
						if ((self.docstatus == 1 or self.docstatus == 2) and (sno.reserved_by_document == self.name or sno.reserved_by_document == self.return_against)and sno.reservation_status=='Sold Out'):
							sno.reservation_status='Available'
							sno.sales_person=None
							sno.sales_person_phone_no=None
							sno.branch=None
							sno.for_customer=None
							sno.reserved_by_document = None
							sno.save(ignore_permissions=True)
					else:
						# check for invalid serial number
						# frappe.throw(_("{0} is invalid serial number").format(serial_no))
						pass

@frappe.whitelist()
def unreserve_serial_no_from_delivery_note(self,method):
	delivery_note = self.name
	if delivery_note and self.docstatus==1:
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
						sno = frappe.get_doc('Serial No', serial_no)
						if (sno.reserved_by_document == self.name and sno.reservation_status=='Sold Out'):
							sno.reservation_status='Available'
							sno.sales_person=None
							sno.sales_person_phone_no=None
							sno.branch=None
							sno.for_customer=None
							sno.reserved_by_document = None
							sno.save(ignore_permissions=True)
					else:
						# check for invalid serial number
						# frappe.throw(_("{0} is invalid serial number").format(serial_no))
						pass




@frappe.whitelist()
def auto_unreserve_serial_no_from_quotation_on_expiry():
	expired_quotation_list=frappe.get_all('Quotation', filters = [["valid_till", ">", datetime.date(1900, 1, 1)],["valid_till", "<", getdate(nowdate())]], fields=['name'])
	
	if expired_quotation_list:
		for quotation_name in expired_quotation_list:
			quotation = frappe.get_doc('Quotation', quotation_name)
			if quotation:
				unreserve_serial_no_from_quotation(self=quotation,method=None,auto_run=1)

@frappe.whitelist()
def auto_close_lead_on_end_date():
	from frappe.utils import nowdate, format_datetime
	todays_date=format_datetime(str(nowdate()+' 00:00:00'))
	expired_lead_list=frappe.get_all('Lead', filters = [["ends_on", "<=", todays_date]], fields=['name'])
	if expired_lead_list:
		for lead_name in expired_lead_list:
			lead = frappe.get_doc('Lead', lead_name.name)
			if lead and lead.ends_on != None:
				lead.status='Do Not Contact'
				lead.add_comment("Comment",text="Lead closed after 90 days, by auto system")
				lead.save(ignore_permissions=True)
				frappe.db.commit()

@frappe.whitelist()
def unreserve_serial_no_from_quotation(self,method,auto_run=0):
	""" update serial no doc with details of Sales Order """
	# if auto_run==1:
	#     self.reserve_above_items=0
	quotation = None if (cint(self.reserve_above_items)==0 or self.status in ('Lost','Ordered') or self.docstatus ==0) else self.name
	if quotation and (self.docstatus ==1 or self.docstatus ==2 ):
		for item in self.items:
			# check for empty serial no
			if not item.serial_no:
				pass
			else:
				# match item qty and serial no count
				for serial_no in item.serial_no.split("\n"):
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
						if (sno.reserved_by_document == self.name and sno.reservation_status=='Reserved'):
							sno.reservation_status='Available'
							sno.sales_person=None
							sno.sales_person_phone_no=None
							sno.branch=None
							sno.for_customer=None
							sno.reserved_by_document = None
							sno.save(ignore_permissions=True)
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
						frappe.throw(_("{0} is already reserved by {1} ,for Customer : {2} against Document No : {3}").format(sno.name,sno.sales_person,sno.for_customer,sno.reserved_by_document))
					if sno.reservation_status=='Sold Out':
						frappe.throw(_("It is sold out"))
					if sno.reservation_status=='Available':
						sno.reservation_status='Reserved'
						if self.sales_person:
							sno.sales_person=self.sales_person
							sno.sales_person_phone_no=frappe.get_value('Sales Person', sno.sales_person, 'phone_no')
							sno.branch=self.sales_person_branch
						sno.for_customer=self.party_name
						sno.reserved_by_document = self.name
						sno.save(ignore_permissions=True)
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

	template_name=frappe.db.sql("""select distinct(item_name) 
	from `tabItem` where has_variants=1 and docstatus < 2 and {cond}
		""".format(cond=cond), tuple(item_groups), as_list=1)
	return template_name if template_name else None

def get_child_nodes(group_type, root):
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

@frappe.whitelist()
def get_registration_plate_no(serial_nos=None):
	if not serial_nos:
		return
	from frappe.utils import cstr
	where_clause = " where name in ({})".format(",".join(
		["'%s'" % d for d in serial_nos.split("\n")]))
	nos = frappe.db.sql("""
		SELECT name, ifnull(registration_plate_no,'NOT AVAILABLE') registration_plate_no
		FROM `tabSerial No` {}
		group by name
	""".format(where_clause))
	data = []
	if nos:
		for d in serial_nos.split("\n"):
			for n in nos:
				if n[0]==d: data.append(n[1]) 
	return "\n".join(data)


@frappe.whitelist()
def get_distinct_attributes_values():
	return frappe.db.sql("""select distinct attribute as attribute ,attribute_value as attribute_value from `tabItem Variant Attribute`
where attribute_value is not null
group by attribute,attribute_value""",as_dict=True)

@frappe.whitelist()
def car_make_delivery_note(source_name, target_doc=None):
	
	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")

		# set company address
		target.update(get_company_address(target.company))
		if target.company_address:
			target.update(get_fetch_values("Delivery Note", 'company_address', target.company_address))

	def update_item(source, target, source_parent):
		target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.base_rate)
		target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
		target.qty = flt(source.qty) - flt(source.delivered_qty)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)

		if item:
			target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center") \
				or item.get("selling_cost_center") \
				or item_group.get("selling_cost_center")

	target_doc = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Delivery Note",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Sales Order Item": {
			"doctype": "Delivery Note Item",
			"field_map": {
				"rate": "rate",
				"serial_no":"serial_no",
				"name": "so_detail",
				"parent": "against_sales_order",
			},
			"postprocess": update_item,
			"condition": lambda doc: abs(doc.delivered_qty) < abs(doc.qty) and doc.delivered_by_supplier!=1
		},
		"Sales Taxes and Charges": {
			"doctype": "Sales Taxes and Charges",
			"add_if_empty": True
		},
		"Sales Team": {
			"doctype": "Sales Team",
			"add_if_empty": True
		}
	}, target_doc, set_missing_values)

	return target_doc


@frappe.whitelist()
def make_sales_order_from_quotation(source_name, target_doc=None):
	quotation = frappe.db.get_value("Quotation", source_name, ["transaction_date", "valid_till"], as_dict = 1)
	if quotation.valid_till and (quotation.valid_till < quotation.transaction_date or quotation.valid_till < getdate(nowdate())):
		frappe.throw(_("Validity period of this quotation has ended."))
	return _make_sales_order_from_quotation(source_name, target_doc)

def _make_sales_order_from_quotation(source_name, target_doc=None, ignore_permissions=False):
	customer = _make_customer(source_name, ignore_permissions)

	def set_missing_values(source, target):
		if customer:
			target.customer = customer.name
			target.customer_name = customer.customer_name
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		if source_parent.reserve_above_items==1:
			sno_warehouse=frappe.db.get_value("Serial No", obj.serial_no, "warehouse")
			target.warehouse=sno_warehouse
		target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)

	doclist = get_mapped_doc("Quotation", source_name, {
			"Quotation": {
				"doctype": "Sales Order",
				"validation": {
					"docstatus": ["=", 1]
				}
			},
			"Quotation Item": {
				"doctype": "Sales Order Item",
				"field_map": {
					"parent": "prevdoc_docname"
				},
				"postprocess": update_item
			},
			"Sales Taxes and Charges": {
				"doctype": "Sales Taxes and Charges",
				"add_if_empty": True
			},
			"Sales Team": {
				"doctype": "Sales Team",
				"add_if_empty": True
			},
			"Payment Schedule": {
				"doctype": "Payment Schedule",
				"add_if_empty": True
			}
		}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	# postprocess: fetch shipping address, set missing values

	return doclist

@frappe.whitelist()
def make_purchase_receipt_from_custom_card_entry(source_name, target_doc=None):

	def set_missing_values(source, target):
		if len(target.get("items")) == 0:
			frappe.throw(_("No Items found"))

		doc = frappe.get_doc(target)
		doc.ignore_pricing_rule = 1
		doc.run_method("onload")
		doc.run_method("set_missing_values")
		doc.run_method("calculate_taxes_and_totals")
	 
	def update_item(obj, target, source_parent):
		target.received_qty=flt(obj.qty)
		target.qty = flt(obj.qty)

	doc = get_mapped_doc("Custom Card Entry", source_name,	{
		"Custom Card Entry": {
			"doctype": "Purchase Receipt",
			"field_map": {
				"supplier":"supplier",
			},
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"Custom Card Entry Item": {
			"doctype": "Purchase Receipt Item",
			"field_map": {
				"name": "custom_card_entry_item",
				"parent": "custom_card_entry",
				"qty":"qty",
				"serial_no":"serial_no"
			},
			"postprocess": update_item,
		},
	}, target_doc, set_missing_values)

	return doc    

def item_exists_in_SO(item_code,qty,serial_nos):
	results=frappe.db.sql("""select SOI.warehouse,SOI.serial_no,SOI.name,SO.name as so_name
							from `tabSales Order` as SO
							inner join `tabSales Order Item` as SOI
							on SO.name=SOI.parent
							where SOI.item_code = %(item_code)s
							and SOI.qty=%(qty)s
			""", {
				'item_code': item_code,
				'qty':qty
			},as_dict=True)
	if len(results)>0:
		for result in results:
			if qty==1 and cstr(result.serial_no).strip().upper()== cstr(serial_nos).strip().upper():
				return result
			elif cstr(result.serial_no).strip().upper()== cstr(serial_nos).strip().upper():
				return result
			elif sorted(result.serial_no.split(",")) ==  sorted(serial_nos.split(",")) :
				return result
		return False
	else:
		return False

@frappe.whitelist()
def custom_logic_on_submit_of_purchase_receipt(self,method):
	update_serial_no_status_from_purchase_receipt(self,method)
	update_sales_order_item_warehouse_based_on_purchase_receipt_item_warehouse(self,method)

@frappe.whitelist()
def update_sales_order_item_warehouse_based_on_purchase_receipt_item_warehouse(self,method):
	for item in self.items:
		if item.item_code and item.serial_no :
			result=item_exists_in_SO(item.item_code,item.qty,item.serial_no)
			if result:
				if result.warehouse==item.warehouse:
					return True
				else:
					frappe.db.set_value('Sales Order Item', result.name, 'warehouse', item.warehouse)
					frappe.msgprint(_('Warehouse is updated for item {0} in sales order {1}').format(
								frappe.bold(item.item_code), frappe.bold(get_link_to_form('Sales Order', result.so_name))))


@frappe.whitelist()
def update_serial_no_status_from_purchase_receipt(self,method):
	""" update serial no doc with details of Purchase Receipt"""
	purchase_receipt_doc = self.name
	if purchase_receipt_doc:
		if self.is_return == 1 :
			for item in self.items:
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
					if item.serial_no and abs(cint(item.qty)) != len(si_serial_nos):
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
							#whatever be reservation_status set to returned
							if sno.reservation_status:
								sno.reservation_status='Returned'
								sno.save(ignore_permissions=True)
						elif len(serial_no)==0:
							pass
						else:
							# check for invalid serial number
							frappe.throw(_("{0} is invalid serial number").format(serial_no))                  
		elif self.is_return== 0 :
			for item in self.items:
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
							#stop if reservation_status=='Sold Out'
							if sno.reservation_status=='Sold Out':
								frappe.throw(_("It is sold out"))
							# pass, if reservation_status=='Reserved'
							if sno.reservation_status=='Reserved':
								pass
							# check, reservation_status=='Showroom Car', set to 'Available'
							if sno.reservation_status=='Showroom Car':
								sno.reservation_status='Available'
								sno.save(ignore_permissions=True)
						elif len(serial_no)==0:
							pass
						else:
							# check for invalid serial number
							frappe.throw(_("{0} is invalid serial number").format(serial_no))

@frappe.whitelist()
def on_submit_of_purchase_invoice(self,method):
	update_warranty_card_issued(self,method)
	update_serial_no_status_from_purchase_invoice(self,method)

@frappe.whitelist()
def update_serial_no_status_from_purchase_invoice(self,method):
	""" update serial no doc with details of Purchase Invoice"""
	purchase_invoice_doc = self.name
	if purchase_invoice_doc:
		if self.is_return == 1 and self.update_stock == 1:
			for item in self.items:
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
					if item.serial_no and abs(cint(item.qty)) != len(si_serial_nos):
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
							#whatever be reservation_status set to returned
							if sno.reservation_status:
								sno.reservation_status='Returned'
								sno.save(ignore_permissions=True)
						elif len(serial_no)==0:
							pass
						else:
							# check for invalid serial number
							frappe.throw(_("{0} is invalid serial number").format(serial_no))       

@frappe.whitelist()
def make_purchase_receipt_from_showroom_car(source_name,serial_no,target_doc=None,):

	def set_missing_values(source, target):
		if len(target.get("items")) == 0:
			frappe.throw(_("No Items found"))

		doc = frappe.get_doc(target)
		doc.ignore_pricing_rule = 1
		doc.run_method("onload")
		doc.run_method("set_missing_values")
		doc.run_method("calculate_taxes_and_totals")
	 
	def update_item(obj, target, source_parent):
		target.received_qty=flt(obj.qty)
		target.qty = flt(obj.qty)
		if obj.rate>0:
			target.rate=obj.rate

	doc = get_mapped_doc("Showroom Car", source_name,	{
		"Showroom Car": {
			"doctype": "Purchase Receipt",
			"field_map": {
				"supplier":"supplier",
			},
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"Showroom Car Item": {
			"doctype": "Purchase Receipt Item",
			"field_map": {
				"name": "showroom_car_item",
				"parent": "showroom_car",
				"qty":"qty",
				"serial_no":"serial_no"
			},
			"postprocess": update_item,
			"condition": lambda doc: serial_no in doc.serial_no
		},
	}, target_doc, set_missing_values)

	return doc

@frappe.whitelist()
def make_custom_card_from_purchase_order(source_name,target_doc=None,):

	def set_missing_values(source, target):
		if len(target.get("custom_card_item")) == 0:
			frappe.throw(_("No Items found"))
		doc = frappe.get_doc(target)
		doc.supplier=source.supplier
		doc.run_method("onload")
		doc.run_method("set_missing_values")
	 
	def update_item(obj, target, source_parent):
		target.item_code=obj.item_code
		target.item_name=obj.item_name
		target.qty = flt(obj.qty)

	doc = get_mapped_doc("Purchase Order", source_name,	{
		"Purchase Order": {
			"doctype": "Custom Card Entry",
			"field_map": {
				"supplier":"supplier",
			}
		},
		"Purchase Order Item": {
			"doctype": "Custom Card Entry Item",
			"field_map": {
				"name": "po_detail",
				"parent": "purchase_order",
				"qty":"qty",
				"serial_no":"serial_no"
			},
			"postprocess": update_item,
		},
	}, target_doc, set_missing_values)

	return doc


@frappe.whitelist()
def make_custom_card_from_car_stock_entry(source_name,target_doc=None,):
	def set_missing_values(source, target):
		if len(target.get("custom_card_item")) == 0:
			frappe.throw(_("No Items found"))
		doc = frappe.get_doc(target)
		doc.supplier=source.supplier
		doc.run_method("set_missing_values")
	 
	def update_item(obj, target, source_parent):
		target.item_code=obj.item_code
		target.item_name=frappe.db.get_value('Item', obj.item_code, 'item_name')
		target.qty = flt(obj.qty)
		target.serial_no=obj.serial_no

	doc = get_mapped_doc("Car Stock Entry", source_name,	{
		"Car Stock Entry": {
			"doctype": "Custom Card Entry",
			"field_map": {
				"supplier":"supplier",
			}
		},
		"Car Stock Entry Detail": {
			"doctype": "Custom Card Entry Item",
			"field_map": {
				"name": "items",
				"parent": "car_stock_entry",
				"item_code":"qty",
				"qty":"qty",
				"serial_no":"serial_no"
			},
			"postprocess": update_item,
		},
	}, target_doc, set_missing_values)
	return doc

@frappe.whitelist()
def make_custom_card_from_purchase_receipt(source_name,target_doc=None,):
	def set_missing_values(source, target):
		if len(target.get("custom_card_item")) == 0:
			frappe.throw(_("No Items found"))

		doc = frappe.get_doc(target)
		doc.supplier=source.supplier
		doc.run_method("onload")
		doc.run_method("set_missing_values")
	 
	def update_item(obj, target, source_parent):
		target.item_code=obj.item_code
		target.item_name=obj.item_name
		target.qty = flt(obj.qty)
		target.serial_no=obj.serial_no

	doc = get_mapped_doc("Purchase Receipt", source_name,	{
		"Purchase Receipt": {
			"doctype": "Custom Card Entry",
			"field_map": {
				"supplier":"supplier",
			}
		},
		"Purchase Receipt Item": {
			"doctype": "Custom Card Entry Item",
			"field_map": {
				"name": "pr_detail",
				"parent": "purchase_receipt",
				"qty":"qty",
				"serial_no":"serial_no"
			},
			"postprocess": update_item,
		},
	}, target_doc, set_missing_values)
	return doc

@frappe.whitelist()
def make_purchase_order_from_new_car_request(source_name,target_doc=None,):

	def set_missing_values(source, target):
		if len(target.get("items")) == 0:
			frappe.throw(_("No Items found"))

		doc = frappe.get_doc(target)
		doc.ignore_pricing_rule = 1
		doc.run_method("onload")
		doc.run_method("set_missing_values")
		doc.run_method("calculate_taxes_and_totals")
	 
	def update_item(obj, target, source_parent):
		target.qty = flt(obj.qty)
		if obj.rate>0:
			target.rate=obj.rate

	doc = get_mapped_doc("New Car Request", source_name,	{
		"New Car Request": {
			"doctype": "Purchase Order",
			"field_map": {
				# "supplier":"supplier",
			},
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"New Car Request Item": {
			"doctype": "Purchase Order Item",
			"field_map": {
				"name": "new_car_request_item",
				"parent": "new_car_request",
				"qty":"qty",
			},
			"postprocess": update_item,
		},
	}, target_doc, set_missing_values)

	return doc

@frappe.whitelist()
def preserve_last_purchase_document_values(self,method):
	if self.stock_entry_type =='Material Transfer':
		for item in self.items:
			# check for empty serial no
			if item.serial_no:
				# match item qty and serial no count
				serial_nos = item.serial_no
				si_serial_nos = set(get_serial_nos(serial_nos))
				if item.serial_no and abs(cint(item.qty)) != len(si_serial_nos):
					frappe.throw(_("Row {0}: {1} Serial numbers required for Item {2}. You have provided {3}.".format(
						item.idx, item.qty, item.item_code, len(si_serial_nos))))
				for serial_no in item.serial_no.split("\n"):
					if serial_no and frappe.db.exists('Serial No', serial_no) :
						#match item_code with serial number-->item_code
						sno_item_code=frappe.db.get_value("Serial No", serial_no, "item_code")
						if (cstr(sno_item_code) != cstr(item.item_code)):
							frappe.throw(_("{0} serial number is not valid for {1} item code").format(serial_no,item.item_code))
						sno = frappe.get_doc('Serial No', serial_no)
						if not sno.original_purchase_doc_no_cf :
							sno.original_purchase_doctype_cf=sno.purchase_document_type
							sno.original_purchase_doc_no_cf=sno.purchase_document_no
							sno.save(ignore_permissions=True)
					elif len(serial_no)==0:
						pass
					else:
						# check for invalid serial number
						frappe.throw(_("{0} is invalid serial number").format(serial_no))

@frappe.whitelist()
def make_car_stock_entry(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.entry_type='Receipt'
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		pass

	def get_existing_CSE_items(po_reference):
		items = frappe.db.sql('''
					select CSED.item_code,sum(CSED.qty) as qty from 
					`tabCar Stock Entry` CSE inner join
					`tabCar Stock Entry Detail` CSED
					on CSE.name=CSED.parent
					where 
					CSE.entry_type='Receipt'
					and CSE.po_reference=%s
					and CSED.docstatus!=2
					group by CSED.item_code
		''', (po_reference), as_dict=True)

		return items



	doc = get_mapped_doc("Purchase Order", source_name,	{
		"Purchase Order": {
			"doctype": "Car Stock Entry",
			"field_map": {
				"company": "company",
				"po_reference":"purchase_order"
			},
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"Purchase Order Item": {
			"doctype": "Car Stock Entry Detail",
			"field_map": {
				"name": "purchase_order_item",
				"parent": "purchase_order",
				"item_code":"item_code",
				"qty":"qty"
			},
			"postprocess": update_item,
			"condition": lambda doc: frappe.db.get_value("Item", doc.item_code, "has_serial_no")==1,
		}
	}, target_doc, set_missing_values)

	existing_items=get_existing_CSE_items(source_name)
	if existing_items:
		for idx,item in enumerate(doc.get('items')):
			for existing_item in existing_items:
				if item.item_code == existing_item.item_code and existing_item.qty >=item.qty:
					doc.items.remove(item)
				elif item.item_code == existing_item.item_code and existing_item.qty < item.qty:
					doc.items[idx].qty=(item.qty-existing_item.qty)
	return doc						

	

@frappe.whitelist()
def make_return_car_stock_entry(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.entry_type='Return'
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	doc = get_mapped_doc("Car Stock Entry", source_name,	{
		"Car Stock Entry": {
			"doctype": "Car Stock Entry",
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"Car Stock Entry Detail": {
			"doctype": "Car Stock Entry Detail"
		}
	}, target_doc, set_missing_values)

	return doc	


def get_serial_nos_from_custom_card(purchase_order):
		return frappe.db.sql("""select serial_no from `tabCustom Card Entry` as CC
					inner join `tabCustom Card Entry Item` as CCE
					on CC.name=CCE.parent
					where from_doctype='Purchase Order'
					and from_docname=%(from_docname)s""", {
									'from_docname': purchase_order
								},as_dict=True)

@frappe.whitelist()
def custom_logic_on_cancel_of_purchase_order(self,method):
	update_serial_no_status_from_po(self,method)
	delink_custom_card_entry_from_po(self,method)


def update_serial_no_status_from_po(self,method):
	if self.docstatus==2 or self.status == "Closed":
		# get serial_no value from custom card
		result=get_serial_nos_from_custom_card(self.name)
		if len(result)>0:
			for row in result:
				serial_nos = get_serial_nos(row.serial_no)
				for serial_no in serial_nos:
					frappe.db.set_value('Serial No', serial_no, 'reservation_status', 'Returned')


					
				
def delink_custom_card_entry_from_po(self,method):
	linked_custom_card_entry=frappe.get_all('Custom Card Entry', filters = [["po_reference", "=", self.name]], fields=['name'])
	if linked_custom_card_entry:
		for custom_card_entry in linked_custom_card_entry:
			custom_card_entry_name=custom_card_entry.name
			frappe.db.set_value('Custom Card Entry', custom_card_entry_name, 'po_reference', None)
			frappe.db.commit()
			frappe.msgprint(_('Custom Card Entry {0} is updated. Purchase Order {1} reference is removed').format(
					frappe.bold(get_link_to_form('Custom Card Entry', custom_card_entry_name)),frappe.bold(self.name))) 