frappe.ui.form.on('Sales Invoice', {
    // after_save: function(frm) {
    //     if (frm.doc.custom_customer_vehicle_no) {
    //         frappe.call({
    //             method: 'frappe.client.insert',
    //             args: {
    //                 doc: {
    //                     doctype: 'Book Package',
    //                     // package_name: frm.doc.custom_package,  // Mapping package_name
    //                     customer: frm.doc.customer,  // Mapping customer
    //                     vehicle_no: frm.doc.custom_customer_vehicle_no,  // Mapping vehicle_no
    //                     si_id: frm.doc.name,  // Mapping Sales Invoice name as si_id
    //                     book_package_item: frm.doc.items.map(row => ({
    //                         item_code: row.item_code,
    //                         item_name: row.item_name,
    //                         qty: row.qty,
    //                         uom: row.uom
    //                     })) // Mapping child table items
    //                 }
    //             },
    //             callback: function(response) {
    //                 if (response.message) {
    //                     frappe.msgprint(__('Book Package {0} created successfully!', [response.message.name]));
    //                 }
    //             }
    //         });
    //     }
    // },
    custom_package: function(frm) {
        if (!frm.doc.custom_package) {
            return;
        }
        // Fetch Customer Wise Vehicle document
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Packages',
                name: frm.doc.custom_package  // Selected vehicle details
            },
            callback: function(response) {
                if (response.message) {
                    let vehicle_doc = response.message;
                    // Clear existing items in Sales Order
                    frm.clear_table('items');
                    // Loop through child table (Customer Wise Vehicle Item)
                    vehicle_doc.items.forEach(row => {
                        let child = frm.add_child('items');
                        child.item_code = row.item;
                        child.item_name = row.item_name;
                        child.uom = row.uom;
                        child.qty = row.qty;
                    });
                    frm.refresh_field('items');  // Refresh the child table UI
                }
            }
        });
    },
    refresh: function (frm) {
        if (frm.doc.customer) {
            frm.set_query('custom_customer_vehicle_no', function() {
                return {
                    filters: {
                        customer: frm.doc.customer  // Match customer field
                    }
                }; 
            });
        }
        if(frm.doc.irn){
            frm.add_custom_button(__('Send Whatsapp'), function() {
                 frappe.call({
                    method: "justsign_custom.public.py.sales_invoice.create_and_attach_pdf",
                    args: {
                        // doc: frm.doc.name
                        doctype: frm.doc.doctype,
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(
                                __("PDF Generated/Updated: <a href='" + r.message + "' target='_blank'>" + r.message + "</a>")
                            );
                            frm.reload_doc();
                        }
                    }
                })
            }) 
        }
    },
    customer: function (frm) {
        if (frm.doc.customer) {
            frm.set_query('custom_customer_vehicle_no', function() {
                return {
                    filters: {
                        customer: frm.doc.customer  // Match customer field
                    }
                };
            });
        }
    },
});

frappe.ui.form.on('Sales Invoice Item', {
    async item_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn]; 
        if (row.item_code) {
            // Fetch package amount from "Packages"
            let pkg_type_res = await frappe.db.get_value("Packages", { name: row.item_code }, "package_amount");

            if (pkg_type_res && pkg_type_res.message && pkg_type_res.message.package_amount) {
                let package_amount = pkg_type_res.message.package_amount;

                // Override standard rate calculation after a short delay
                setTimeout(() => {
                    frappe.model.set_value(cdt, cdn, 'rate', package_amount);
                    frm.refresh_field('items'); // Refresh the child table UI
                }, 500); // Delay ensures our value is set last
            }
            // try {
            //     console.log("Call")
            //     let item = await frappe.db.get_doc('Item', row.item_code);
            //     if (item.item_group === "PPF") {
            //         console.log("Call1")
            //         let item_group = await frappe.db.get_doc('Item Group', item.item_group);
            //         if (item_group.custom_qty) {
            //             console.log(item_group.custom_qty)
            //             frappe.model.set_value(cdt, cdn, 'qty', item_group.custom_qty);
            //             frm.refresh_field('items'); // Refresh the child table UI
            //         }
            //     }
            // } catch (error) {
            //     console.error("Error fetching data:", error);
            // }
        }
    }
});


// frappe.ui.form.on('Sales Invoice', {
//     item_code: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         if (row.item_code) {
//             frappe.call({
//                 method: 'frappe.client.get',
//                 args: {
//                     doctype: 'Item',
//                     name: row.item_code
//                 },
//                 callback: function(response) {
//                     if (response.message) {
//                         let item_group = response.message.item_group;
//                         if (item_group === "PPF") {
//                             frappe.call({
//                                 method: 'frappe.client.get',
//                                 args: {
//                                     doctype: 'Item Group',
//                                     name: item_group
//                                 },
//                                 callback: function(resp) {
//                                     if (resp.message) {
//                                         let item_qty = resp.message.custom_qty;
//                                         frappe.model.set_value(cdt, cdn, 'qty', item_qty);
//                                         frm.refresh_field('items');  // Refresh the child table UI
//                                     }
//                                 }
//                             });
//                         }
//                     }
//                 }
//             });
//         }
//     }
// });
