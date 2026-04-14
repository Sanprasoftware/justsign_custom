// // Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Book Package", {
//     package_name: function(frm) {
//         if (frm.doc.package_name) {
//             frappe.call({
//                 method: 'frappe.client.get',
//                 args: { 
//                     doctype: 'Packages',
//                     name: frm.doc.package_name
//                 },
//                 callback: function(r) {
//                     if (r.message) {
//                         // Clear existing child table data
//                         frm.clear_table('book_package_item');
                        
//                         // Loop through the 'items' child table of the selected package
//                         $.each(r.message.items || [], function(i, item) {
//                             // Add data to the 'book_package_item' child table
//                             frm.add_child('book_package_item', {
//                                 item: item.item,
//                                 item_name: item.item_name,
//                                 uom: item.uom,
//                                 qty: item.qty
//                             });
//                         });
                        
//                         // Refresh the child table
//                         frm.refresh_field('book_package_item');
//                     }
//                 }
//             });
//         }
//     }
// });

