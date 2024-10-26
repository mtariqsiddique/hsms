// Copyright (c) 2024, Tariq Siddique and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lease And Other Charges", {
	refresh(frm) {

	},
});


frappe.ui.form.on("Lease And Other Charge Item", {
    gross_amount: function(frm, cdt, cdn) {
        calc_net_amount(frm, cdt, cdn)
        calc_total_amount(frm);
    },
    discount: function(frm, cdt, cdn) {
        calc_discount_net_amount(frm, cdt, cdn)
        calc_total_amount(frm);
    },
    description: function(frm, cdt, cdn) {
        get_account_code(frm, cdt, cdn);
    },

    laoc_item_remove: function(frm, cdt, cdn) {
        calc_total_amount(frm);
    },
    laoc_item_clear_table: function(frm, cdt, cdn) {
        frm.set_value('gross_amount', 0.0);
        frm.set_value('discount', 0.0);
        frm.set_value('net_amount', 0.0);
    }
});

function get_account_code(frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    
    if (child.description === "Lease Charges") {
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Company",
                fieldname: "default_lease_account",
                filters: {
                    name: frm.doc.company
                }
            },
            callback: function(r) {
                if (r.message) {
                    frappe.model.set_value(cdt, cdn, "account", r.message.default_lease_account);
                }
            }
        });
    } else {
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Company",
                fieldname: "default_letter_issuance_account",
                filters: {
                    name: frm.doc.company 
                }
            },
            callback: function(r) {
                if (r.message) {
                    frappe.model.set_value(cdt, cdn, "account", r.message.default_letter_issuance_account);
                }
            }
        });
    }
}


function calc_total_amount(frm) {
    let grossTotal = 0;
    let discount = 0;
    let netTotal = 0;

    frm.doc.laoc_item.forEach(d => {
        grossTotal += flt(d.gross_amount);
        discount += flt(d.discount);
        netTotal += flt(d.net_amount);
    });

    frm.set_value('gross_amount', grossTotal);
    frm.set_value('discount', discount);
    frm.set_value('net_amount', netTotal);
}

function calc_discount_net_amount(frm, cdt, cdn) {    
    let row = locals[cdt][cdn];
    let netAmount = row.gross_amount - row.discount;

    if (row.discount < 0) {
        frappe.model.set_value(cdt, cdn, 'discount', 0.0);
        frappe.msgprint("Discount cannot be less than Zero");
    } else if (netAmount <= 0) {
        if (!row.netAmountMsg) {
            frappe.msgprint("Net Amount cannot be less than or equal to Zero");
            row.netAmountMsg = true;
        }
        frappe.model.set_value(cdt, cdn, 'gross_amount', 0.0);
        frappe.model.set_value(cdt, cdn, 'discount', 0.0);
        frappe.model.set_value(cdt, cdn, 'net_amount', 0.0);
    } else {
        frappe.model.set_value(cdt, cdn, 'net_amount', netAmount);
    }
}

function calc_net_amount(frm, cdt, cdn) {    
    let row = locals[cdt][cdn];
    let netAmount = row.gross_amount - row.discount;
        frappe.model.set_value(cdt, cdn, 'net_amount', netAmount);
}