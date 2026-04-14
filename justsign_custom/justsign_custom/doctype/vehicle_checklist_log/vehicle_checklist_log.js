// Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Checklist Log", {
    on_submit: function(frm) {
        if (frm.doc.delivery_not_id) {
            frappe.db.set_value("Delivery Note", frm.doc.delivery_not_id, "custom_check_list_id", frm.doc.name)
                .then(response => {
                    if (!response.exc) {
                        frappe.msgprint(__('Delivery Note updated successfully!'));
                    }
                });
        }
    },
    // before_cancel: function(frm) {
    //     if (frm.doc.delivery_not_id) {
    //         frappe.db.set_value("Delivery Note", frm.doc.delivery_not_id, "custom_check_list_id", null)
    //             .then(response => {
    //                 if (!response.exc) {
    //                     frappe.msgprint(__('Checklist ID removed from Delivery Note!'));
    //                 }
    //             });
    //     }
    // }
});

// frappe.ui.form.on('Vehicle Checklist Log', {
//     on_cancel: function(frm) {
//         if (frm.doc.delivery_not_id) {
//             frappe.call({
//                 method: 'frappe.client.set_value',
//                 args: {
//                     doctype: 'Delivery Note',
//                     name: frm.doc.delivery_not_id,
//                     fieldname: 'custom_check_list_id',
//                     value: ''
//                 },
//                 callback: function(response) {
//                     if (!response.exc) {
//                         frappe.msgprint(__('Checklist ID cleared successfully.'));
//                     }
//                 }
//             });
//         }
//     }
// });




