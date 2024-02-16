# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from distutils.log import debug
import frappe
import erpnext
from frappe.utils import flt


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
Supplier,supplier,Link,Supplier,110
Individual Car Entry,individual_car_entry_reference,Link,Individual Car Stock Entry,130
Sales Invoice,sales_invoice,Link,Sales Invoice,110
Customer Name,customer_name,,,120
Sales Date,sales_date,Date,,100
Sales Amount,sales_amount,Currency,,120
Cost Amount,cost_amount,Currency,,120
Plate No Cost,plate_no_cost,Currency,,110
Insurance Expense,insurance_expense,Currency,,110
Transfer Cost,transfer_cost,Currency,,110
Maintenance Cost,maintenance_cost,Currency,,110
Other Expense,other_expense,Currency,,110
Sales Person Profit Expense,profit_for_sales_person,Currency,,110
Partner Profit Expense,profit_for_sales_partner,,110
Total Expense,total_expense,Currency,,110
Net Profit,net_profit,Currency,,120
Percentage,net_percentage,Percent,,100,1
"""
    )


def get_conditions(filters=None):
    conditions = []

    conditions += ["tsn.reservation_status in ('Sold Out','Sold Individual') "]

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
		tsn.name serial_no , tsn.item_code , tsn.item_name ,
		tsn.car_color_cf , tsn.car_model_cf , tpi.supplier , 
        case 
        when tsn.individual_car_entry_reference is not null then 
        (
            select name 
            from `tabSales Invoice` x
            where x.individual_car_entry_reference = tsn.individual_car_entry_reference
            and x.docstatus=1
        )
        else tsn.delivery_document_no 
        end sales_invoice , 
		tsn.customer,tsn.customer_name, tsn.delivery_date sales_date ,   
		tsii.rate , 
        tsn.individual_car_entry_reference,
	CASE
		WHEN tsn.individual_car_entry_reference is not null THEN (
		select
			icse.sale_rate
		from
			`tabIndividual Car Stock Entry` icse
        where
			icse.name = tsn.individual_car_entry_reference    
)
		ELSE tsii.base_net_amount
	END as sales_amount,        
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
    ispd.profit_for_party AS profit_for_sales_person,
    ispartd.profit_for_party AS profit_for_sales_partner,
	IFNULL(COALESCE(exp.plate_no_cost,0) + COALESCE(exp.insurance_expense,0) +	COALESCE(exp.transfer_cost,0) +COALESCE(exp.maintenance_cost,0) + COALESCE(ispd.profit_for_party,0) + COALESCE(ispartd.profit_for_party,0) + COALESCE(exp.other_expense,0),0) as total_expense,
		(COALESCE((SELECT sales_amount),0)-(IFNULL((SELECT cost_amount),0)+COALESCE((SELECT total_expense),0))) as net_profit,
		(COALESCE((SELECT net_profit),0)/(SELECT sales_amount))*100 as net_percentage    
	from `tabSerial No` tsn 
left outer join `tabPurchase Invoice Item` tpii on
	tpii.item_code = tsn.item_code
	and tpii.serial_no = tsn.name
    and tpii.docstatus = 1
left outer join `tabPurchase Invoice` tpi on
	tpi.name = tpii.parent
	and tpi.docstatus = 1
left outer join `tabSales Invoice Item` tsii on
	tsii.parent = tsn.delivery_document_no
	and tsii.item_code = tsn.item_code
	and tsii.serial_no = tsn.name
	and tsii.docstatus = 1
left outer join `tabSales Invoice` tsi on 
	tsi.name=tsii.parent 
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
                teed.expense_account , teed.amount , teed.serial_no 
            from `tabExpense Entry` tee 
            inner join `tabExpenses Entry Detail` teed on teed.parent = tee.name 
                and tee.docstatus = 1 -- and tee.company = %(company)s
                and teed.serial_no is not null
            union all		
            select 
                tjea.account , tje.total_debit , tjea.serial_no_cf 
            from `tabJournal Entry` tje 
            inner join `tabJournal Entry Account` tjea on tjea.parent = tje.name
                and tje.docstatus = 1 -- and tje.company = %(company)s
                and tjea.serial_no_cf is not null
            union all
            select 
                tpii.expense_account , tpii.amount , tpii.serial_no 
            from `tabPurchase Invoice` tpi 
            inner join `tabPurchase Invoice Item` tpii on tpii.parent = tpi.name
                and tpi.docstatus = 1 -- and tpi.company = %(company)s
                and tpii.serial_no is not null
        ) t
        group by serial_no	
	) exp on exp.serial_no = tsn.name 
    left outer join `tabIEC Sales Person Detail`  ispd on
    ispd.item_code = tsn.item_code
    and ispd.serial_no = tsn.name
    and ispd.docstatus=1
    left outer join  `tabInternal Employee Commission` iec on 
    iec.name=ispd.parent
    and iec.company= %(company)s
    left outer join `tabIEC Sales Partner Detail`  ispartd on
    ispartd.item_code = tsn.item_code
    and ispartd.serial_no = tsn.name
    and ispartd.docstatus=1
    left outer join  `tabInternal Employee Commission` isparec on 
    isparec.name=ispartd.parent
    and isparec.company= %(company)s    
        {conditions}
    order by tsi.posting_date
    """.format(
            conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        debug=1
    )
    expense_accounts={
        frappe.db.get_value('Company', filters["company"], 'car_plate_no_cost_account_cf'):'plate_no_cost',
        frappe.db.get_value('Company', filters["company"], 'car_insurance_expense_account_cf'):'insurance_expense',
        frappe.db.get_value('Company', filters["company"], 'car_transfer_cost_account_cf'):'transfer_cost',
        frappe.db.get_value('Company', filters["company"], 'car_maintenance_cost_account_cf'):'maintenance_cost',
        frappe.db.get_value('Company', filters["company"], 'car_other_expense_account_cf'):'other_expense'

    }

    for d in data:
        if d['individual_car_entry_reference']:
            individual_car_entry_expenses=frappe.db.get_list('Individual Car Expense Detail',filters={'parent':  d['individual_car_entry_reference'] }, 
                                                             fields=['expense_account', 'amount','name','parent'])
            if individual_car_entry_expenses and len(individual_car_entry_expenses)>0:
                for individual_expenses in individual_car_entry_expenses:
                    if individual_expenses.get('expense_account'):
                        expense_account_type=expense_accounts.get(individual_expenses.get('expense_account'))
                        d[expense_account_type]=(d[expense_account_type] or 0 )+individual_expenses.get('amount')
            d['customer_name']=frappe.db.get_value('Individual Car Stock Entry', d['individual_car_entry_reference'], 'customer_buyer')
            d['sales_date']=frappe.db.get_value('Individual Car Stock Entry', d['individual_car_entry_reference'], 'selling_or_return_date')
        # user to link expense from purchase invoice by tagging Serial No in Item Line for that expense line
        if d['serial_no']:
            pi_expense_amount = frappe.db.sql(
                """select tpii.amount,tpii.expense_account  FROM `tabPurchase Invoice Item` tpii 
                    inner join `tabPurchase Invoice` tpi 
                    on tpi.name=tpii.parent 
                    WHERE tpii.serial_no = tpi.car_serial_no_to_book_expense_cf 
                    and tpi.car_serial_no_to_book_expense_cf =%s """,(d['serial_no']),as_dict=True,debug=1)     
            if pi_expense_amount and len(pi_expense_amount)>0:
                expense_account_type=expense_accounts.get(pi_expense_amount[0].expense_account)
                if expense_account_type:
                    d[expense_account_type]=(d[expense_account_type] or 0 )+pi_expense_amount[0].amount

    for d in data:
        d["total_expense"] = (
            flt(d.plate_no_cost)
            + flt(d.insurance_expense)
            + flt(d.transfer_cost)
            + flt(d.maintenance_cost)
            + flt(d.profit_for_party_a)
            + flt(d.profit_for_party_b)
            + flt(d.other_expense)
        )
        d["net_profit"] = (
            flt(d.sales_amount) - (flt(d.cost_amount) + flt(d.total_expense))
        )
        if d["sales_amount"] and d["sales_amount"]!=0:
            d["net_percentage"] = (flt(d["net_profit"]) / flt(d["sales_amount"]))*100
        else:
            # to pass division by zero error
            pass

    return data
