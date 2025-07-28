import frappe
from frappe import _
from frappe.utils import get_link_to_form

def before_cancel(doc, method=None):
    validate_parent_document_cancellation(doc)

def validate_parent_document_cancellation(doc):
    if not (doc.document_type and doc.document_number):
        return
    
    parent = frappe.get_doc(doc.document_type, doc.document_number)
    
    if parent.docstatus == 2:
        return
        
    if parent.docstatus != 1:
        frappe.throw(_(
            "Parent document {0} must be submitted before it can be cancelled."
        ).format(get_link_to_form(parent.doctype, parent.name)))
        
    if hasattr(parent, 'on_cancel'):
        try:
            parent.run_method('validate_cancel')
        except Exception as e:
            frappe.throw(_(
                "Cannot cancel because parent document {0} has restrictions: {1}"
            ).format(
                get_link_to_form(parent.doctype, parent.name),
                str(e)
            ))

def on_cancel(doc, method=None):
    """Cancel the parent document when sales invoice is cancelled"""
    if not (doc.document_type and doc.document_number):
        return
        
    parent = frappe.get_doc(doc.document_type, doc.document_number)
    if parent.docstatus == 1:
        try:
            parent.cancel()
            frappe.msgprint(_(
                "Parent document {0} has been cancelled automatically."
            ).format(get_link_to_form(parent.doctype, parent.name)))
        except Exception as e:
            frappe.throw(_(
                "Failed to cancel parent document {0}: {1}"
            ).format(
                get_link_to_form(parent.doctype, parent.name),
                str(e)
            ))

def autoname_sales_invoice(doc, method=None):
    if not doc.posting_date:
        frappe.throw("Posting Date is required for naming")

    fiscal_year = get_fiscal_year(doc.posting_date)
    prefix = f"SINV-{fiscal_year}-"
    
    last_invoice = frappe.db.sql("""
        SELECT name FROM `tabSales Invoice`
        WHERE name LIKE %s
        ORDER BY creation DESC
        LIMIT 1
    """, prefix + "%")
    
    if last_invoice:
        last_num = int(last_invoice[0][0].split("-")[-1])
        next_num = last_num + 1
    else:
        next_num = 1
    
    doc.name = f"{prefix}{next_num:05d}"

def get_fiscal_year(posting_date):
    fiscal = frappe.get_value("Fiscal Year", {
        "year_start_date": ("<=", posting_date),
        "year_end_date": (">=", posting_date)
    }, "fiscal_year_short_name")
    
    if not fiscal:
        frappe.throw(f"No active Fiscal Year found for date {posting_date}")
    
    return fiscal

