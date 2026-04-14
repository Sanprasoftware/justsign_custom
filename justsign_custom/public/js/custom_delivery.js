frappe.ui.form.on('Delivery Note', {
    refresh: function (frm) {
        if (frm.doc.customer) {
            frm.set_query('custom_select_package', function() {
                return {
                    filters: {
                        customer: frm.doc.customer  // Match customer field
                    }
                };
            });
        }
        setTimeout(() => {
            cur_frm.page.remove_inner_button(__('Pricing Rule'),  __('Create'));
            cur_frm.page.remove_inner_button(__('Link with Supplier'),  __('Actions'));
            cur_frm.page.remove_inner_button(__('Get Customer Group Details'),  __('Actions'));

            cur_frm.page.remove_inner_button(__('Accounts Receivable'),  __('View'));
            cur_frm.page.remove_inner_button(__('Accounting Ledger'),  __('View'));

            cur_frm.page.remove_inner_button(__('Close'));
       }, 500);
       if (frm.doc.custom_select_package && frm.doc.docstatus == 0)
        {
            frm.add_custom_button(__('Job Completion'), function () {
                frappe.model.with_doctype('Job Completion', function () {
                    let customer_doc = frappe.model.get_new_doc('Job Completion');
                    customer_doc.document_type = "Delivery Note";
                    customer_doc.delivery_not_id = frm.doc.name;
                    customer_doc.vehicle_no = frm.doc.custom_vehicle_details;
                    frappe.set_route('Form', 'Job Completion', customer_doc.name);
                });
            },);
        }  

        frappe.db.get_value("Customer", frm.doc.customer, "customer_group", (r) => {
            let customer_group = r.customer_group;
             if (frm.doc.docstatus == 0 && frm.doc.custom_select_package && customer_group == "P91 Car Care")
            { 
                frm.add_custom_button(__('Create Job Card'), async function () {
                    frappe.model.with_doctype('Job Cards', async function () {
                        let job_card_doc = frappe.model.get_new_doc('Job Cards');
                        job_card_doc.document_type = "Delivery Note";
                        job_card_doc.document_id = frm.doc.name;
                        job_card_doc.customer = frm.doc.customer;
                        job_card_doc.vehicle_details = frm.doc.custom_vehicle_details;
    
                        await frappe.call({
                            method: 'frappe.client.get',
                            args: {
                                doctype: 'Delivery Note',
                                name: frm.doc.name
                            },
                            callback: async function (response) {
                                if (response.message) {
                                    let delivery_note_doc = response.message;
                                    job_card_doc.items = [];
                                    delivery_note_doc.items.forEach(row => {
                                        let child = job_card_doc.items.push({
                                            item_code: row.item_code,
                                            item_name: row.item_name,
                                            uom: row.uom,
                                            qty: row.qty
                                        });
                                    });
                                    frappe.set_route('Form', 'Job Cards', job_card_doc.name);
                                }
                            }
                        });
                    });
                });
            }
        })
        // if (frm.doc.docstatus == 0 && frm.doc.custom_select_package)
        //     { 
        //         frm.add_custom_button(__('Create Job Card'), async function () {
        //             frappe.model.with_doctype('Job Cards', async function () {
        //                 let job_card_doc = frappe.model.get_new_doc('Job Cards');
        //                 job_card_doc.document_type = "Delivery Note";
        //                 job_card_doc.document_id = frm.doc.name;
        //                 job_card_doc.customer = frm.doc.customer;
        //                 job_card_doc.vehicle_details = frm.doc.custom_vehicle_details;
    
        //                 await frappe.call({
        //                     method: 'frappe.client.get',
        //                     args: {
        //                         doctype: 'Delivery Note',
        //                         name: frm.doc.name
        //                     },
        //                     callback: async function (response) {
        //                         if (response.message) {
        //                             let delivery_note_doc = response.message;
        //                             job_card_doc.items = [];
        //                             delivery_note_doc.items.forEach(row => {
        //                                 let child = job_card_doc.items.push({
        //                                     item_code: row.item_code,
        //                                     item_name: row.item_name,
        //                                     uom: row.uom,
        //                                     qty: row.qty
        //                                 });
        //                             });
        //                             frappe.set_route('Form', 'Job Cards', job_card_doc.name);
        //                         }
        //                     }
        //                 });
        //             });
        //         });
        //     }
    },
    on_submit: function(frm) {
        console.log("qqqqqqqqqqqqqq")
        // if (!frm.doc.custom_job_completion_id) {
        //     frappe.throw(__('Please Add Job Completion before submitting.'));
        // }
        if (frm.doc.custom_select_package) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Book Package',  
                    name: frm.doc.custom_select_package  
                },
                callback: function(response) {
                    if (response.message) {
                        let book_package_doc = response.message;

                        // Loop through Delivery Note Items
                        frm.doc.items.forEach(dn_item => {
                            // Find matching item in Book Package Items
                            let matching_item = book_package_doc.book_package_item.find(bp_item => 
                                bp_item.item_code === dn_item.item_code
                            );

                            // If match found, add qty to use_pkg_qty
                            if (matching_item || ((matching_item.use_pkg_qty || 0) + dn_item.qty) <= matching_item.qty) {
                                matching_item.use_pkg_qty = (matching_item.use_pkg_qty || 0) + dn_item.qty;
                            } else {
                                frappe.validate = false;
                                frappe.throw(__('Qty Cannot be greater.'));
                                return;
                            }
                        });

                        // Save the updated Book Package
                        frappe.call({
                            method: 'frappe.client.save',
                            args: {
                                doc: book_package_doc
                            },
                        });
                    }
                }
            });
        }
    },
    // before_save(frm){
    //     if (frm.doc.custom_select_package) {
    //         frappe.call({
    //             method: 'frappe.client.get',
    //             args: {
    //                 doctype: 'Book Package',  
    //                 name: frm.doc.custom_select_package  
    //             },
    //             callback: function(response) {
    //                 if (response.message) {
    //                     let book_package_doc = response.message;

    //                     // Loop through Delivery Note Items
    //                     frm.doc.items.forEach(dn_item => {
    //                         // Find matching item in Book Package Items
    //                         let matching_item = book_package_doc.book_package_item.find(bp_item => 
    //                             bp_item.item_code === dn_item.item_code
    //                         );

    //                         // If match found, add qty to use_pkg_qty
    //                         if (matching_item || ((matching_item.use_pkg_qty || 0) + dn_item.qty) > matching_item.qty) {
    //                             frappe.validate = false;
    //                             frappe.throw(__('Please Add Vehicle Check List before submitting.'));
    //                         }
    //                     });
    //                 }
    //             }
    //         });
    //     }
    // },
    custom_select_package: function(frm) {
        if (!frm.doc.custom_select_package) {
            return;
        }
        // Fetch Customer Wise Vehicle document
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Book Package',
                name: frm.doc.custom_select_package  // Selected vehicle details
            },
            callback: function(response) {
                if (response.message) {
                    let vehicle_doc = response.message;
                    // Clear existing items in Sales Order
                    frm.clear_table('items');
                    // Loop through child table (Customer Wise Vehicle Item)
                    vehicle_doc.book_package_item.forEach(row => {
                        if(row.qty > row.use_pkg_qty){
                            let child = frm.add_child('items');
                            child.item_code = row.item_code;
                            child.item_name = row.item_name;
                            child.uom = row.uom;
                            child.stock_uom = row.uom;
                            child.qty = row.qty - row.use_pkg_qty;
                        }
                    });
                    frm.refresh_field('items');  // Refresh the child table UI
                }
            }
        });
    }
});

frappe.ui.form.on('Delivery Note', {    
    after_cancel: function(frm) {
        if (frm.doc.custom_select_package) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Book Package',
                    name: frm.doc.custom_select_package
                },
                callback: function(response) {
                    if (response.message) {
                        let book_package_doc = response.message;

                        // Loop through Delivery Note Items
                        frm.doc.items.forEach(dn_item => {
                            // Find matching item in Book Package Items
                            let matching_item = book_package_doc.book_package_item.find(bp_item => 
                                bp_item.item_code === dn_item.item_code
                            );

                            // If match found, subtract qty from use_pkg_qty
                            if (matching_item) {
                                matching_item.use_pkg_qty = (matching_item.use_pkg_qty || 0) - dn_item.qty;
                                if (matching_item.use_pkg_qty < 0) {
                                    matching_item.use_pkg_qty = 0; // Prevent negative values
                                }
                            }
                        });

                        // Save the updated Book Package
                        frappe.call({
                            method: 'frappe.client.save',
                            args: {
                                doc: book_package_doc
                            },
                            // callback: function(save_response) {
                            //     if (save_response.message) {
                            //         frappe.msgprint(__('Book Package updated successfully with reduced quantities.'));
                            //     }
                            // }
                        });
                    }
                }
            });
        }
    }
});
