# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from distutils.log import debug
import frappe
import erpnext


def csv_to_columns(csv_str):
    props = ["label", "fieldname", "fieldtype", "options", "width", "precision"]
    return [
        zip(props, [x.strip() for x in col.split(",")])
        for col in csv_str.split("\n")
        if col.strip()
    ]


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_columns(filters=None):
    return csv_to_columns(
        """
Serial No,serial_no,Link,Serial No,130
Item Name,item_name,Data,,210
Color,car_color_cf,,,70
Model,car_model_cf,,,70
Reservation Status,reservation_status,,,100
Supplier,supplier,,,110,
Purchase Reference,purchase_invoice,,,100,
Purchase Date,purchase_date,Date,,100
Purchase Rate,cost_amount,Currency,,120
Plate No Cost,plate_no_cost,Currency,,100
Insurance Expense,insurance_expense,Currency,,100
Transfer Cost,transfer_cost,Currency,,100
Maintenance Cost,maintenance_cost,Currency,,100
Other Expense,other_expense,Currency,,100
Total Expense,total_expense,Currency,,110
Total Cost,total_cost,Currency,,110
"""
    )


def get_conditions(filters=None):
    conditions = []

    conditions += ["1=1"]

    if filters.get("item_code"):
        conditions += ["tsn.item_code = %(item_code)s"]
    if filters.get("customer"):
        conditions += ["tsi.customer = %(customer)s"]
    if filters.get("color"):
        conditions += ["tsn.car_color_cf = %(color)s"]
    if filters.get("model"):
        conditions += ["tsn.car_model_cf = %(model)s"]
    if filters.get("car_type"):
        car_type_filter = filters.get("car_type")
        if car_type_filter == "Individual Car":
            conditions += ["tsn.individual_car_entry_reference   IS NOT NULL "]
        elif car_type_filter == "Purchase Car":
            conditions += ["tsn.individual_car_entry_reference   IS  NULL "]
    return conditions and " where " + " and ".join(conditions) or ""


def get_data(filters=None):
    filters["company"] = erpnext.get_default_company()

    # TODO: logic for cost amount

    data = frappe.db.sql(
        """
    select 
    tsn.name serial_no ,
    tsn.item_code ,
    tsn.item_name ,
    tsn.car_color_cf ,
    tsn.car_model_cf ,
    tsn.reservation_status,
    tpi.supplier ,
    tpi.name as purchase_invoice,
    tpi.posting_date as purchase_date,
    tsn.individual_car_entry_reference,
    CASE
        WHEN tsn.individual_car_entry_reference is not null THEN (
        select
            icse.receive_rate 
        from
            `tabIndividual Car Stock Entry` icse
        left outer join `tabIndividual Car Expense Detail` iced on
            icse.name = iced.parent
        where
            icse.name = tsn.individual_car_entry_reference
        group by
            icse.name
)
        ELSE tsn.purchase_rate
    END as cost_amount,
    exp.plate_no_cost ,
    exp.insurance_expense ,
    exp.transfer_cost ,
    exp.maintenance_cost ,
    exp.other_expense ,
    coalesce(COALESCE(exp.plate_no_cost,0) + COALESCE(exp.insurance_expense,0) + COALESCE(exp.transfer_cost,0) + COALESCE(exp.maintenance_cost,0) + COALESCE(exp.other_expense), 0) as total_expense,
    (COALESCE((SELECT total_expense),0) + COALESCE((SELECT cost_amount),0)) as total_cost 
from `tabSerial No` tsn
left outer join `tabPurchase Invoice Item` tpii on
    tpii.item_code = tsn.item_code
    and tpii.serial_no = tsn.name
    and tpii.docstatus = 1
left outer join `tabPurchase Invoice` tpi on
    tpi.name = tpii.parent
    and tpi.docstatus = 1
left outer join (
    select
        serial_no ,
        sum(case when expense_account in 
            (select car_plate_no_cost_account_cf from tabCompany where name = %(company)s) then amount else 0 end) plate_no_cost ,
        sum(case when expense_account in 
            (select car_insurance_expense_account_cf from tabCompany where name = %(company)s) then amount else 0 end) insurance_expense ,
        sum(case when expense_account in 
            (select car_transfer_cost_account_cf from tabCompany where name = %(company)s) then amount else 0 end) transfer_cost ,
        sum(case when expense_account in 
            (select car_maintenance_cost_account_cf from tabCompany where name = %(company)s) then amount else 0 end) maintenance_cost ,
        sum(case when expense_account in 
            (select car_other_expense_account_cf from tabCompany where name = %(company)s) then amount else 0 end) other_expense
    from
        (
        select
            teed.expense_account ,
            teed.amount ,
            teed.serial_no
        from
            `tabExpense Entry` tee
        inner join `tabExpenses Entry Detail` teed on
            teed.parent = tee.name
            and tee.docstatus = 1
            and teed.serial_no is not null
    union all
        select
            tjea.account ,
            tje.total_debit ,
            tjea.serial_no_cf
        from
            `tabJournal Entry` tje
        inner join `tabJournal Entry Account` tjea on
            tjea.parent = tje.name
            and tje.docstatus = 1
            and tjea.serial_no_cf is not null
    union all
        select
            tpii.expense_account ,
            tpii.amount ,
            tpii.serial_no
        from
            `tabPurchase Invoice` tpi
        inner join `tabPurchase Invoice Item` tpii on
            tpii.parent = tpi.name
            and tpi.docstatus = 1
            and tpii.serial_no is not null
        ) t
    group by
        serial_no	
    ) exp on
    exp.serial_no = tsn.name 
          {conditions} 
    """.format(
            conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True
    )
    expense_accounts={
        frappe.db.get_value('Company', filters["company"], 'car_plate_no_cost_account_cf'):'plate_no_cost',
        frappe.db.get_value('Company', filters["company"], 'car_insurance_expense_account_cf'):'insurance_expense',
        frappe.db.get_value('Company', filters["company"], 'car_transfer_cost_account_cf'):'transfer_cost',
        frappe.db.get_value('Company', filters["company"], 'car_maintenance_cost_account_cf'):'maintenance_cost',
        frappe.db.get_value('Company', filters["company"], 'car_other_expense_account_cf'):'other_expense'

    }
    for d in data:
        # ignore Available-Qty / Available-Card
        if d['reservation_status'] in ['Available Individual','Sold Individual','Returned Individual']:
            if  d['individual_car_entry_reference']:
                icse = frappe.db.get_value('Individual Car Stock Entry',  d['individual_car_entry_reference'], ['customer_seller', 'entry_date'], as_dict=1)
                d['supplier']=icse.customer_seller
                d['purchase_date']=icse.entry_date
                d['purchase_invoice']=d['individual_car_entry_reference']
        elif  d['reservation_status'] in ['Showroom Car','Showroom Car-Returned']:
            showroom_rate=frappe.db.get_list('Showroom Car Item', filters=[['serial_no', '=', d.get('serial_no')]], fields=['rate','parent'],order_by='creation desc')
            if showroom_rate and len(showroom_rate)>0:            
                d['cost_amount']=showroom_rate[0].rate
                shc = frappe.db.get_value('Showroom Car', showroom_rate[0].parent, ['transaction_date', 'supplier'], as_dict=1)
                d['supplier']=shc.supplier
                d['purchase_date']=shc.transaction_date
                d['purchase_invoice']=showroom_rate[0].parent
                d['total_cost']= d['cost_amount']+d['total_expense']
        elif  d['reservation_status'] in ['Reserved','Available','Sold Out','Returned']:
            # PI
            if not d['purchase_invoice']:
                serial_dict = frappe.db.get_value('Serial No', d.get('serial_no'), ['purchase_document_type', 'purchase_document_no'], as_dict=1)
                if serial_dict and serial_dict.purchase_document_type=='Purchase Receipt':
                    pr_dict=frappe.db.get_value('Purchase Receipt',serial_dict.get('purchase_document_no'), ['supplier', 'posting_date'], as_dict=1)
                    if pr_dict:
                        d['supplier']=pr_dict.get('supplier')
                        d['purchase_invoice']=serial_dict.get('purchase_document_no')
                        d['purchase_date']=pr_dict.get('posting_date')
        
        if d['individual_car_entry_reference']:
            individual_car_entry_expenses=frappe.db.get_list('Individual Car Expense Detail',filters={'parent':  d['individual_car_entry_reference'] }, fields=['expense_account', 'amount','name','parent'])
            if individual_car_entry_expenses and len(individual_car_entry_expenses)>0:
                delta_individual_expense=0
                for individual_expenses in individual_car_entry_expenses:
                    expense_account_type=expense_accounts.get(individual_expenses.get('expense_account'))
                    d[expense_account_type]=(d[expense_account_type] or 0 )+individual_expenses.get('amount')
                    delta_individual_expense=delta_individual_expense+individual_expenses.get('amount')
                d['total_expense']=d['total_expense']+delta_individual_expense
                d['total_cost']=d['total_cost']+delta_individual_expense

    return data
