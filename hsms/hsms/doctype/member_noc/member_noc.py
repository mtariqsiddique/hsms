# Copyright (c) 2024, Tariq Siddique and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days
from hsms.controllers.hsms_controller import HSMS_Controller, validate_accounting_period_open

class MemberNOC(HSMS_Controller):
    def validate(self):
        self.validate_posting_date()
        validate_accounting_period_open(self)
        self.validate_noc_type()
        self.validate_net_amount()
        
    def on_submit(self):
        self.make_sales_invoice()
        
    def validate_noc_type(self):
            noc_types = []
            for row in self.noc_item:
                payment_type = row.noc_type
                if payment_type in noc_types:
                    frappe.throw(_("Payment Type '{0}' occurs more than once").format(payment_type))
                else:
                    noc_types.append(payment_type)
        
    def validate_net_amount(self):
        for row in self.noc_item:
            if row.net_amount <=0:
                frappe.throw(_("Net Amount not less then zero '{0}'").format(row.description))


    def make_sales_invoice(self):
        if self.net_amount != 0:
            company = frappe.get_doc("Company", self.company)
            default_receivable_account = frappe.get_value("Company", company, "default_receivable_account")
            noc_account = frappe.get_value("Company", self.company, "default_noc_revenue_account")
            
            if not default_receivable_account:
                frappe.throw('Please set Default Receivable Account in Company Settings')
            if not noc_account:
                frappe.throw('Please set Default NOC Account in Company Settings')
                
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
                    "document_type": "Member NOC",
                    "property_number": self.property_number,
                    "debit_to": default_receivable_account
                })
                
            for item in self.noc_item:
                sales_invoice.append("items", {
                        "item_name": item.noc_type,
                        "qty": 1,
                        "rate": item.net_amount,
                        "income_account": noc_account,
                        "cost_center": cost_center,
                        "document_number": self.name,
                        "document_type": "Member NOC",
                        "property_number": self.property_number,
                    })
                        
            sales_invoice.append("payment_schedule",{
                "due_date": due_date,
                "invoice_portion": 100,
                "payment_amount": self.net_amount
            })

            # Submit with validation disabled
            sales_invoice.insert(ignore_permissions=True)
            sales_invoice.submit()

            frappe.db.commit()
            frappe.msgprint(_('Sales Invoice {0} created successfully').format(
                frappe.get_desk_link("Sales Invoice", sales_invoice.name)))
            