import frappe
from frappe.utils import getdate

def autoname_payment_entry(doc, method=None):
    if not doc.posting_date:
        frappe.throw("Posting Date is required for naming")

    # Determine prefix
    if doc.doctype == "Payment Entry":
        prefix = "Rec-" if doc.payment_type == "Receive" else "Pay-"
    else: 
        prefix = "Pay-" 

    fiscal_year = get_fiscal_year(doc.posting_date)
    full_prefix = f"{prefix}{fiscal_year}-"

    max_number = get_max_sequence_number(full_prefix)

    doc.name = f"{full_prefix}{max_number:05d}"

def get_max_sequence_number(prefix):
    """Get max sequence number from both Payment Entry and Journal Entry"""
    # Query Payment Entry table
    pe_max = frappe.db.sql("""
        SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(name, '-', -1) AS UNSIGNED)), 0)
        FROM `tabPayment Entry`
        WHERE name LIKE %s
    """, f"{prefix}%")[0][0]

    # Query Journal Entry table
    je_max = frappe.db.sql("""
        SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(name, '-', -1) AS UNSIGNED)), 0)
        FROM `tabJournal Entry`
        WHERE name LIKE %s
    """, f"{prefix}%")[0][0]

    return max(int(pe_max), int(je_max)) + 1

def get_fiscal_year(posting_date):
    """Get fiscal year short code (2526 for 2025-2026)"""
    fiscal = frappe.get_value("Fiscal Year", {
        "year_start_date": ("<=", posting_date),
        "year_end_date": (">=", posting_date)
    }, ["fiscal_year_short_name", "year_start_date", "year_end_date"], as_dict=True)
    
    if not fiscal:
        frappe.throw(_("No active Fiscal Year found for date {0}").format(posting_date))
    
    return fiscal.fiscal_year_short_name or (
        f"{fiscal.year_start_date.year % 100:02d}"
        f"{fiscal.year_end_date.year % 100:02d}"
    )
