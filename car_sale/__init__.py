# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
__version__ = '0.0.1'

# @frappe.whitelist()
# def carsale_has_customer(self):
#     pass
    # try:
    #     if self:
    #         if self.name:
    #             if self.inquiry_item:
    #                 if self.linked_quotation or self.linked_sales_order:
    #                     return None
    #                 else:
    #                     return frappe.db.get_value("Customer", {"lead_name": self.name})
    # except Exception:
    #     frappe.msgprint(Exception)
        
# from erpnext.crm.doctype.lead.lead import Lead
# Lead.has_customer = carsale_has_customer