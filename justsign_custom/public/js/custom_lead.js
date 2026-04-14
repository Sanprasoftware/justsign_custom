frappe.ui.form.on('Lead', {
    refresh: function(frm) {
        // frm.timeline.insert_comment('Comment', 'This is an automated comment.');
        setTimeout(() => {
            cur_frm.page.remove_inner_button(__('Customer'),  __('Create'));
       }, 500);
    },
    custom_vehicle_type: function(frm) {
        if (frm.doc.custom_vehicle_type === "Car") {
             frm.set_value('custom_bike_type', '');
             frm.set_value('custom_bike_brand', '');
             frm.set_value('custom_bike_model_name', '');
         } else {
             frm.set_value('custom_body_type', '');
             frm.set_value('custom_car_brand', '');
             frm.set_value('custom_car_model_name', '');
         }
     }
}); 


 
frappe.ui.form.on('Lead', {
    refresh: function(frm) {
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
                        method:"justsign_custom.public.py.custom_lead.add_comments",
                        args:{
                            comment:values.comment,
                            email: frm.doc.email_id,
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
            
        });


    //   if (!frm.is_new()) {
    //         frm.add_custom_button(__('Add Event'), function () {

    //             let dialog = new frappe.ui.Dialog({
    //                 title: 'Add Event',
    //                 fields: [
    //                     {
    //                         fieldname: 'subject',
    //                         fieldtype: 'Data',
    //                         label: 'Subject',
    //                         reqd: 1,
    //                         default: `Meeting with ${frm.doc.lead_name}`
    //                     },
    //                     {
    //                         fieldname: 'starts_on',
    //                         fieldtype: 'Datetime',
    //                         label: 'Start Time',
    //                         reqd: 1,
    //                         default: frappe.datetime.now_datetime()
    //                     },
    //                     {
    //                         fieldname: 'duration',
    //                         fieldtype: 'Int',
    //                         label: 'Duration (Minutes)',
    //                         default: 30
    //                     },
    //                     {
    //                         fieldname: "Event Category",
    //                         fieldtype: "Select",
    //                         label: "Event Category",
    //                         options: [
    //                             "Event",
    //                             "Meeting",
    //                             "Call",
    //                             "Sent/Received Email",
    //                             "Other",
    //                             "Follow Up",
    //                             "Studio Visit",
    //                         ],
    //                         default: "Event"

    //                     },
    //                     {
    //                         fieldname: 'assign_users',
    //                         fieldtype: 'MultiSelectPills',
    //                         label: 'Assign To',
    //                         get_data: function (txt) {
    //                             return frappe.db.get_link_options('User', txt);
    //                         }
    //                     },
    //                     {
    //                         fieldname: 'description',
    //                         fieldtype: 'Small Text',
    //                         label: 'Description'
    //                     }
    //                 ],
    //                 primary_action_label: 'Save',
    //                 primary_action(values) {

    //                     let ends_on = moment(values.starts_on)
    //                         .add(values.duration || 30, 'minutes')
    //                         .format('YYYY-MM-DD HH:mm:ss');

    //                     frappe.call({
    //                         method: 'frappe.client.insert',
    //                         args: {
    //                             doc: {
    //                                 doctype: 'Event',
    //                                 subject: values.subject,
    //                                 starts_on: values.starts_on,
    //                                 ends_on: ends_on,
    //                                 description: values.description,
    //                                 event_participants: [{
    //                                     reference_doctype: 'Lead',
    //                                     reference_docname: frm.doc.name
    //                                 }]
    //                             }
    //                         },
    //                         callback: function () {
    //                             frappe.msgprint(__('Event created successfully'));
    //                             dialog.hide();
    //                         }
    //                     });
    //                 }
    //             });

    //             dialog.show();
    //         });
    //     }


 // ================= ADD EVENT =================
        if (frm.is_new()) return;
        frm.add_custom_button(__('Add Follow Up'), function () {

            let dialog = new frappe.ui.Dialog({
                title: 'Add Event',
                fields: [
                    {
                        fieldname: 'subject',
                        fieldtype: 'Data',
                        label: 'Subject',
                        reqd: 1,
                        default: `Meeting with ${frm.doc.lead_name}`
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
                        fieldname: 'duration',
                        fieldtype: 'Int',
                        label: 'Duration (Minutes)',
                        default: 30
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
                        default: 'Event'
                    },
                    {
                        fieldname: 'assign_users',
                        fieldtype: 'MultiSelectPills',
                        label: 'Assign To',
                        get_data: function (txt) {
                            return frappe.db.get_link_options('User', txt);
                        }
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
                        method: "justsign_custom.public.py.custom_lead.create_event_with_todos",
                        args: {
                            data: {
                                subject: values.subject,
                                starts_on: values.starts_on,
                                ends_on: values.ends_on,
                                duration: values.duration,
                                description: values.description,
                                event_category: values.event_category,
                                lead_name: frm.doc.name,
                                assign_users: values.assign_users || []
                            }
                        },
                        callback: function () {
                            frappe.msgprint(__('Event and ToDo(s) created successfully'));
                            dialog.hide();
                        }
                    });
                }
            });

            dialog.show();
        });



        if (frm.is_new()) return;

        frm.add_custom_button(__('RNR Follow Up'), function () {

            let dialog = new frappe.ui.Dialog({
                title: 'Add Event',
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
                    // {
                    //     fieldname: 'assign_users',
                    //     fieldtype: 'MultiSelectPills',
                    //     label: 'Assign To',
                    //     get_data: function (txt) {
                    //         return frappe.db.get_link_options('User', txt);
                    //     }
                    // },
                    {
                        fieldname: 'description',
                        fieldtype: 'Small Text',
                        label: 'Description'
                    }
                ],
                primary_action_label: 'Save',
                primary_action(values) {

                    frappe.call({
                        method: "justsign_custom.public.py.custom_lead.create_event_with_todos_rnr",
                        args: {
                            data: {
                                subject: values.subject,
                                starts_on: values.starts_on,
                                description: values.description,
                                event_category: values.event_category,
                                lead_name: frm.doc.name,
                                assign_users: values.assign_users || [],
                                created_from_button: 1  
                            }
                        },
                        callback: function () {
                            frappe.msgprint(__('Event and ToDo(s) created successfully'));
                            dialog.hide();
                        }
                    });
                }
            });

            dialog.show();
        });



    }
}); 



// frappe.ui.form.on('Lead', {
//     refresh: function(frm) {
//         // Ensure the form is fully loaded before inserting a comment
//         setTimeout(() => {
//             frappe.model.with_doc("Lead", frm.doc.name, function() {
//                 frappe.model.add_comment("Lead", frm.doc.name, "This is an automated comment.")
//                     .then(() => {
//                         frm.reload_doc(); // Reload to show the comment
//                     });
//             });
//         }, 500);

//         // Remove only the specific "Customer" button, ensuring others remain
//         setTimeout(() => {
//             frm.page.wrapper.find('.dropdown-menu .dropdown-item').each(function() {
//                 if ($(this).text().trim() === __('Customer')) {
//                     $(this).remove();
//                 }
//             });
//         }, 500);
//     },

//     custom_vehicle_type: function(frm) {
//         if (frm.doc.custom_vehicle_type === "Car") {
//             frm.set_value('custom_bike_type', '');
//             frm.set_value('custom_bike_brand', '');
//             frm.set_value('custom_bike_model_name', '');
//         } else {
//             frm.set_value('custom_body_type', '');
//             frm.set_value('custom_car_brand', '');
//             frm.set_value('custom_car_model_name', '');
//         }
//     }
// });
