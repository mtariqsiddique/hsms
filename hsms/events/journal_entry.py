import frappe
from frappe import _
from frappe.utils import getdate

def check_plot_booking(doc, method=None):
    pass
    # if doc.get('document_type') == 'Cancellation Property' and doc.get('document_number'):
    #     cacellation_propertry = frappe.get_doc('Cancellation Property', doc.get('document_number'))
    #     if frappe.db.exists('Plot List', {'name': cacellation_propertry.plot_no, 'status':  ["in", ["Booked", "Token"]]}):
    #         frappe.throw('Plot not avaliable for booking')

def check_document_status(doc, method=None):
    pass
    # if doc.get('document_type') == 'Customer Payment' and doc.get('document_number'):
    #     cust_pmt = frappe.get_doc('Customer Payment', doc.get('document_number'))
    #     doctype = cust_pmt.document_type
    #     if cust_pmt.document_number and not frappe.db.exists(doctype, {'name': cust_pmt.document_number, 'status': 'Active'}):  
    #         frappe.throw(_('The {0} is not Active').format(frappe.get_desk_link(doctype, cust_pmt.document_number)))

def update_entry_type(doc, method=None):
    if not doc.doc_type:
        frappe.throw("Document type is required for Entry")
    
    if doc.doc_type in ("Payment Entry", "Receive Entry"):
        doc.voucher_type = "Bank Entry"

def autoname_journal_entry(doc, method=None):
    """
    Final working solution that handles:
    - Payment Entry: Pay-2526-00001
    - Receive Entry: Rec-2526-00001 
    - Journal Entry: JE-2507-0001
    """
    if not doc.posting_date:
        frappe.throw("Posting Date is required for naming")

    try:
        if doc.doc_type == "Payment Entry":
            doc.name = generate_payment_number(doc.posting_date)
        elif doc.doc_type == "Receive Entry":
            doc.name = generate_receive_number(doc.posting_date)
        else:  # Journal Entry
            doc.name = generate_journal_number(doc.posting_date)
    except frappe.DuplicateEntryError:
        # Retry with new number if duplicate occurs
        frappe.db.rollback()
        if doc.doc_type == "Payment Entry":
            doc.name = generate_payment_number(doc.posting_date, retry=True)
        elif doc.doc_type == "Receive Entry":
            doc.name = generate_receive_number(doc.posting_date, retry=True)
        else:
            doc.name = generate_journal_number(doc.posting_date, retry=True)

def generate_payment_number(posting_date, retry=False):
    """Generate payment number with fiscal year"""
    fiscal_short = get_fiscal_short_name(posting_date)
    prefix = f"Pay-{fiscal_short}-"
    
    if retry:
        current_max = get_current_max(prefix, "Payment Entry")
        next_num = current_max + 1
    else:
        next_num = get_next_series_number(prefix)
    
    return f"{prefix}{next_num:05d}"

def generate_receive_number(posting_date, retry=False):
    """Generate receive number with fiscal year"""
    fiscal_short = get_fiscal_short_name(posting_date)
    prefix = f"Rec-{fiscal_short}-"
    
    if retry:
        current_max = get_current_max(prefix, "Payment Entry")
        next_num = current_max + 1
    else:
        next_num = get_next_series_number(prefix)
    
    return f"{prefix}{next_num:05d}"

def generate_journal_number(posting_date, retry=False):
    """Generate monthly journal number"""
    post_date = getdate(posting_date)
    month_code = post_date.strftime("%y%m")
    prefix = f"JE-{month_code}-"
    
    if retry:
        current_max = get_current_max(prefix, "Journal Entry")
        next_num = current_max + 1
    else:
        next_num = get_next_series_number(prefix)
    
    return f"{prefix}{next_num:04d}"

def get_fiscal_short_name(posting_date):
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

def get_current_max(prefix, doctype):
    """Get current maximum number for prefix"""
    result = frappe.db.sql(f"""
        SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(name, '-', -1) AS UNSIGNED)), 0)
        FROM `tab{doctype}`
        WHERE name LIKE %s
    """, f"{prefix}%")
    return int(result[0][0]) if result else 0

def get_next_series_number(prefix):
    """Thread-safe next number generation"""
    try:
        frappe.db.sql("""
            INSERT INTO `tabSeries` (name, current)
            VALUES (%s, 1)
            ON DUPLICATE KEY UPDATE current = current + 1
        """, prefix)
        next_num = frappe.db.sql("SELECT current FROM `tabSeries` WHERE name = %s", prefix)[0][0]
        frappe.db.commit()
        return next_num
    except Exception:
        frappe.db.rollback()
        current_max = get_current_max(prefix, "Payment Entry")
        return current_max + 1

