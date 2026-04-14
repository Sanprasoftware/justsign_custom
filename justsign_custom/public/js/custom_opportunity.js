frappe.ui.form.on('Opportunity', {
    refresh: function (frm) {
        // frm.timeline.insert_comment('Comment', 'This is an automated comment.');
        // setTimeout(() => {
    //         cur_frm.page.remove_inner_button(__('Quotation'),  __('Create'));
    //         cur_frm.page.remove_inner_button(__('Supplier Quotation'),  __('Create'));
    //         cur_frm.page.remove_inner_button(__('Request For Quotation'),  __('Create'));
    //         cur_frm.page.remove_inner_button(__('Close'));
    //    }, 500);
        if(frm.doc._customer){
            frm.doc.party_name = frm.doc._customer
            frm.refresh_field('party_name')
        }
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
                        method:"justsign_custom.public.py.opportunity.add_comments",
                        args:{
                            comment:values.comment,
                            email: frm.doc.contact_email,
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
                        method: "justsign_custom.public.py.opportunity.create_event_with_todos_opportunity",
                        args: {
                            data: {
                                subject: values.subject,
                                starts_on: values.starts_on,
                                ends_on: values.ends_on,
                                description: values.description,
                                event_category: values.event_category,
                                opportunity_name: frm.doc.name,
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
                        method: "justsign_custom.public.py.opportunity.create_event_with_todos_rnr_opportunity",
                        args: {
                            data: {
                                description: values.description,
                                opportunity_name: frm.doc.name
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




    },
    // status: function (frm) {
    //     frappe.call({
    //         method: "justsign_custom.public.py.opportunity.set_quotation_lost",
    //         doc: frm.doc
    //         // agrs: {
    //         //     doc: frm.doc
    //         // }
    //     })
    // }
});  