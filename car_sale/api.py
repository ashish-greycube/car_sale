from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import (cstr, validate_email_add, cint, comma_and, has_gravatar, now, getdate, nowdate)
from frappe.model.mapper import get_mapped_doc
import frappe, json
from erpnext.controllers.selling_controller import SellingController
from frappe.contacts.address_and_contact import load_address_and_contact
from erpnext.accounts.party import set_taxes
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.party import get_party_account_currency

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
		# target_doc.quotation_to = "Customer"
		target_doc.linked_lead=source_doc.name
		if source_doc.customer:
			if source_doc.transaction_type=='Bank Funded':
				target_doc.customer=source_doc.bank_name
				target_doc.sub_customer=source_doc.customer
			else:
				target_doc.customer=source_doc.customer
		else:
			if source_doc.organization_lead==0 and source_doc.transaction_type=='Cash':
				target_doc.customer=source_doc.lead_name
			elif source_doc.organization_lead==0 and source_doc.transaction_type=='Cash':
				target_doc.customer=source_doc.company_name
			elif source_doc.organization_lead==0 and source_doc.transaction_type=='Bank Funded':
				target_doc.customer=source_doc.bank_name
				target_doc.sub_customer=source_doc.lead_name
			elif source_doc.organization_lead==1 and source_doc.transaction_type=='Bank Funded':
				target_doc.customer=source_doc.bank_name
				target_doc.sub_customer=source_doc.company_name
	table_maps={
			"Lead": 
			{"doctype": "Quotation",
			"field_map": 
			{"name": "lead","customer":"lead_name","transaction_date":"date"},
			"postprocess": update_quotation
			},
			"Inquiry Item": 
			{"doctype": "Quotation Item",
			"field_map": {"parent": "against_inquiry_item","parenttype": "Lead","uom": "stock_uom"}
			,"add_if_empty": True
			}
		}
	target_doc = get_mapped_doc("Lead",source_name,table_maps, target_doc,set_missing_values)
	print 'target_doc'
	print target_doc
	# target_doc.quotation_to = "Lead"
	target_doc.save(ignore_permissions=True)

	source_lead = frappe.get_doc('Lead', source_name)
	source_lead.linked_quotation=target_doc.name
	source_lead.set_status(update=True,status='Quotation')
	source_lead.save(ignore_permissions=True)

	return target_doc

@frappe.whitelist()
def make_customer_from_lead(doc):
	doc=frappe._dict(json.loads(doc))
	#check existing contact
	contact_name = frappe.db.get_value('Contact',{'mobile_no': doc.mobile_no}, 'name')
	if contact_name:
		#existing contact
		print 'duplicate'
		# frappe.msgprint(_("Existing contact").format(contact_name), alert=1)
		# if doc.organization_lead==1:
		# 	customer_name = frappe.db.get_value('Customer',{'name': doc.company_name}, 'name')
		# else:
		# 	customer_name = frappe.db.get_value('Customer',{'name': doc.lead_name}, 'name')
		# contact=frappe.get_doc("Contact",contact_name)
		# customer=frappe.get_doc("Customer",customer_name)
		# leave.db_set('description', new_description)
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
			customer.default_sales_partner=doc.sales_partner
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
			# frappe.msgprint(_("Company {0} contact is created").format(customer.name), alert=1)
	
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
			customer.default_sales_partner=doc.sales_partner
			customer.insert(ignore_permissions=True)
			primary_contact=get_customer_primary_contact(customer.name)
			print primary_contact
			customer.customer_primary_contact=primary_contact['name']
			customer.mobile_no=primary_contact['mobile_no']
			customer.email_id=primary_contact['email_id']
			customer.save(ignore_permissions=True)
			# frappe.msgprint(_("Individual {0} contact is created").format(customer.name), alert=1)
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
		select cust.default_sales_partner,cust.customer_group,
			cust.customer_type,
			cust.customer_name,
			RTRIM(concat(cont.first_name,' ',ifnull(cont.last_name,'')))as person_name,
			cont.email_id,
			cont.mobile_no
		from `tabCustomer` cust 
		inner join `tabContact` cont
		on cust.customer_primary_contact=cont.name
		where cont.mobile_no= %(mobile_no)s
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
def get_sales_partner(user_email):
	sales_partner= frappe.db.sql("""select name from `tabSales Partner` where user =%(user_email)s
	""",{
			'user_email': user_email
		},as_list=True)
	print 'sales_partner'
	print sales_partner
	return sales_partner[0] if sales_partner else None

# extra function
def make_customer(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		if source.company_name:
			target.customer_type = "Company"
			target.customer_name = source.company_name
		else:
			target.customer_type = "Individual"
			target.customer_name = source.lead_name

		target.customer_group = frappe.db.get_default("Customer Group")

	doclist = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Customer",
			"field_map": {
				"name": "lead_name",
				"company_name": "customer_name",
				"contact_no": "phone_1",
				"fax": "fax_1"
			}
		}}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)
	doclist.save(ignore_permissions=True)
	# make_quotation(source_name, target_doc=None)
	return doclist
	

