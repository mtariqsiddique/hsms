// Copyright (c) 2024, Tariq Siddique and contributors
// For license information, please see license.txt

frappe.query_reports["Revenue Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "doctype",
            "label": __("Document Type"),
            "fieldtype": "Select",
            "options": ["", "Member NOC", "Property Transfer", "Lease And Other Charges"],
            "default": "Property Transfer"
        }
    ],

    // Query report based on the filters selected
    "onload": function(report) {
        report.page.add_inner_button(__("Apply Filters"), function() {
            report.refresh();  // Refreshes report with filter values
        });
    }
};
