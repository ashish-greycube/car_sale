from __future__ import unicode_literals
from frappe import _
import frappe


def get_data():
    return [
        {
            "label": _("Car Sale - Comission"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Individual Car Stock Entry",
                },   
                {
                    "type": "doctype",
                    "name": "Company",
                },      
                                                     
            ],
        },        
        {
            "label": _("Setup"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Car Customer Source",
                },
                {
                    "type": "doctype",
                    "name": "Custom Card Entry",
                },
                {
                    "type": "doctype",
                    "name": "Expense Entry",
                },
                {
                    "type": "doctype",
                    "name": "GTP Color",
                },
                {
                    "type": "doctype",
                    "name": "New Car Request",
                },
                {
                    "type": "doctype",
                    "name": "Showroom Car",
                },
                {
                    "type": "doctype",
                    "name": "Warranty Card Issued",
                }              
            ],
        },
        {
            "label": _("Standard Reports"),
            "items": [
                {
                    "type": "report",
                    "name": "Car Available Stock Inquiry",
                    "is_query_report": True,
                    "doctype": "Serial No",
                },
                {
                    "type": "report",
                    "name": "Car Available Stock Serial No Wise",
                    "is_query_report": True,
                    "doctype": "Serial No",
                },
                {
                    "type": "report",
                    "name": "Car Comprehensive",
                    "is_query_report": True,
                    "doctype": "Serial No",
                },
                {
                    "type": "report",
                    "name": "Car Sales Report",
                    "is_query_report": True,
                    "doctype": "Serial No",
                },
                {
                    "type": "report",
                    "name": "Car Sales Analysis",
                    "is_query_report": True,
                    "doctype": "Serial No",
                },
                {
                    "type": "report",
                    "name": "Car Serial No",
                    "is_query_report": True,
                    "doctype": "Serial No",
                },
                {
                    "type": "report",
                    "name": "Car Serial No for Sales",
                    "is_query_report": True,
                    "doctype": "Serial No",
                },
                {
                    "type": "report",
                    "name": "Sales Inquiry Analysis",
                    "is_query_report": True,
                    "doctype": "Lead",
                },
                {
                    "type": "report",
                    "name": "Stock Balance with Balance Serial No",
                    "is_query_report": True,
                    "doctype": "Stock Ledger Entry",
                },
            ],
        },
    ]
