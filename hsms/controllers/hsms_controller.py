import frappe
from frappe import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from frappe.model.document import Document
from frappe.utils import flt, getdate, today

class ClosedAccountingPeriod(frappe.ValidationError):
    pass

class HSMS_Controller(Document):
    def validate(self):
        self.validate_posting_date()
        
    def validate_posting_date(self):
        if self.posting_date:
            posting_date = getdate(self.posting_date)
            today_date = today()
        if posting_date and posting_date > getdate(today_date):
            frappe.throw("Future Document date not Allowed.")


def validate_accounting_period_open(doc, method=None):
    ap = frappe.qb.DocType("Accounting Period")
    cd = frappe.qb.DocType("Closed Document")
    accounting_period = (
        frappe.qb.from_(ap)
        .from_(cd)
        .select(ap.name)
        .where(
            (ap.name == cd.parent)
            & (ap.company == doc.company)
            & (cd.closed == 1)
            & (cd.document_type == doc.doctype)
            & (doc.posting_date >= ap.start_date)
            & (doc.posting_date <= ap.end_date)
        )
    ).run(as_dict=1)

    if accounting_period:
        frappe.throw(_("You cannot create a {0} within the closed Accounting Period {1}").format(
            doc.doctype, frappe.bold(accounting_period[0]["name"]),
            ClosedAccountingPeriod
        ))
