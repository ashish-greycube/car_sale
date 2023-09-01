import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Sales Invoice": [
            dict(
                fieldname="car_sales_partner_comission_section_cf",
                label="Car Sales Partner Comission",
                fieldtype="Section Break",
                insert_after="total_commission",
            ),
            dict(
                fieldname="car_sales_partner_cf",
                label="Car Sales Partner",
                fieldtype="Link",
                options="Sales Partner",
                insert_after="car_sales_partner_comission_section_cf",
                allow_on_submit=1
            ),
            dict(
                fieldname="col_sales_partner_comission_cf",
                label="",
                fieldtype="Column Break",
                insert_after="car_sales_partner_cf",  
            ),  
		    dict(
                fieldname="car_sales_partner_commission_rate_cf",
                label="Car Sales Partner Commission Rate (%)",
                fieldtype="Float",
                insert_after="col_sales_partner_comission_cf",
                allow_on_submit=1,
	    	)
                                              
        ]}
    print('creating fields for new sp..')
    create_custom_fields(custom_fields, update=True)
