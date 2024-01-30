import frappe
from frappe import _

def check_plot_booking(doc, method=None):
    pass
    # if doc.get('document_type') == 'Cancellation Property' and doc.get('document_number'):
    #     cacellation_propertry = frappe.get_doc('Cancellation Property', doc.get('document_number'))
    #     if frappe.db.exists('Plot List', {'name': cacellation_propertry.plot_no, 'status':  ["in", ["Booked", "Token"]]}):
    #         frappe.throw('Plot not avaliable for booking')

def check_document_status(doc, method=None):
    pass
    # if doc.get('document_type') == 'Customer Payment' and doc.get('document_number'):
    #     cust_pmt = frappe.get_doc('Customer Payment', doc.get('document_number'))
    #     doctype = cust_pmt.document_type
    #     if cust_pmt.document_number and not frappe.db.exists(doctype, {'name': cust_pmt.document_number, 'status': 'Active'}):  
    #         frappe.throw(_('The {0} is not Active').format(frappe.get_desk_link(doctype, cust_pmt.document_number)))

  
