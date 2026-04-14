// frappe.ui.form.on('Customer', {
//     refresh: function (frm) {
//         setTimeout(() => {
//             cur_frm.page.remove_inner_button(__('Accounts Receivable'),  __('View'));
//             cur_frm.page.remove_inner_button(__('Accounting Ledger'),  __('View'));
//        }, 500);
//        if (frm.doc.customer_group === "P91 Car Care")
//        {
//         frm.add_custom_button(__('Add Vehicle'), function () {
//             frappe.model.with_doctype('Customer Wise Vehicle', function () {
//                 let customer_doc = frappe.model.get_new_doc('Customer Wise Vehicle');
//                 customer_doc.customer = frm.doc.name;
//                 customer_doc.document_type = "Customer";
//                 frappe.set_route('Form', 'Customer Wise Vehicle', customer_doc.name);
//             });
//         },);
//     }
//     }
// });  

frappe.ui.form.on('Customer', {
    refresh: async function (frm) {
        // Remove "Accounts Receivable" and "Accounting Ledger" buttons
        frappe.after_ajax(() => {
            ["Accounts Receivable", "Accounting Ledger"].forEach(button => 
                cur_frm.page.remove_inner_button(__(button), __('View'))
            );
        });

        if (frm.doc.customer_group !== "P91 Car Care" || !frm.doc.lead_name) return;

        frm.add_custom_button(__('Add Vehicle'), async function () {
            await frappe.model.with_doctype('Customer Wise Vehicle');
            try {
                const lead_doc = await frappe.db.get_doc('Lead', frm.doc.lead_name);
                if (!lead_doc) {
                    frappe.msgprint(__('Lead not found.'));
                    return;
                }
                // Check if a "Customer Wise Vehicle" exists for this Lead
                const { message } = await frappe.db.get_value('Customer Wise Vehicle', { "customer": frm.doc.lead_name }, "name");
                if (message?.name) {
                    await frappe.set_route('Form', 'Customer Wise Vehicle', message.name);
                    frappe.model.set_value('Customer Wise Vehicle', message.name, {
                        'document_type': 'Customer',
                        'customer': frm.doc.name
                    });
                    return;
                }
                // Create new "Customer Wise Vehicle" entry
                let customer_doc = frappe.model.get_new_doc('Customer Wise Vehicle');
                Object.assign(customer_doc, {
                    customer: frm.doc.name,
                    document_type: "Customer",
                    mobile_number:frm.doc.mobile_no
                });
                await frappe.set_route('Form', 'Customer Wise Vehicle', customer_doc.name);
                frappe.msgprint(__('No existing Customer Wise Vehicle found. Created a new one.'));
            } catch (error) {
                frappe.msgprint(__('Error fetching Lead details: ') + error.message);
            }
        });





        if (frm.is_new()) return;

        // ================= ADD FOLLOW UP =================
        frm.add_custom_button(__('Add Follow Up'), function () {

            let dialog = new frappe.ui.Dialog({
                title: 'Add Event',
                fields: [
                    {
                        fieldname: 'subject',
                        fieldtype: 'Data',
                        label: 'Subject',
                        reqd: 1,
                        default: `Meeting with ${frm.doc.customer_name || frm.doc.name}`
                    },
                    {
                        fieldname: 'starts_on',
                        fieldtype: 'Datetime',
                        label: 'Start Time',
                        reqd: 1,
                        default: frappe.datetime.now_datetime()
                    },
                    {
                        fieldname: 'ends_on',
                        fieldtype: 'Datetime',
                        label: 'End Time',
                        reqd: 1,
                        default: frappe.datetime.now_datetime()
                    },
                    {
                        fieldname: 'event_category',
                        fieldtype: 'Select',
                        label: 'Event Category',
                        options: [
                            'Event',
                            'Meeting',
                            'Call',
                            'Sent/Received Email',
                            'Other',
                            'Follow Up',
                            'Studio Visit'
                        ],
                        default: 'Follow Up'
                    },
                    {
                        fieldname: 'assign_users',
                        fieldtype: 'MultiSelectPills',
                        label: 'Assign To',
                        get_data: txt => frappe.db.get_link_options('User', txt)
                    },
                    {
                        fieldname: 'description',
                        fieldtype: 'Small Text',
                        label: 'Description'
                    }
                ],
                primary_action_label: 'Save',
                primary_action(values) {

                    frappe.call({
                        method: "justsign_custom.public.py.customer.create_event_with_todos_customer",
                        args: {
                            data: {
                                subject: values.subject,
                                starts_on: values.starts_on,
                                ends_on: values.ends_on,
                                description: values.description,
                                event_category: values.event_category,
                                customer_name: frm.doc.name,
                                assign_users: values.assign_users || []
                            }
                        },
                        callback() {
                            frappe.msgprint(__('Event and ToDo(s) created successfully'));
                            dialog.hide();
                        }
                    });
                }
            });

            dialog.show();
        });


        // ================= RNR FOLLOW UP =================
        frm.add_custom_button(__('RNR Follow Up'), function () {

            let dialog = new frappe.ui.Dialog({
                title: 'RNR Follow Up',
                fields: [
                    {
                        fieldname: 'subject',
                        fieldtype: 'Data',
                        label: 'Subject',
                        reqd: 1,
                        default: 'Followup Call'
                    },
                    {
                        fieldname: 'starts_on',
                        fieldtype: 'Datetime',
                        label: 'Start Time',
                        reqd: 1,
                        default: frappe.datetime.now_datetime()
                    },
                    {
                        fieldname: 'event_category',
                        fieldtype: 'Select',
                        label: 'Event Category',
                        options: [
                            'Event',
                            'Meeting',
                            'Call', 
                            'Sent/Received Email',
                            'Other',
                            'Follow Up',
                            'Studio Visit'
                        ],
                        default: 'Follow Up'
                    },
                    {
                        fieldname: 'description',
                        fieldtype: 'Small Text',
                        label: 'Description'
                    }
                ],
                primary_action_label: 'Save',
                primary_action(values) {

                    frappe.call({
                        method: "justsign_custom.public.py.customer.create_event_with_todos_rnr_customer",
                        args: {
                            data: {
                                description: values.description,
                                customer_name: frm.doc.name
                            }
                        },
                        callback() {
                            frappe.msgprint(__('RNR Event and ToDo created successfully'));
                            dialog.hide();
                        }
                    });
                }
            });

            dialog.show();
        });

    
    // Create a Opportunity button 
        if(!frm.is_new()){
            frm.add_custom_button(__('Create Opportunity'), async function () {
                frappe.model.with_doctype('Opportunity', async () => {
                    
                    let opportunity_doc = frappe.model.get_new_doc('Opportunity');

                    opportunity_doc.opportunity_from = "Customer";
                    opportunity_doc._customer = frm.doc.name;
                    
                    
                    frappe.set_route('Form', 'Opportunity', opportunity_doc.name);
                }) 
            })
        }


    }
});

// frappe.ui.form.on('Customer', {
//     refresh: async function (frm) {
//         // Remove "Accounts Receivable" and "Accounting Ledger" buttons
//         frappe.after_ajax(() => {
//             cur_frm.page.remove_inner_button(__('Accounts Receivable'), __('View'));
//             cur_frm.page.remove_inner_button(__('Accounting Ledger'), __('View'));
//         });

//         if (frm.doc.customer_group !== "P91 Car Care") return;

//         frm.add_custom_button(__('Add Vehicle'), async function () {
//             await frappe.model.with_doctype('Customer Wise Vehicle');

//             try {
//                 const prospect_doc = await frappe.db.get_doc('Prospect', frm.doc.prospect_name);
//                 if (!prospect_doc.leads || prospect_doc.leads.length === 0) {
//                     frappe.msgprint(__('No leads found in Prospect.'));
//                     return;
//                 }

//                 for (let row of prospect_doc.leads) {
//                     const vehicle_doc_res = await frappe.db.get_value('Customer Wise Vehicle', { "customer": row.lead }, "name");
//                     if (vehicle_doc_res && vehicle_doc_res.message && vehicle_doc_res.message.name) {
//                         const vehicle_doc_name = vehicle_doc_res.message.name;
//                         await frappe.set_route('Form', 'Customer Wise Vehicle', vehicle_doc_name);
//                         frappe.model.set_value('Customer Wise Vehicle', vehicle_doc_name, 'document_type', 'Customer');
//                         frappe.model.set_value('Customer Wise Vehicle', vehicle_doc_name, 'customer', frm.doc.name);
//                         return;
//                     }
//                 }

//                 // Create new Customer Wise Vehicle entry
//                 frappe.run_serially([
//                     async () => {
//                         let customer_doc = frappe.model.get_new_doc('Customer Wise Vehicle');
//                         customer_doc.customer = frm.doc.name;
//                         customer_doc.document_type = "Customer";
//                         await frappe.set_route('Form', 'Customer Wise Vehicle', customer_doc.name);
//                     },
//                     () => frappe.msgprint(__('No existing Customer Wise Vehicle found. Created a new one.'))
//                 ]);
                
//             } catch (error) {
//                 frappe.msgprint(__('Error fetching prospect details: ') + error.message);
//             }
//         });
//     }
// });





