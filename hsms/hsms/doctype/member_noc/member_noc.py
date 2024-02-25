# Copyright (c) 2024, Tariq Siddique and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from hsms.controllers.hsms_controller import HSMS_Controller, validate_accounting_period_open

class MemberNOC(HSMS_Controller):
    def validate(self):
        self.validate_posting_date()
        validate_accounting_period_open(self)
        self.validate_transfer_type()
        self.validate_transfer_table()
        
    def on_submit(self):
        pass
        # self.make_gl_entries()
        

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
    
	
	
	
	
	


    

	
	