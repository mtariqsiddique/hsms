import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


# Define the function to be executed after migration
def after_migrate():
    add_roles_on_install()
    create_custom_fields(get_custom_fields())

def before_uninstall():
    delete_role()
    delete_custom_fields(get_custom_fields())


def delete_role():
    role_names = ["Hsms Manager", "Hsms User"]
    for role_name in role_names:
        if frappe.db.exists("Role", role_name):
            frappe.delete_doc("Role", role_name)

def delete_custom_fields(custom_fields):
	for doctype, fields in custom_fields.items():
		for field in fields:
			custom_field_name = frappe.db.get_value(
				"Custom Field", dict(dt=doctype, fieldname=field.get("fieldname"))
			)
			if custom_field_name:
				frappe.delete_doc("Custom Field", custom_field_name)

		frappe.clear_cache(doctype=doctype)

def add_roles_on_install():
    role_names = ["Hsms Manager", "Hsms User"]
    for role_name in role_names:
        if not frappe.db.exists("Role", role_name):
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
            })
            role.insert()

def get_custom_fields():
    custom_fields_company = [
        {
            "label": "Housting Settings",
            "fieldname": "housting_settings",
            "fieldtype": "Section Break",
            "insert_after": "exception_budget_approver_role"
        },
        {
            "label": "Default NOC Revenue Account",
            "fieldname": "default_noc_revenue_account",
            "fieldtype": "Link",
            "options": "Account",
            "insert_after": "housting_settings",
        },
        {
            "label": "Default Transfer Revenue Account",
            "fieldname": "default_transfer_revenue_account",
            "fieldtype": "Link",
            "options": "Account",
            "insert_after": "default_noc_revenue_account",
        },
        {
            "fieldname": "col_break_real_estate",
            "fieldtype": "Column Break",
            "insert_after": "default_transfer_revenue_account",
        },
        {
            "label": "Default Letter Issuance Account",
            "fieldname": "default_letter_issuance_account",
            "fieldtype": "Link",
            "options": "Account",
            "insert_after": "col_break_real_estate",
        },
        {
            "label": "Default Cost Center",
            "fieldname": "real_estate_cost_center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "insert_after": "default_letter_issuance_account",
        },
    ]
    custom_fields_customer = [
        {
            "label": "Father Name",
            "fieldname": "father_name",
            "fieldtype": "Data",
            "insert_after": "territory",
			"allow_in_quick_entry":1,
			"no_copy":1,
        },
		{
            "label": "ID Card No",
            "fieldname": "id_card_no",
            "fieldtype": "Data",
            "allow_in_quick_entry":1,
            "insert_after": "father_name",
			"reqd":1,
			"no_copy":1,
        },
        {
            "label": "Member Type",
            "fieldname": "member_type",
            "fieldtype": "Select",
            "options": "\nOrginal Member \nAssociate Member",
            "allow_in_quick_entry":1,
            "insert_after": "id_card_no",
			"reqd":1,
			"no_copy":1,
        }

    ]
    custom_fields_Journal_Entry = [
        {
            "label": "Document Type",
            "fieldname": "document_type",
            "fieldtype": "Link",
			"options": "DocType",
			"read_only":1,
			"no_copy":1,
            "insert_after": "cheque_date",
        },
		
		{
            "label": "Document Number",
            "fieldname": "document_number",
            "fieldtype": "Dynamic Link",
			"options": "document_type",
			"read_only":1,
			"no_copy":1,
            "insert_after": "document_type",
        },
		{
            "label": "Property Number",
            "fieldname": "property_number",
            "fieldtype": "Link",
			"options": "Inventory Master Data",
			"read_only":1,
			"no_copy":1,
            "insert_after": "document_number",
        }

    ]
    custom_fields_Journal_Entry_account = [
        {
            "label": "Document Type",
            "fieldname": "document_type",
            "fieldtype": "Link",
			"options": "DocType",
			"read_only":1,
			"no_copy":1,
            "insert_after": "cheque_date",
        },
		{
            "label": "Document Number",
            "fieldname": "document_number",
            "fieldtype": "Dynamic Link",
			"options": "document_type",
			"read_only":1,
			"no_copy":1,
            "insert_after": "document_type",
        },
		{
            "label": "Property Number",
            "fieldname": "property_number",
            "fieldtype": "Link",
			"options": "Inventory Master Data",
			"read_only":1,
			"no_copy":1,
            "insert_after": "document_number",
        }
    ]
	
    return {
        "Company": custom_fields_company,
        "Customer": custom_fields_customer,
		"Journal Entry": custom_fields_Journal_Entry,
		"Journal Entry Account" : custom_fields_Journal_Entry_account,
    }

