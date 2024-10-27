import frappe
from frappe.utils import getdate

def execute(filters=None):
    columns = [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Rept. No.", "fieldname": "receipt_number", "fieldtype": "Data", "width": 80},
        {"label": "Document Type", "fieldname": "doctype", "fieldtype": "Data", "width": 200}, 
        {"label": "Document Name", "fieldname": "name", "fieldtype": "Dynamic Link", "options": "doctype", "width": 150},
        {"label": "Customer", "fieldname": "customer_code", "fieldtype": "Link", "options": "Customer", "width": 120},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 250},
        {"label": "Property No.", "fieldname": "property_number", "fieldtype": "Link", "options": "Inventory Master Data", "width": 80},
        {"label": "Transaction Type", "fieldname": "transaction_type", "fieldtype": "Data", "width": 200},
        {"label": "Net Amount", "fieldname": "net_amount", "fieldtype": "Currency", "width": 150},
    ]

    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    doctype_filter = filters.get("doctype")

    data = []

    def fetch_records(doc_type, child_table, fields, doctype_name_field, parent_customer_field, parent_customer_code, filter_field="posting_date"):
        records = []
        parent_fields = ["name", "posting_date", parent_customer_field, parent_customer_code, "property_number"]
        
        if frappe.get_meta(doc_type).has_field("receipt_number"):
            parent_fields.append("receipt_number")

        conditions = [
            [doc_type, "docstatus", "=", 1],
            [doc_type, filter_field, ">=", from_date],
            [doc_type, filter_field, "<=", to_date]
        ]
        parent_docs = frappe.get_all(doc_type, filters=conditions, fields=parent_fields)

        for parent in parent_docs:
            child_docs = frappe.get_all(child_table, filters={"parent": parent.name}, fields=fields)
            for child in child_docs:
                record = {
                    "posting_date": parent.posting_date,
                    "receipt_number": parent.get("receipt_number"),  
                    "customer_name": parent.get(parent_customer_field),
                    "customer_code": parent.get(parent_customer_code),
                    "property_number": parent.property_number,
                    "transaction_type": child.get(doctype_name_field),
                    "net_amount": child.net_amount,
                    "name": parent.name,
                    "doctype": doc_type
                }
                records.append(record)
        return records

    if not doctype_filter or doctype_filter == "Member NOC":
        data.extend(fetch_records("Member NOC", "Member NOC Item", ["noc_type", "net_amount"], "noc_type", "customer_name", "customer"))

    if not doctype_filter or doctype_filter == "Property Transfer":
        data.extend(fetch_records("Property Transfer", "Property Transfer Item", ["transfer_type", "net_amount"], "transfer_type", "to_customer_name", "to_customer"))

    if not doctype_filter or doctype_filter == "Lease And Other Charges":
        data.extend(fetch_records("Lease And Other Charges", "Lease And Other Charge Item", ["description", "net_amount"], "description", "customer_name", "customer"))

    # Sort the data by `posting_date`
    data = sorted(data, key=lambda x: x["posting_date"])

    return columns, data
