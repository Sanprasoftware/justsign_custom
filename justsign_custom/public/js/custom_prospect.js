// frappe.ui.form.on('Prospect', {
//     refresh: function (frm) {
//         setTimeout(() => {
//             cur_frm.page.remove_inner_button(__('Customer'),  __('Create'));
//        }, 500);
//         // Add a custom button to the toolbar
//         frm.add_custom_button(__('Create Customer'), function () {
//             // Open a new Customer form and pre-fill the 'prospect_name' field
//             frappe.model.with_doctype('Customer', function () {
//                 let customer_doc = frappe.model.get_new_doc('Customer');
//                 customer_doc.prospect_name = frm.doc.name; // Pre-fill 'prospect_name' with the current Prospect name
//                 customer_doc.customer_name = frm.doc.company_name;
//                 customer_doc.customer_group = frm.doc.customer_group;
//                 customer_doc.territory = frm.doc.territory;
//                 frappe.set_route('Form', 'Customer', customer_doc.name);
//             });
//         }, __('Create'));


//         if (frm.doc.leads && frm.doc.leads.length > 0) {
//             frappe.call({
//                 method: "frappe.client.get_list",
//                 args: {
//                     doctype: "Lead",
//                     filters: [
//                         ["name", "in", frm.doc.leads.map(row => row.lead)],
//                         ["status", "=", "Converted"]
//                     ],
//                     fields: ["name"]
//                 },
//                 callback: function(response) {
//                     if (response.message.length > 0) {
//                         frm.page.remove_inner_button("Create Customer", "Create");
//                     }
//                 }
//             });
//         }
//     }
// });



// frappe.ui.form.on('Prospect', {
//     refresh: function (frm) {
//         // Remove default Customer button after a short delay
//         setTimeout(() => {
//             cur_frm.page.remove_inner_button(__('Customer'),  __('Create'));
//         }, 500);

//         // Add custom Create Customer button
//         frm.add_custom_button(__('Create Customer'), function () {
//             frappe.model.with_doctype('Customer', function () {
//                 let customer_doc = frappe.model.get_new_doc('Customer');
//                 customer_doc.prospect_name = frm.doc.name; // Pre-fill 'prospect_name'
//                 customer_doc.customer_name = frm.doc.company_name;
//                 customer_doc.customer_group = frm.doc.customer_group;
//                 customer_doc.territory = frm.doc.territory;
//                 frappe.set_route('Form', 'Customer', customer_doc.name);
//             });
//         }, __('Create'));

//         // Check if any Lead is already converted
//         if (frm.doc.leads && frm.doc.leads.length > 0) {
//             frappe.call({
//                 method: "frappe.client.get_list",
//                 args: {
//                     doctype: "Lead",
//                     filters: [
//                         ["name", "in", frm.doc.leads.map(row => row.lead)],
//                         ["status", "=", "Converted"]
//                     ],
//                     fields: ["name"]
//                 },
//                 callback: function(response) {
//                     if (response.message.length > 0) {
//                         frm.page.remove_inner_button("Create Customer", "Create");
//                     }
//                 }
//             });
//         }

//         // ---- Our new code: check if Customer already exists ----
//         frappe.call({
//             method: "justsign_custom.public.py.prospect.check_customer_exists", // Replace with your Python path
//             // justsign_custom.public.py.prospect
//             args: { prospect_name: frm.doc.name },
//             callback: function(r) { 
//                 if (r.message) {
//                     // Customer exists → remove Create button
//                     frm.page.remove_inner_button("Create Customer", "Create");

//                     // Optional: Add "View Customer" button
//                     frm.add_custom_button(__('View Customer'), function () {
//                         frappe.set_route('Form', 'Customer', r.message);
//                     });
//                 }
//             }
//         });
//     }
// });

frappe.ui.form.on('Prospect', {
    refresh: function (frm) {
        // Remove default Customer button after a short delay
        setTimeout(() => {
            cur_frm.page.remove_inner_button(__('Customer'), __('Create'));
        }, 500);

        // Add custom Create Customer button
        frm.add_custom_button(__('Create Customer'), function () {
            frappe.model.with_doctype('Customer', function () {
                let customer_doc = frappe.model.get_new_doc('Customer');
                customer_doc.prospect_name = frm.doc.name; // Pre-fill 'prospect_name'
                customer_doc.customer_name = frm.doc.company_name;
                customer_doc.customer_group = frm.doc.customer_group;
                customer_doc.territory = frm.doc.territory;
                frappe.set_route('Form', 'Customer', customer_doc.name);
            });
        }, __('Create'));

        // Hide Create Customer button if any Lead is converted
        if (frm.doc.leads && frm.doc.leads.length > 0) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Lead",
                    filters: [
                        ["name", "in", frm.doc.leads.map(row => row.lead)],
                        ["status", "=", "Converted"]
                    ],
                    fields: ["name"]
                },
                callback: function(response) {
                    if (response.message.length > 0) {
                        frm.page.remove_inner_button("Create Customer", "Create");
                    }
                }
            });  
        }

        // -------- Hide Create Customer button if Customer already exists --------
        frappe.call({
            method: "justsign_custom.public.py.prospect.check_customer_exists", 
            args: { prospect_name: frm.doc.name },
            callback: function(r) {
                if (r.message) {
                    // Customer exists → hide Create button 
                    console.log(r.message)
                    frm.page.remove_inner_button("Create Customer", "Create");

                    // Optional: add "View Customer" button
                    frm.add_custom_button(__('View Customer'), function () {
                        frappe.set_route('Form', 'Customer', r.message);
                    });
                }
            } 
        });

        // -------- Hide Create Opportunity button if Opportunity already exists --------
        // frappe.call({
        //     method: "justsign_custom.public.py.prospect.check_opportunity_exists", 
        //     args: { prospect_name: frm.doc.name },
        //     callback: function(r) {
        //         if (r.message) {
        //             // Opportunity exists → hide Create button 
        //             console.log(r.message)
        //             frm.page.remove_inner_button("Opportunity", "Create");

        //             // Optional: add "View Customer" button
        //             frm.add_custom_button(__('View Customer'), function () {
        //                 frappe.set_route('Form', 'Opportunity', r.message);
        //             });
        //         }
        //     } 
        // });




            frm.add_custom_button(__("Add Comment"), function() {
            if(!frm.is_new()){  
                let d = new frappe.ui.Dialog({
                title: 'Enter Comment',
                fields: [
                    {
                        label: 'Comment',
                        fieldname: 'comment',
                        fieldtype: 'Small Text',
                        reqd:1
                    }
                
                ],
                size: 'small', 
                primary_action_label: 'Add Comment',
                async primary_action(values) {
                    frappe.call({
                        method:"justsign_custom.public.py.prospect.add_comments",
                        args:{
                            comment:values.comment,
                            email: frm.doc.custom_email,
                            name: frm.doc.name
                        },
                        callback:(response)=>{
                        if(response.message == "Success"){
                            frappe.msgprint("Comment Added Successfully")
                        }else{
                            frappe.msgprint("Failed to Add Comment")
                        }
                            
                        }
                    })
                    d.hide();
                }
            }); 
                    d.show();   
            }
            
        })




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
                        default: `Meeting with ${frm.doc.name}`
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
                        method: "justsign_custom.public.py.prospect.create_event_with_todos_prospect",
                        args: {
                            data: {
                                subject: values.subject,
                                starts_on: values.starts_on,
                                ends_on: values.ends_on,
                                description: values.description,
                                event_category: values.event_category,
                                prospect_name: frm.doc.name,
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
                            default: `Fallow Up Call`
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
                            method: "justsign_custom.public.py.prospect.create_event_with_todos_rnr_prospect",
                            args: {
                                data: {
                                    description: values.description,
                                    prospect_name: frm.doc.name
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




    }
});

