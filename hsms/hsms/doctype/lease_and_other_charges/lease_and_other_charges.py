# Copyright (c) 2024, Tariq Siddique and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils import add_days

from hsms.controllers.hsms_controller import HSMS_Controller, validate_accounting_period_open

class LeaseAndOtherCharges(HSMS_Controller):
    def validate(self):
        self.validate_posting_date()
        validate_accounting_period_open(self)
        self.validate_noc_type()
        self.validate_account_and_net_amount()
        
    def on_submit(self):
        self.make_sales_invoice()
        
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

    def make_sales_invoice(self):
        if self.net_amount != 0:
            company = frappe.get_doc("Company", self.company)
            default_receivable_account = frappe.get_value("Company", company, "default_receivable_account")
        
            if not default_receivable_account:
                frappe.throw('Please set Default Receivable Account in Company Settings')
            
            cost_center = frappe.get_value("Company", self.company, "real_estate_cost_center")
            if not cost_center:
                frappe.throw('Please set Cost Centre in Company Settings')
            
            due_date = add_days(self.posting_date, 2)

            sales_invoice = frappe.get_doc({
                    "doctype": "Sales Invoice",
                    "customer": self.customer,
                    "company": self.company,
                    "posting_date": self.posting_date,
                    "due_date": due_date,
                    "set_posting_time":1,
                    "remarks": self.remarks,
                    "cost_center": cost_center,
                    "document_number": self.name,
                    "document_type": "Lease And Other Charges",
                    "property_number": self.property_number,
                    "debit_to": default_receivable_account
                })
                
            for item in self.laoc_item:
                sales_invoice.append("items", {
                        "item_name": item.description,
                        "qty": 1,
                        "rate": item.net_amount,
                        "income_account": item.account,
                        "cost_center": cost_center,
                        "document_number": self.name,
                        "document_type": "Lease And Other Charges",
                        "property_number": self.property_number,
                    })

            sales_invoice.insert(ignore_permissions=True)
            sales_invoice.submit()

            frappe.db.commit()
            frappe.msgprint(_('Sales Invoice {0} created successfully').format(
                frappe.get_desk_link("Sales Invoice", sales_invoice.name)))