// frappe.ui.form.on("Sales Invoice", {
//     custom_pdf: function(frm) {
//         if (frm.doc.custom_pdf) {
//             frappe.call({
//                 method: "justsign_custom.justsign_custom..create_and_attach_pdf",
//                 args: {
//                     docname: frm.doc.name
//                 },
//                 callback: function(r) {
//                     if (r.message) {
//                         frappe.msgprint(
//                             __("PDF Generated/Updated: <a href='" + r.message + "' target='_blank'>" + r.message + "</a>")
//                         );
//                         frm.reload_doc();
//                     }
//                 }
//             });
//         }
//     }
// });
// frappe.ui.form.on("Sales Invoice", {
//     custom_pdf: function(frm) {
//         if (frm.doc.custom_pdf) {
//             frappe.call({
//                 method: "justsign_custom.justsign_custom..create_and_attach_pdf",
//                 args: {
//                     docname: frm.doc.name
//                 },
//                 callback: function(r) {
//                     if (r.message) {
//                         frappe.msgprint(
//                             __("PDF Generated/Updated: <a href='" + r.message + "' target='_blank'>" + r.message + "</a>")
//                         );
//                         frm.reload_doc();
//                     }
//                 }
//             });
//         }
//     }
// });
