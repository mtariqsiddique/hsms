import frappe
    
def autoname_payment_entry(doc, method=None):
    if not doc.posting_date:
        frappe.throw("Posting Date is required for naming")

    try:
        if doc.payment_type in ("Pay", "Internal Transfer") :
            doc.name = generate_payment_number(doc.posting_date)
        elif doc.payment_type == "Receive":
            doc.name = generate_receive_number(doc.posting_date)
    except frappe.DuplicateEntryError:
        # Retry with new number if duplicate occurs
        frappe.db.rollback()
        if doc.payment_type in ("Pay", "Internal Transfer") :
            doc.name = generate_payment_number(doc.posting_date, retry=True)
        elif doc.payment_type == "Receive":
            doc.name = generate_receive_number(doc.posting_date, retry=True)

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

