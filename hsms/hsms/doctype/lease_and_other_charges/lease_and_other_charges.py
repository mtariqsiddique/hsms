# Copyright (c) 2024, Tariq Siddique and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from hsms.controllers.hsms_controller import HSMS_Controller, validate_accounting_period_open

class LeaseAndOtherCharges(HSMS_Controller):
    def validate(self):
        self.validate_posting_date()
        validate_accounting_period_open(self)
        self.validate_noc_type()
        self.validate_account_and_net_amount()
        
    def on_submit(self):
        self.make_gl_entries()
        
    def validate_noc_type(self):
            noc_types = []
            for row in self.laoc_item:
                payment_type = row.description
                if payment_type in noc_types:
                    frappe.throw(_("Description '{0}' occurs more than once").format(payment_type))
                else:
                    noc_types.append(payment_type)

    def validate_account_and_net_amount(self):
        for row in self.laoc_item:
            if row.account is None:
                frappe.throw(_("Account is mandatory for row '{0}'").format(row.description))
            if row.net_amount <=0:
                frappe.throw(_("Net Amount not less then zero '{0}'").format(row.description))

    def make_gl_entries(self):
        if self.net_amount != 0:
            company = frappe.get_doc("Company", self.company)
            default_receivable_account = frappe.get_value("Company", company, "default_receivable_account")
           
            if not default_receivable_account:
                frappe.throw('Please set Default Receivable Account in Company Settings')
            
            cost_center = frappe.get_value("Company", self.company, "real_estate_cost_center")
            if not cost_center:
                frappe.throw('Please set Cost Centre in Company Settings')

            journal_entry = frappe.get_doc({
                    "doctype": "Journal Entry",
                    "voucher_type": "Journal Entry",
                    "voucher_no": self.name,
                    "posting_date": self.posting_date,
                    "user_remark": self.remarks,
                    "document_number": self.name,
                    "document_type": "Lease And Other Charges",
                    "property_number": self.property_number
                })
                
            journal_entry.append("accounts", {
                        "account": default_receivable_account,
                        "party_type": "Customer",
                        "party": self.customer,
                        "debit_in_account_currency": self.net_amount,
                        "property_number": self.property_number, 
                        "cost_center": "",
                        "is_advance": 0,
                        "document_number": self.name,
                        "document_type": "Lease And Other Charges"
                    })
            for item in self.laoc_item:     
                journal_entry.append("accounts", {
                            "account": item.account,
                            "credit_in_account_currency": item.net_amount,
                            "against": default_receivable_account,
                            "property_number": self.property_number,
                            "cost_center": cost_center,
                            "is_advance": 0,
                            "document_number": self.name,
                            "document_type": "Lease And Other Charges"
                        })

            journal_entry.insert(ignore_permissions=True)
            journal_entry.submit()

            frappe.db.commit()
            frappe.msgprint(_('Journal Entry {0} created successfully').format(frappe.get_desk_link("Journal Entry", journal_entry.name)))
	