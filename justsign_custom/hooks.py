app_name = "justsign_custom"
app_title = "Justsign Custom"
app_publisher = "sanpra Softwares"
app_description = "Justsign Custom"
app_email = "sanprasoftwares@gmail.com"
app_license = "mit"


# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "justsign_custom",
# 		"logo": "/assets/justsign_custom/logo.png",
# 		"title": "Justsign Custom",
# 		"route": "/justsign_custom",
# 		"has_permission": "justsign_custom.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/justsign_custom/css/justsign_custom.css"
# app_include_js = "/assets/justsign_custom/js/justsign_custom.js"

# include js, css files in header of web template
# web_include_css = "/assets/justsign_custom/css/justsign_custom.css"
# web_include_js = "/assets/justsign_custom/js/justsign_custom.js"
web_include_js = ["/assets/justsign_custom/js/custom_cart.js"]
# app_include_css = "/assets/justsign_custom/css/custom_login.css"
# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "justsign_custom/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

doctype_js = {"Lead":"public/js/custom_lead.js",
                "Prospect":"public/js/custom_prospect.js",
                "Opportunity":"public/js/custom_opportunity.js",
                "Customer":"public/js/custom_customer.js",
                "Delivery Note":"public/js/custom_delivery.js",
                "Sales Order":"public/js/custom_salesorder.js",
                "Sales Invoice":"public/js/custom_salesinvoice.js",
                "Quotation":"public/js/custom_quotation.js",
                "Purchase Receipt":"public/js/custom_purchase_receipt.js",
                "Job Card":"public/js/custom_jobcard.js",
                "Delivery Note":"public/js/delivery_note.js",
                # "Sales Order":"public/js/sales_order.js",
                # "Prospect": "public/js/prospect.js",
            }
after_migrate = ["justsign_custom.custom_pyfile.custom_python.patch_make_packing_list"]

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "justsign_custom/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------
# add methods and filters to jinja environment
# jinja = {
# 	"methods": "justsign_custom.utils.jinja_methods",
# 	"filters": "justsign_custom.utils.jinja_filters"
# }
jinja = {
    "methods": [
        "frappe.utils.data.money_in_words",
    ]
}

# Installation
# ------------

# before_install = "justsign_custom.install.before_install"
# after_install = "justsign_custom.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "justsign_custom.uninstall.before_uninstall"
# after_uninstall = "justsign_custom.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "justsign_custom.utils.before_app_install"
# after_app_install = "justsign_custom.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "justsign_custom.utils.before_app_uninstall"
# after_app_uninstall = "justsign_custom.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "justsign_custom.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"Payment Entry": "justsign_custom.overrides.payment_entry.CustomPaymentEntry"
# }
# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    "Prospect": {
        "before_save": "justsign_custom.custom_pyfile.custom_python.before_save",
        "on_trash": "justsign_custom.custom_pyfile.custom_python.on_trash"
    },
     "Customer": { 
        "before_save": "justsign_custom.custom_pyfile.custom_python.cust_set_status",
        "on_trash": "justsign_custom.custom_pyfile.custom_python.cust_del_set_status"
    },
    # "Sales Invoice": {
    #     "on_submit": [
    #         "justsign_custom.custom_pyfile.custom_python.salesinvocie_after_save",
    #         "justsign_custom.public.py.sales_invoice.send_invoice_email",
    #     ]
    # },
    "Sales Invoice": {
        "on_submit":[
            "justsign_custom.public.py.sales_invoice.create_and_attach_pdf",
            "justsign_custom.public.py.sales_invoice.send_invoice_email",
        ],
        "on_update_after_submit": "justsign_custom.public.py.sales_invoice.create_and_attach_pdf",
    },
    "Quotation": {
        "on_submit":[
            "justsign_custom.public.py.quotation.create_and_attach_pdf",
            "justsign_custom.public.py.quotation.send_invoice_email",
        ], 
        "on_update_after_submit": "justsign_custom.public.py.quotation.create_and_attach_pdf",
    },
    "Delivery Note": {  
        "on_submit": "justsign_custom.custom_pyfile.custom_python.delivery_note_submit",
    }, 
    "Lead": {
        "after_insert": "justsign_custom.public.py.custom_lead.assign_sales_partner",
        "on_update": "justsign_custom.public.py.custom_lead.assign_sales_partner"
    },
    "Sales Partner Assigned Lead": {
        "after_insert": "justsign_custom.public.py.custom_sales_partner_assign_lead.create_opportunity"
    },
    "Opportunity":{
        "before_save":[
            "justsign_custom.public.py.opportunity.set_quotation_lost",
            "justsign_custom.public.py.opportunity.set_prospect_company_name"
            # "after_save": "justsign_custom.public.py.opportunity.set_quotation_lost" 
        ] 
    },
    "ToDo": {
        "after_insert": "justsign_custom.public.py.todo_webhook.update_due_checkbox",
        "on_update": "justsign_custom.public.py.todo_webhook.update_due_checkbox"
    },
     "Event": {
        "before_insert": "justsign_custom.public.py.event.set_event_public"
    },
    # "Sales Order": {
    #     "validate": "justsign_custom.public.py.sales_order.apply_freight_rule"
    # }
   
    # "Sales Order": {
    #       "on_submit": "justsign_custom.public.py.sales_order.create_and_attach_pdf"
    #   #   "on_submit": "justsign_custom.public.py.sales_order.create_job_cards",
    # },
}
# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"justsign_custom.tasks.all"
# 	],
# 	"daily": [
# 		"justsign_custom.tasks.daily"
# 	],
	"hourly": [
		"justsign_custom.justsign_custom.doctype.plan_visit.plan_visit.recurring_plan"
	],
    "daily": [
        "justsign_custom.public.py.notification.send_todo_summary",
        "justsign_custom.public.py.notification.send_due_date_reminder",
        "justsign_custom.public.py.notification.send_overdue_todos",
        "justsign_custom.public.py.todo_webhook.check_due_todos",
    ],
    "cron": { 
        "59 23 * * *": [
            "justsign_custom.public.py.notification.send_camping_wise_lead_report_html",
            "justsign_custom.public.py.notification.brand_costcenter_sales_mail"
        ]
    }

# 	"weekly": [
# 		"justsign_custom.tasks.weekly"
# 	],
# 	"monthly": [
# 		"justsign_custom.tasks.monthly"
# 	],
}

# Testing
# -------

# before_tests = "justsign_custom.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "justsign_custom.event.get_events"
# }
override_whitelisted_methods = {
    "webshop.webshop.shopping_cart.cart.update_cart": "justsign_custom.public.py.web_cart.update_cart",
    "webshop.webshop.shopping_cart.cart.place_order": "justsign_custom.public.py.web_cart.place_order",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "justsign_custom.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]
ignore_links_on_delete = ["Job Cards"]

# Request Events
# ----------------
# before_request = ["justsign_custom.utils.before_request"]
# after_request = ["justsign_custom.utils.after_request"]

# Job Events
# ----------
# before_job = ["justsign_custom.utils.before_job"]
# after_job = ["justsign_custom.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"justsign_custom.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
