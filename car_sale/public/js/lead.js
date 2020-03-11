// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext");
cur_frm.email_field = "email_id";
{% include "car_sale/public/js/car_search_lead.js" %}
{% include "car_sale/public/js/sales_person.js" %}

erpnext.LeadController = frappe.ui.form.Controller.extend({
	onload: function() {
		this.frm.fields_dict.customer.get_query = function(doc, cdt, cdn) {
			return { query: "erpnext.controllers.queries.customer_query" } }

			//get only customer of bank type
			cur_frm.set_query('bank_name', function(doc) {
				return {
					query: "car_sale.api.get_bank_name"
				}
			})

	},
	validate: function() {
		if (cur_frm.doc.customer){
			cur_frm.set_value("email_id", '');
		}
		console.log(cur_frm.doc.ends_on,'cur_frm.doc.ends_on')
		if (cur_frm.doc.ends_on == undefined) {
			var ends_on = frappe.datetime.add_days(cur_frm.doc.date, 90);
			cur_frm.set_value("ends_on", ends_on);			
			
		}
	},
	sales_inquiry_type: function (frm) {
		if (cur_frm.doc.sales_inquiry_type == '') {
			// Hide 
			cur_frm.set_df_property('unknown_car_group', 'hidden', 1);
			cur_frm.set_df_property('unknown_car_brand', 'hidden', 1);
			//Make it non required
			cur_frm.set_df_property('unknown_car_group', 'reqd', 0);
			cur_frm.set_df_property('unknown_car_brand', 'reqd', 0)
			cur_frm.set_df_property('search_group', 'reqd', 0);
			cur_frm.set_df_property('search_template', 'reqd', 0);
			//Unhide
			cur_frm.set_df_property('search_group', 'hidden', 0);
			cur_frm.set_df_property('search_template', 'hidden', 0);
			cur_frm.set_df_property('search_category', 'hidden', 0);
			cur_frm.set_df_property('search_model', 'hidden', 0);
			cur_frm.set_df_property('search_color', 'hidden', 0);
			cur_frm.set_df_property('add', 'hidden', 0);
			cur_frm.set_df_property('inquiry_item', 'hidden', 0);
		} else if (cur_frm.doc.sales_inquiry_type == 'Basic Only') {
			// Hide 
			cur_frm.set_df_property('search_category', 'hidden', 1);
			cur_frm.set_df_property('search_model', 'hidden', 1);
			cur_frm.set_df_property('search_color', 'hidden', 1);
			cur_frm.set_df_property('add', 'hidden', 1);
			cur_frm.set_df_property('inquiry_item', 'hidden', 1);
			cur_frm.set_df_property('unknown_car_group', 'hidden', 1);
			cur_frm.set_df_property('unknown_car_brand', 'hidden', 1);
			//Make it non required			
			cur_frm.set_df_property('unknown_car_group', 'reqd', 0);
			cur_frm.set_df_property('unknown_car_brand', 'reqd', 0);
			//Unhide
			cur_frm.set_df_property('search_group', 'hidden', 0);
			cur_frm.set_df_property('search_template', 'hidden', 0);
			//Make it required
			cur_frm.set_df_property('search_group', 'reqd', 1);
			cur_frm.set_df_property('search_template', 'reqd', 1);
		} else if (cur_frm.doc.sales_inquiry_type == 'Unknown Car') {
			// Hide 
			cur_frm.set_df_property('search_group', 'hidden', 1);
			cur_frm.set_df_property('search_template', 'hidden', 1);
			cur_frm.set_df_property('search_category', 'hidden', 1);
			cur_frm.set_df_property('search_model', 'hidden', 1);
			cur_frm.set_df_property('search_color', 'hidden', 1);
			cur_frm.set_df_property('add', 'hidden', 1);
			cur_frm.set_df_property('inquiry_item', 'hidden', 1);
			//Make it non required
			cur_frm.set_df_property('search_group', 'reqd', 0);
			cur_frm.set_df_property('search_template', 'reqd', 0);
			//Unhide
			cur_frm.set_df_property('unknown_car_group', 'hidden', 0);
			cur_frm.set_df_property('unknown_car_brand', 'hidden', 0);
			//Make it required
			cur_frm.set_df_property('unknown_car_group', 'reqd', 1);
			cur_frm.set_df_property('unknown_car_brand', 'reqd', 1);
		}
	},
	refresh: function() {
		var doc = cur_frm.doc;
		erpnext.toggle_naming_series();
		frappe.dynamic_link = {doc: doc, fieldname: 'name', doctype: 'Lead'}

		if(!doc.__islocal && doc.__onload && !doc.__onload.is_customer) {
			// added custom option
			console.log('k')
			if(doc.status =='Ordered' ||doc.status == 'Quotation'|| doc.status =='Converted')
			{

			}else{
				console.log(doc.status)
			this.frm.add_custom_button(__("Car - Quotation"), this.make_customer_quotation, __("Make"));
			this.frm.add_custom_button(__("Car - Sales Order"), this.make_customer_sales_order, __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
			}

		}

		if(!this.frm.doc.__islocal) {
			frappe.contacts.render_address_and_contact(cur_frm);
		} else {
			frappe.contacts.clear_address_and_contact(cur_frm);
		}
	},

	client_mobile:function() {
		cur_frm.set_value("mobile_no", cur_frm.doc.client_mobile);
		return frappe.call({
			type: "POST",
			method: 'car_sale.api.get_existing_customer',
			args: {
				'mobile_no':cur_frm.doc.client_mobile
			},			
			freeze: true,
			callback: function(r) {
				if(!r.exc) {
					console.log(r.message)
					if(r.message){
						let exist_cust=r.message
						cur_frm.set_value("lead_name", exist_cust['person_name']);
						cur_frm.set_value("email_id", exist_cust['email_id']);
						cur_frm.set_value("car_customer_source", exist_cust['car_customer_source']);
						cur_frm.set_value("territory", exist_cust['territory']);
						cur_frm.set_value("source",'Existing Customer')
						
						// cur_frm.set_value("customer",exist_cust['customer_name'])
						cur_frm.set_value("customer",exist_cust['name'])
						if (exist_cust['national_id_cf']){
							cur_frm.set_value("national_id_cf", exist_cust['national_id_cf']);
						}
						if (exist_cust['customer_group']){
							cur_frm.set_value("customer_group", exist_cust['customer_group']);

						}

						cur_frm.set_df_property('lead_name', 'read_only', 1);
						cur_frm.set_df_property('email_id', 'read_only', 1);
						cur_frm.set_df_property('car_customer_source', 'read_only', 1);
						cur_frm.set_df_property('territory', 'read_only', 1);
						cur_frm.set_df_property('source', 'read_only', 1);
						cur_frm.set_df_property('customer', 'read_only', 1);
						cur_frm.set_df_property('national_id_cf', 'read_only', 1);

						if (exist_cust['customer_type']=='Company'){
							cur_frm.set_value("organization_lead", 1);
							cur_frm.set_value("company_name", exist_cust['customer_name']);
							
							cur_frm.set_df_property('organization_lead', 'read_only', 1);
							cur_frm.set_df_property('company_name', 'read_only', 1);
						}
						if (exist_cust['customer_type']=='Individual'){
							cur_frm.set_value("organization_lead", 0);
							cur_frm.set_df_property('organization_lead', 'read_only', 1);
						}
					}
					else{
						//New contact, so clear
						cur_frm.set_value("organization_lead", 0);
						cur_frm.set_value("lead_name", '');
						cur_frm.set_value("company_name", '');
						cur_frm.set_value("email_id", '');
						cur_frm.set_value("car_customer_source", '');
						cur_frm.set_value("territory", '');
						cur_frm.set_value("national_id_cf", '');

						if (cur_frm.doc.source=='Existing Customer'){
							cur_frm.set_value("source",'')
						}
						cur_frm.set_value("customer","");

						cur_frm.set_df_property('car_customer_source', 'read_only', 0);
						cur_frm.set_df_property('territory', 'read_only', 0);
						cur_frm.set_df_property('organization_lead', 'read_only', 0);
						cur_frm.set_df_property('lead_name', 'read_only', 0);
						cur_frm.set_df_property('company_name', 'read_only', 0);
						cur_frm.set_df_property('email_id', 'read_only', 0);
						cur_frm.set_df_property('source', 'read_only', 0);
						cur_frm.set_df_property('customer', 'read_only',0);
						cur_frm.set_df_property('national_id_cf', 'read_only', 0);
						if (!cur_frm.doc.sales_person){
							//get sales partenr
							return frappe.call({
								method: "car_sale.api.get_sales_person_and_branch",
								args: {"user_email":frappe.session.user_email},
								callback: function(r) {
									if(r.message) {
										let sales_person=r.message[0][0]
										let branch=r.message[0][1]
										cur_frm.set_value('sales_person',sales_person);
										cur_frm.set_value('sales_person_branch',branch);
										cur_frm.refresh_field('sales_person_branch')
										cur_frm.refresh_field('sales_person')

									}
								}
							})
	
			}
					}
				}
			}
		})

	},

	make_customer_sales_order: function() {
		if (cur_frm.doc.inquiry_item.length>0){
		var cur_doc = cur_frm.doc;
		if (cur_doc.national_id_cf.length>0) {
			return frappe.call({
				type: "POST",
				method: 'car_sale.api.make_customer_from_lead',
				args: {doc:cur_frm.doc},			
				freeze: true,
				callback: function(r) {
					console.log('r')
					console.log(r)
					if(!r.exc) {
						if (cur_frm.doc.inquiry_item){
							frappe.model.open_mapped_doc({
								method: "car_sale.api._make_sales_order",
								frm: cur_frm
							})
						}
					}
				}
			})			
		} else {
			cur_frm.set_df_property('national_id_cf', 'reqd', 1);
			frappe.msgprint(__('National ID is required, sales order cannot be created'));			
		}
	}
	else{
		cur_frm.set_df_property('inquiry_item', 'reqd', 1);
		frappe.msgprint(__('Item is empty, sales order cannot be created'));
	}
	},

	make_customer_quotation: function() {
		
		if (cur_frm.doc.inquiry_item.length>0){
		var cur_doc = cur_frm.doc;
		if (cur_doc.national_id_cf.length>0) {
			return frappe.call({
				type: "POST",
				method: 'car_sale.api.make_customer_from_lead',
				args: {doc:cur_frm.doc},			
				freeze: true,
				callback: function(r) {
					if(!r.exc) {
						if (cur_frm.doc.inquiry_item){
							frappe.model.open_mapped_doc({
								method: "car_sale.api.make_quotation_for_customer",
								frm: cur_frm
							})
						}
					}
				}
			})			
		} else {
			cur_frm.set_df_property('national_id_cf', 'reqd', 1);
			frappe.msgprint(__('National ID is required, quotation cannot be created'));				
		}
	}
	else{
		cur_frm.set_df_property('inquiry_item', 'reqd', 1);
		frappe.msgprint(__('Item is empty, quotation cannot be created'));
	}
	},
	transaction_type: function() {
		if (cur_frm.doc.transaction_type == 'Bank Funded') {
			cur_frm.set_df_property('bank_name', 'reqd', 1);
		} else {
			cur_frm.set_df_property('bank_name', 'reqd', 0);
		}
	},
	company_name: function() {
		if (this.frm.doc.organization_lead == 1) {
			// make company code inactive
			// this.frm.set_value("lead_name", this.frm.doc.company_name);
		}
	}
});

$.extend(cur_frm.cscript, new erpnext.LeadController({frm: cur_frm}));

// fill up item details
cur_frm.cscript.item_code = function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.item_code) {
		return frappe.call({
			method: "car_sale.api.get_item_details",
			args: {"item_code":d.item_code},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(k, v) {
						frappe.model.set_value(cdt, cdn, k, v);
					});
					refresh_field('image_view', d.name, 'inquiry_item');
				}
			}
		})
	}
}