// Copyright (c) 2024, Tariq Siddique and contributors
// For license information, please see license.txt

frappe.ui.form.on("Property Transfer", {
    discount: function(frm) {
        calculate_net_amount(frm);
    },
    gross_transfer_amount: function(frm) {
        calculate_net_amount(frm);
    },

    // document_number : function(frm) {
    //     if(frm.doc.document_number) {
    //         frappe.call({
    //             method: 'realestate_account.controllers.real_estate_controller.get_customer_partner',
    //             args: {
    //                 document_number: frm.doc.document_number,
    //             },
    //             callback: function(data) {
    //                 if (data.message) {
    //                     frm.clear_table('customer_partnership');
    //                     for (let i = 0; i < data.message.length; i++) {
    //                         var row = frm.add_child('customer_partnership');
    //                         row.customer = data.message[i].customer;
    //                         row.father_name = data.message[i].father_name;
    //                         row.id_card_no = data.message[i].id_card_no;
    //                         row.mobile_no = data.message[i].mobile_no;
    //                         row.address = data.message[i].address;
    //                         row.share_percentage = data.message[i].share_percentage;
    //                     }
    //                     frm.refresh_fields('customer_partnership');        
    //                 } else {
    //                     frappe.msgprint(__('Error: ') + data.exc);
    //                 }
    //             }
    //         });
        
    //     }
    // },   



});

function calculate_net_amount(frm) {
    var netTransferAmount = frm.doc.gross_transfer_amount + frm.doc.discount ;
    frm.set_value("net_transfer_amount", netTransferAmount);
}