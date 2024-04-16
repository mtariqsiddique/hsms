// Copyright (c) 2024, Tariq Siddique and contributors
// For license information, please see license.txt

frappe.ui.form.on("Property Transfer", {
    setup(frm) {
		frm.trigger("set_queries_inventory");
	},

	set_queries_inventory(frm) {
		frm.set_query("property_number", function(frm) {
            return {
                filters: {
                    'status': 'Allotted'
                }
            };
		});
	},
    property_number: function(frm) {
        frappe.call({
            method: 'hsms.hsms.doctype.property_transfer.property_transfer.get_customer_partnership',
            args: {
                inv_master_data: frm.doc.property_number,
            },
            callback: function(data) {
                console.log(data);
                if (data.message) {
                    frm.clear_table('from_customer_partnership');
                    for (let i = 0; i < data.message.length; i++) {
                        var row = frm.add_child('from_customer_partnership');
                        row.customer = data.message[i].customer;
                        row.customer_name = data.message[i].customer_name;
                        row.father_name = data.message[i].father_name;
                        row.id_card_no = data.message[i].id_card_no;
                        row.mobile_no = data.message[i].mobile_no;
                        row.address = data.message[i].address;
                        row.share_percentage = data.message[i].share_percentage;
                    }
                    frm.refresh_fields('from_customer_partnership');        
                } else {
                    frappe.msgprint(__('Error: ') + data.exc);
                }
            }
        });
    },
    
});

frappe.ui.form.on("Property Transfer Item", {
    gross_amount: function(frm, cdt, cdn) {
        calc_net_amount(frm, cdt, cdn)
        calc_total_transfer_amount(frm);
    },
    discount: function(frm, cdt, cdn) {
        calc_net_amount(frm, cdt, cdn)
        calc_total_transfer_amount(frm);
    },
    transfer_remove: function(frm, cdt, cdn) {
        calc_total_transfer_amount(frm);
    },
    transfer_clear_table: function(frm, cdt, cdn) {
        frm.set_value('gross_transfer_amount', 0.0);
        frm.set_value('discount', 0.0);
        frm.set_value('net_transfer_amount', 0.0);
    }
});

function calc_total_transfer_amount(frm) {
    let grossTotal = 0;
    let discount = 0;
    let netTotal = 0;

    frm.doc.transfer.forEach(d => {
        grossTotal += flt(d.gross_amount);
        discount += flt(d.discount);
        netTotal += flt(d.net_amount);
    });

    frm.set_value('gross_transfer_amount', grossTotal);
    frm.set_value('discount', discount);
    frm.set_value('net_transfer_amount', netTotal);
}

function calc_net_amount(frm, cdt, cdn) {    
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
