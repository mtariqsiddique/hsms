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
    if not doc.posting_date:
        frappe.throw("Posting Date is required for naming")

    if doc.doc_type in ("Payment Entry", "Receive Entry"):
        doc.name = generate_payment_receive_number(doc.doc_type, doc.posting_date)
    
    else:
        doc.name = generate_journal_number(doc.posting_date)

def generate_journal_number(posting_date):
    """Generate monthly journal number"""
    post_date = getdate(posting_date)
    month_code = post_date.strftime("%y%m")
    prefix = f"JE-{month_code}-"
    
    current_max = get_max_sequence_number(prefix)

    return f"{prefix}{current_max:05d}"

def generate_payment_receive_number(document_type, posting_date):
    if document_type == "Payment Entry":
        prefix = "Pay-"
    elif document_type == "Receive Entry":
        prefix = "Rec-"

    fiscal_year = get_fiscal_year(posting_date)
    full_prefix = f"{prefix}{fiscal_year}-"

    # Get max number from both tables
    max_number = get_max_sequence_number(full_prefix)
    
    return  f"{full_prefix}{max_number:05d}"
     
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