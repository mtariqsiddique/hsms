# # Copyright (c) 2024, Tariq Siddique and contributors
# # For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cstr, add_days

from hsms.controllers.hsms_controller import HSMS_Controller, validate_accounting_period_open

class PropertyTransfer(HSMS_Controller):
    def validate(self):
        self.validate_posting_date()
        validate_accounting_period_open(self)
        self.validate_from_customer_and_to_customer()
        self.validate_check_customer_master_data_transfer()
        self.validate_transfer_type()
        self.validate_transfer_table()

    def on_submit(self):
        self.make_gl_entries()
        self.update_property_master()

    def on_cancel(self):
        self.update_inventory_master_cancel()
        
    def validate_from_customer_and_to_customer(self):
        to_customer = [row.customer for row in self.to_customer_partnership]
        from_customer = {row.customer for row in self.from_customer_partnership}
        if self.from_customer == self.to_customer:
            frappe.throw('From Customer and To Customer must be different')
        if self.from_customer in to_customer:
            frappe.throw(_('From Customer and To Customer must be different'))
        for row in self.to_customer_partnership:
            if row.customer in from_customer:
                frappe.throw(_("Duplicate customer found in from customer and to Customer: {0}").format(row.customer))
                
    def validate_check_customer_master_data_transfer(self):
                pass
    #     if self.from_customer:
    #         customer = frappe.get_value('Plot List', {'name': self.plot_no}, 'customer')
    #         if customer != self.from_customer:
    #             frappe.throw('The master data customer does not match the payment customer')

    def validate_transfer_type(self):
        payment_types = []
        for row in self.transfer:
            payment_type = row.transfer_type
            if payment_type in payment_types:
                frappe.throw(_("Payment Type '{0}' occurs more than once").format(payment_type))
            else:
                payment_types.append(payment_type)

    def validate_transfer_table(self):
         for row in self.transfer:
              if row.net_amount <=0:
                   frappe.throw(_("Payment Type '{0}' not less then zero ").format(row.transfer_type))

    def validate_share_percentage(self):
        if self.to_customer_type == "Individual":
            if flt(self.to_share_percentage) != 100.0:
                frappe.throw(_('The Individual customer share percentage must be equal to 100. Current total: {0:.2f}').format(self.to_share_percentage))
            rows = len([row.customer for row in self.to_customer_partnership])
            if rows > 0:
                frappe.throw(_('Remove the rows in the customer partnership table.'))
        
        elif self.to_customer_type == "Partnership":
            share_percentage = flt(self.to_share_percentage) + flt(sum(row.share_percentage for row in self.to_customer_partnership))
            
            if flt(share_percentage) != 100.0:
                frappe.throw(_('The Partnership customers share percentage must be equal to 100. Current total: {0:.2f}').format(share_percentage))
            if any(row.share_percentage == 0.0 for row in self.to_customer_partnership):
                frappe.throw(_('Share percentage for Partnership customers cannot be 0.0'))
            if flt(self.to_share_percentage) == 0.0:
                frappe.throw(_('Share percentage for Main customers cannot be 0.0'))

    def validate_duplicates_customer_in_partnership(self):
        partnership_customer = [row.customer for row in self.to_customer_partnership]
        duplicates_in_partnership = [x for x in partnership_customer if partnership_customer.count(x) > 1]
        
        if duplicates_in_partnership:
            duplicate_customers = ', '.join(set(duplicates_in_partnership))
            frappe.throw(_('Duplicate customers found in the to customer partnership table: {0}').format(duplicate_customers))
        
        if self.to_customer and self.to_customer in partnership_customer:
            frappe.throw(_('Duplicate customer found in the to customer partnership table: {0}').format(self.to_customer))

    def make_gl_entries(self):
        if self.net_transfer_amount != 0:
            company = frappe.get_doc("Company", self.company)
            default_receivable_account = frappe.get_value("Company", company, "default_receivable_account")
            transfer_account = frappe.get_value("Company", self.company, "default_transfer_revenue_account")
            
            if not default_receivable_account:
                frappe.throw('Please set Default Receivable Account in Company Settings')
            if not transfer_account:
                frappe.throw('Please set Default Transfer Revenue Account in Company Settings')
                
            cost_center = frappe.get_value("Company", self.company, "real_estate_cost_center")
            if not cost_center:
                frappe.throw('Please set Cost Centre in Company Settings')
                
            due_date = add_days(self.posting_date, 2)

            sales_invoice = frappe.get_doc({
                "doctype": "Sales Invoice",
                "customer": self.to_customer,
                "company": self.company,
                "posting_date": self.posting_date,
                "due_date": due_date,
                "set_posting_time": 1,
                "remarks": self.remarks,
                "cost_center": cost_center,
                "document_number": self.name,
                "document_type": "Property Transfer",
                "property_number": self.property_number,
                "debit_to": default_receivable_account
            })
            
            for item in self.noc_item:
                sales_invoice.append("items", {
                    "item_name": item.noc_type,
                    "qty": 1,
                    "rate": item.net_amount,
                    "income_account": transfer_account,
                    "cost_center": cost_center,
                    "document_number": self.name,
                    "document_type": "Property Transfer",
                    "property_number": self.property_number,
                })
                    
            sales_invoice.append("payment_schedule", {
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
                
    def update_property_master(self):
            inventory_master = frappe.get_doc("Inventory Master Data", self.property_number)    
            inventory_master.update({
                        'customer': self.to_customer, 'customer_name': self.to_customer_name, 
                        'mobile_no': self.to_mobile_no, 'address': self.to_address,
                        'father_name': self.to_father_name, 'cnic': self.to_cnic,
                        'customer_type': self.to_customer_type,'share_percentage': self.to_share_percentage,
                        'document_type':"Property Transfer",'document_number': self.name,
                    })
        
            if self.to_customer_type == "Individual":
                inventory_master.set("customer_partnership", [])
            
            elif self.to_customer_type == "Partnership":
                for customer in self.to_customer_partnership:
                    inventory_master.append("customer_partnership", {
                    'customer': customer.customer,
                    'customer_name': customer.customer_name,
                    'address': customer.address,
                    'mobile_no': customer.mobile_no,
                    'father_name': customer.father_name,
                    'id_card_no': customer.id_card_no,
                    'share_percentage': customer.share_percentage,
            })
            inventory_master.save()
            frappe.msgprint(_('{0} successfully updated ').format(frappe.get_desk_link('Inventory Master Data', inventory_master.name)))                    
            
    def update_inventory_master_cancel(self):   
            inventory_master = frappe.get_doc('Inventory Master Data', self.property_number)
            inventory_master.update({
                                'customer': self.from_customer, 'customer_name': self.from_customer_name, 
                                'mobile_no': self.from_mobile_no, 'address': self.from_address, 
                                'father_name': self.from_father_name, 'cnic': self.from_cnic,
                                'customer_type': self.from_customer_type,'share_percentage': self.from_share_percentage,
                                'document_type' :self.from_document_type, 'document_number':self.from_document_number,
                            })
            
            if self.from_customer_type == "Individual":
                inventory_master.set("customer_partnership", [])

            elif self.from_customer_type == "Partnership":
                for customer in self.from_customer_partnership:
                    inventory_master.append("customer_partnership", {
                    'customer': customer.customer,
                    'customer_name': customer.customer_name,
                    'address': customer.address,
                    'mobile_no': customer.mobile_no,
                    'father_name': customer.father_name,
                    'id_card_no': customer.id_card_no,
                    'share_percentage': customer.share_percentage,                    
            })
            inventory_master.save()
            frappe.msgprint(_('{0} successfully updated').format(frappe.get_desk_link('Inventory Master Data', inventory_master.name)))    


@frappe.whitelist()
def get_customer_partnership(inv_master_data):      
    data = []
    pb_data = frappe.get_doc("Inventory Master Data", inv_master_data)
    for item in pb_data.get("customer_partnership"):
        data.append({
            "name": item.get('name'),
            "customer": item.get("customer"),
            "customer_name": item.get("customer_name"),
            "share_percentage": item.get("share_percentage"),
            "father_name": item.get("father_name"),
            "id_card_no": item.get("id_card_no"),
            "mobile_no": item.get("mobile_no"),
            "address": item.get("address"),
        })
    return data
