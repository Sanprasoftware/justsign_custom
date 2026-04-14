// Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Field Visits", {
// 	refresh(frm) {

// 	},
// });
 // Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt


frappe.ui.form.on("Field Visits", {  
	refresh(frm) {
        frm.set_intro("Please Save Doc to attach files") 
        


        // ================= ADD EVENT =================
       if (frm.is_new()) return;

        frm.add_custom_button(__('Add Event'), function () {

            let d = new frappe.ui.Dialog({
                title: 'Create Event',
                fields: [
                    {
                        label: 'Subject',
                        fieldname: 'subject',
                        fieldtype: 'Data',
                    },
                    {
                        label: 'Starts On',
                        fieldname: 'starts_on',
                        fieldtype: 'Datetime',
                        default: frm.doc.visit_date
                    },
                    {
                        label: 'Event Category',
                        fieldname: 'event_category',
                        fieldtype: 'Select',
                        options: ['Event', 'Call', 'Meeting', 'Visit', 'Sent/Received Email', 'Others', 'Follow Up', 'Studio Visit'],
                        default: 'Select Category'
                    },
                    {
                        fieldname: 'assign_users',
                        fieldtype: 'MultiSelectPills',
                        label: 'Assign To', 
                        get_data: txt => frappe.db.get_link_options('User', txt)
                    },
                    {
                        label: 'Description',
                        fieldname: 'description',
                        fieldtype: 'Small Text'
                    }
                ],
                primary_action_label: 'Create',
                primary_action(values) {

                    frm.call({
                        doc: frm.doc,
                        method: "create_event",
                        args: {
                            data: values
                        },
                        callback: function (r) {
                            if (r.message) {
                                frappe.msgprint("Event Created: " + r.message);
                                // frappe.set_route("Form", "Event", r.message);
                            }
                        }
                    });

                    d.hide();
                }
            });

            d.show();

        });




	},
    start_time: function(frm) {
        if(!frm.doc.start){
            frm.doc.start = frappe.datetime.now_datetime();
            frm.doc.status = "Started"
            // frm.doc.refresh_field("items");
            frm.dirty()
            frm.save();   
        }
    },
    end_time: function(frm) {

        if (!frm.doc.end) {
            frm.doc.end = frappe.datetime.now_datetime();
        }

        // calculate span if start and end exist
        if (frm.doc.start && frm.doc.end) {
            let start_time = frappe.datetime.str_to_obj(frm.doc.start);
            let end_time = frappe.datetime.str_to_obj(frm.doc.end);

            // difference in seconds
            let diff_in_seconds = Math.floor((end_time - start_time) / 1000);

            if (diff_in_seconds > 0) {
                let hours = Math.floor(diff_in_seconds / 3600);
                let minutes = Math.floor((diff_in_seconds % 3600) / 60);
                let seconds = diff_in_seconds % 60;

                // format result like "1 Hour 30 Minutes 20 Seconds"
                let result = "";
                if (hours > 0) result += hours + " Hour" + (hours > 1 ? "s " : " ");
                if (minutes > 0) result += minutes + " Minute" + (minutes > 1 ? "s " : " ");
                if (seconds > 0) result += seconds + " Second" + (seconds > 1 ? "s" : "");

                frm.doc.status = "Completed" 
                frm.doc.meeting_span = result.trim();
            } else {
                frm.doc.meeting_span = "0 Seconds";
            }
            // frm.refresh_field("items"); 
            frm.dirty();
            frm.save();
        }
    },
    attach_files(frm){
        if(frm.is_new()){    
            frappe.throw("First Save the Form to attach Documents")
            return
        }
    }
});

frappe.ui.form.on('Field Visit Opportunity', {

    add_comment: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        let d = new frappe.ui.Dialog({
            title: "Add Comment",
            fields: [
                {
                    label: "Comment",
                    fieldname: "comment",
                    fieldtype: "Small Text",
                    reqd: 1
                }
            ],

            primary_action_label: "Save",

            primary_action(values) {

                frm.call({
                    doc: frm.doc,
                    method: "add_opportunity_comment",
                    args: {
                        opportunity_id: row.opportunity_id,
                        content: values.comment
                    },
                    callback: function() {
                        frappe.msgprint("Comment Added");
                    }
                });

                d.hide();

            }

        });

        d.show();

    }

});
