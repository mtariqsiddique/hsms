# Copyright (c) 2024, Tariq Siddique and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from hsms.controllers.hsms_controller import HSMS_Controller, validate_accounting_period_open

class LetterIssuance(HSMS_Controller):
    def validate(self):
        self.validate_posting_date()
        validate_accounting_period_open(self)
        self.validate_net_amount()
        
    def on_submit(self):
        self.make_gl_entries()
              
    def validate_net_amount(self):
            if self.net_amount <=0: 
                   frappe.throw(_("Net Amount not less then zero "))

    def make_gl_entries(self):
        if self.net_amount != 0:
            company = frappe.get_doc("Company", self.company)
            default_receivable_account = frappe.get_value("Company", company, "default_receivable_account")
            letter_issuance_account = frappe.get_value("Company", self.company, "default_letter_issuance_account")
            if not default_receivable_account:
                frappe.throw('Please set Default Receivable Account in Company Settings')
            if not letter_issuance_account:
                frappe.throw('Please set Default Letter Issuance Account in Company Settings')
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
                    "document_type": "Letter Issuance",
                    "property_number": self.property_number
                })
                
            journal_entry.append("accounts", {
                        "account": default_receivable_account,
                        "party_type": "Customer",
                        "party": self.member_name,
                        "debit_in_account_currency": self.net_amount,
                        "property_number": self.property_number, 
                        "cost_center": "",
                        "is_advance": 0,
                        "document_number": self.name,
                        "document_type": "Letter Issuance"
                    })
            journal_entry.append("accounts", {
                        "account": letter_issuance_account,
                        "credit_in_account_currency": self.net_amount,
                        "against": default_receivable_account,
                        "property_number": self.property_number,
                        "cost_center": cost_center,
                        "is_advance": 0,
                        "document_number": self.name,
                        "document_type": "Letter Issuance"
                    })

            journal_entry.insert(ignore_permissions=True)
            journal_entry.submit()

            frappe.db.commit()
            frappe.msgprint(_('Journal Entry {0} created successfully').format(frappe.get_desk_link("Journal Entry", journal_entry.name)))

	
	
	
	


    

	
	