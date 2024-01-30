# Copyright (c) 2024, Tariq Siddique and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from hsms.controllers.hsms_controller import HSMS_Controller, validate_accounting_period_open

class PropertyAllotment(HSMS_Controller):
    def validate(self):
        self.validate_posting_date()
        validate_accounting_period_open(self)
        self.validate_plot_booking()
        self.validate_duplicates_customer_in_partnership()
        self.validate_share_percentage()

    def on_submit(self):
        self.book_plot()

    def on_cancel(self):
        self.unbook_plot()

    def validate_plot_booking(self):
        if not self.property_number:
            frappe.throw(_("Error: Plot number not specified in the document."))
        plot_status = frappe.db.get_value("Inventory Master Data", self.property_number, 'status')
        if plot_status == 'Booked':
            frappe.throw(_('The {0} is not avaliable').format(frappe.get_desk_link("Inventory Master Data", self.property_number)))

    def validate_share_percentage(self):
        if self.customer_type == "Individual":
            if flt(self.share_percentage) != 100.0:
                frappe.throw(_('The Individual customer share percentage must be equal to 100. Current total: {0:.2f}').format(self.share_percentage))
            rows = len([row.customer for row in self.customer_partnership])
            if rows > 0:
                frappe.throw(_('Remove the rows in the customer partnership table.'))
        
        elif self.customer_type == "Partnership":
            share_percentage = flt(self.share_percentage) + flt(sum(row.share_percentage for row in self.customer_partnership))
            
            if flt(share_percentage) != 100.0:
                frappe.throw(_('The Partnership customers share percentage must be equal to 100. Current total: {0:.2f}').format(share_percentage))
            if any(row.share_percentage == 0.0 for row in self.customer_partnership):
                frappe.throw(_('Share percentage for Partnership customers cannot be 0.0'))
            if flt(self.share_percentage) == 0.0:
                frappe.throw(_('Share percentage for Main customers cannot be 0.0'))

    def validate_duplicates_customer_in_partnership(self):
        partnership_customer = [row.customer for row in self.customer_partnership]
        duplicates_in_partnership = set(x for x in partnership_customer if partnership_customer.count(x) > 1)
        
        if duplicates_in_partnership:
            frappe.throw(_('Duplicate customer found in the customer partnership table: {0}').format(', '.join(duplicates_in_partnership)))
        
        if self.customer in partnership_customer:
            frappe.throw(_('Duplicate customer found in the customer partnership table.'))

    def book_plot(self):
        plot_master = frappe.get_doc("Inventory Master Data", self.property_number)
        
        if (plot_master.status == "Available"):
            plot_master.update({      
                'status'            : "Allotted",
                'customer'          : self.customer,
                'address'           : self.address,
                'contact_no'        : self.contact_no,
                'father_name'       : self.father_name,
                'cnic'              : self.cnic,
                'customer_type'     : self.customer_type,
                'share_percentage'  : self.share_percentage,
            })

            if self.customer_type == "Partnership":
                for customer in self.customer_partnership:
                    plot_master.append("customer_partnership", {
                    'customer': customer.customer,
                    'address': customer.address,
                    'mobile_no': customer.mobile_no,
                    'father_name': customer.father_name,
                    'id_card_no': customer.id_card_no,
                    'share_percentage': customer.share_percentage,
            })

            plot_master.save()
            frappe.msgprint(_('{0} booked successfully').format(frappe.get_desk_link('Inventory Master Data', plot_master.name)))
        else:
            frappe.throw(_("Error: The selected plot is not available for booking."))
        
    def unbook_plot(self):
        plot_master = frappe.get_doc("Inventory Master Data", self.property_number)
        if not self.token_number :
            plot_master.update({
                'status'            : "Available",
                'customer'          : '',
                'address'           : '',
                'contact_no'        : '',
                'sales_broker'      : '',
                'father_name'       : '',
                'cnic'              : '',
                'customer_type'     : '',
                'share_percentage'  : '',
            })

        if self.customer_type == "Partnership":
            plot_master.set("customer_partnership", [])

        if self.token_number :
            plot_master.update({
                'status'            : "Token",
                'customer'          : self.customer,
                'address'           : self.address,
                'contact_no'        : self.contact_no,
                'sales_broker'      : self.sales_broker,
                'father_name'       : self.father_name,
                'cnic'              : self.cnic,
                'customer_type'     : '',
                'share_percentage'  : '',
            })

            if self.customer_type == "Partnership":
                plot_master.set("customer_partnership", [])

        plot_master.save()
        frappe.msgprint(_('{0} unbooked').format(frappe.get_desk_link('Inventory Master Data', plot_master.name)))
        
