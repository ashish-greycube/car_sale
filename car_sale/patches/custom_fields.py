import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Sales Partner": [
            dict(
                fieldname="sales_partner_commission_account_cf",
                label="Sales Partner Commission Account",
                fieldtype="Link",
                options="Account",
                insert_after="commission_rate",
            ),
        ],
        "Company":[
            dict(
                fieldname="col_break_cf",
                label="",
                fieldtype="Column Break",
                insert_after="car_other_expense_account_cf",  
            ),
            dict(
                fieldname="sales_partner_commission_expense_account_cf",
                label="Sales Partner Commission Expense Account",
                fieldtype="Link",
                options="Account",
                insert_after="col_break_cf",
            ),
            dict(
                fieldname="sales_person_commission_payable_account_cf",
                label="Sales Person Commission Payable Account",
                fieldtype="Link",
                options="Account",
                insert_after="sales_partner_commission_expense_account_cf",
            ),
            dict(
                fieldname="sales_person_commission_expense_account_cf",
                label="Sales Person Commission Account",
                fieldtype="Link",
                options="Account",
                insert_after="sales_person_commission_payable_account_cf",
            ),
        ],
        "Journal Entry":[
            dict(
                fieldname="internal_employee_commission_ref_cf",
                label="Internal Employee Commission Reference",
                fieldtype="Link",
                options="Internal Employee Commission",
                insert_after="individual_car_entry_reference", 
            ),
        ]  
    }

    create_custom_fields(custom_fields, update=True)