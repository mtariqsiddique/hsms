import frappe
from frappe import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from frappe.model.document import Document
from frappe.utils import flt, getdate, today

class ClosedAccountingPeriod(frappe.ValidationError):
    pass

class RealEstateController(Document):
    @frappe.whitelist()
    def generate_installment(self):
        self.validate_payment_plan()

    def validate_payment_plan(self):
        if not self.payment_plan:
            frappe.throw(_('Please set payment plan'))
        for plan in self.payment_plan:
            if not plan.get('plan_type'):
                frappe.throw(_('Plan type is required for each installment'))
            if not plan.get('start_date'):
                frappe.throw(_('Start date is required for each installment'))
            if not plan.get('end_date'):
                frappe.throw(_('End date is required for each installment'))
            if not plan.get('installment_amount') or flt(plan.get('installment_amount')) <= 0:
                frappe.throw(_('Valid installment amount is required for each installment'))

    def validate_posting_date(self):
        if self.posting_date:
            posting_date = getdate(self.posting_date)
            today_date = today()
        if posting_date and posting_date > getdate(today_date):
            frappe.throw("Future Document date not Allowed.")

    def validate_amount(self):
        if flt(self.difference) != 0.0:
            frappe.throw(_('Amount of Total Payment Schedule and Total Sales Amout is not matched'))

    def Check_customer_plot_master_data(self):
        if self.customer:
            customer = frappe.get_value('Plot List', {'name': self.plot_no}, 'customer')
            if customer != self.customer:
                frappe.msgprint('The master data customer does not match the payment customer')
                frappe.throw('Validation Error: Customer mismatch')



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
