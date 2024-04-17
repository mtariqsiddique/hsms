app_name = "hsms"
app_title = "hsms"
app_publisher = "Tariq Siddique"
app_description = "housing society management system"
app_email = "tariq.siddique84@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

website_context = {
	"favicon": "/assets/hsms/images/smart_logo.svg",
	"splash_image": "/assets/hsms/images/smart_biz_logo.svg",
}

# include js, css files in header of desk.html
# app_include_css = "/assets/hsms/css/hsms.css"
# app_include_js = "/assets/hsms/js/hsms.js"

# include js, css files in header of web template
# web_include_css = "/assets/hsms/css/hsms.css"
# web_include_js = "/assets/hsms/js/hsms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hsms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hsms/public/icons.svg"

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
# 	"methods": "hsms.utils.jinja_methods",
# 	"filters": "hsms.utils.jinja_filters"
# }

# Installation
# ------------
after_migrate = "hsms.setup.install.after_migrate"
after_install = "hsms.setup.install.after_migrate"

# Uninstallation
# ------------

before_uninstall = "hsms.setup.install.before_uninstall"

# after_uninstall = "hsms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hsms.utils.before_app_install"
# after_app_install = "hsms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hsms.utils.before_app_uninstall"
# after_app_uninstall = "hsms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hsms.notifications.get_notification_config"

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
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
    "Journal Entry": {
        'on_cancel': [
            'hsms.events.journal_entry.check_plot_booking',
            'hsms.events.journal_entry.check_document_status'
        ]
    },
    "Customer": {
        'validate': [
            'hsms.events.customer.validate_id_card_number_format',
            "hsms.events.customer.validate_check_duplicate_cnic_number"
        ]
    },
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hsms.tasks.all"
# 	],
# 	"daily": [
# 		"hsms.tasks.daily"
# 	],
# 	"hourly": [
# 		"hsms.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hsms.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hsms.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "hsms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hsms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hsms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hsms.utils.before_request"]
# after_request = ["hsms.utils.after_request"]

# Job Events
# ----------
# before_job = ["hsms.utils.before_job"]
# after_job = ["hsms.utils.after_job"]

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
# 	"hsms.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

