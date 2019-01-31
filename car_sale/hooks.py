# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "car_sale"
app_title = "Car Sale"
app_publisher = "GreyCube Technologies"
app_description = "CRM for selling cars"
app_icon = "octicon octicon-broadcast"
app_color = "#d90000"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/car_sale/css/car_sale.css"
# app_include_js = "/assets/car_sale/js/car_sale.js"

# include js, css files in header of web template
# web_include_css = "/assets/car_sale/css/car_sale.css"
# web_include_js = "/assets/car_sale/js/car_sale.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
"Lead" : "public/js/lead.js",
"Quotation":"public/js/quotation.js",
"Sales Order":"public/js/sales_order.js",
"Sales Invoice":"public/js/car_search.js",
"Stock Entry":"public/js/car_search.js",
"Material Request":"public/js/car_search.js",
"Request for Quotation":"public/js/car_search.js",
"Supplier Quotation":"public/js/car_search.js",
"Purchase Order":"public/js/car_search.js",
"Purchase Invoice":"public/js/car_search.js",
"Delivery Note":"public/js/car_search.js",
"Stock Reconciliation":"public/js/car_search.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "car_sale.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "car_sale.install.before_install"
# after_install = "car_sale.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "car_sale.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
	"Sales Order": {
		"after_insert": "car_sale.api.update_lead_status_from_sales_order",
		"validate":"car_sale.api.update_serial_no_from_so",
		"on_cancel":"car_sale.api.unreserve_serial_no_from_so_on_cancel"
		
	},
    "Quotation": {
		"on_change": "car_sale.api.update_lead_status_from_quotation",
		"on_submit":"car_sale.api.update_serial_no_from_quotation",
		"on_cancel":"car_sale.api.unreserve_serial_no_from_quotation",
		"on_update_after_submit":"car_sale.api.unreserve_serial_no_from_quotation"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"car_sale.tasks.all"
# 	],
# 	"daily": [
# 		"car_sale.tasks.daily"
# 	],
# 	"hourly": [
# 		"car_sale.tasks.hourly"
# 	],
# 	"weekly": [
# 		"car_sale.tasks.weekly"
# 	]
# 	"monthly": [
# 		"car_sale.tasks.monthly"
# 	]
# }

scheduler_events = {
	"daily": [
		"car_sale.api.auto_unreserve_serial_no_from_quotation_on_expiry"
	]
}

# Testing
# -------

# before_tests = "car_sale.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "car_sale.event.get_events"
# }

