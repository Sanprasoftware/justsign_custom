// Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt
let entries = []
frappe.ui.form.on("Vehicle Entry", {
    setup: function(frm){
        frm.set_query("vehicle_number",function(){
            return {
                filters : {
                    name : ["in",entries]
                }
            }
        })
    },
    onload: async function(frm){
        if(frm.doc.mobile_number){
            entries = (await frm.call({
                method:"get_entries",
                doc:frm.doc
            })).message
        }
    },
    check_in: function(frm) {
        const now = frappe.datetime.now_datetime();
        frm.set_value('check_in_time', now);
        frm.set_value('status', 'Check In');
        frm.refresh_field('check_in_time');
    },
    check_out: function(frm) {
        const now = frappe.datetime.now_datetime();
        frm.set_value('check_out_time', now);
        frm.set_value('status', 'Check Out');
        frm.refresh_field('check_out_time');
    },
    // refresh: function(frm) {
    //     frm.add_custom_button(__('Create Lead'), function() {
    //         frappe.new_doc('Lead', {
    //             custom_vehicle_entry_id: frm.doc.name
    //         });
    //     }, __('Action'));
    // },
    mobile_number: function (frm) {
        frm.call({
            method: 'getvehino',
            doc: frm.doc,
            callback: function (response) {
                if (response.message && response.message.length) {
                    let vehicle_list = response.message;
                    frm.set_query("vehicle_number", function () {
                        return {
                            filters: [["name", "in", vehicle_list]] 
                        };
                    });
                    frm.refresh_field("vehicle_number");
                }
            }
        });
        frm.call({
            method:'get_lead',
            doc: frm.doc
        });
    },
    vehicle_number: function (frm) {	
        frm.call({
            method:'get_vehicle',
            doc: frm.doc
        });
	},
    create_veh: function (frm) {
        frappe.call({
            method: 'frappe.client.insert',
            args: {
                doc: {
                    doctype: 'Customer Wise Vehicle',
                    document_type: "Lead",
                    customer: frm.doc.lead,
                    vehicle_no: frm.doc.vehicle_number,
                    mobile_number: frm.doc.mobile_number
                }
            },
            callback: function(response) {
                if (response.message) {
                    let vehi_id = response.message.name; // Get created Lead ID
                    frappe.msgprint(__('Vehicle Created Successfully: {0}', [vehi_id]));
                }
            }
        });


        // if (frm.doc.lead) {
        //     frappe.model.with_doctype('Customer Wise Vehicle', function () {
        //         let customer_doc = frappe.model.get_new_doc('Customer Wise Vehicle');
        //         customer_doc.document_type = "Lead";
        //         customer_doc.customer = frm.doc.lead;
        //         customer_doc.vehicle_no = frm.doc.vehicle_number;
        //         customer_doc.mobile_number = frm.doc.mobile_number;
    
        //         // Auto-save the document
        //         frappe.db.insert(customer_doc).then(doc => {
        //             frappe.msgprint(__('Customer Wise Vehicle created successfully'));
        //             frappe.set_route('Form', 'Customer Wise Vehicle', doc.name);
        //         }).catch(err => {
        //             frappe.msgprint(__('Failed to create Customer Wise Vehicle'));
        //             console.error(err);
        //         });
        //     });
        // }
    }
    
});

frappe.ui.form.on('Vehicle Entry', {
    create_vehicle: function(frm) {
        let dialog = new frappe.ui.Dialog({
            title: 'Enter Details',
            fields: [
                {
                    label: 'Mobile Number',
                    fieldname: 'mobile_number',
                    fieldtype: 'Data',
                    reqd: 1
                },
                {
                    label: 'Vehicle Number',
                    fieldname: 'vehicle_number',
                    fieldtype: 'Data',
                    reqd: 1
                },
                {
                    label: 'Full Name',
                    fieldname: 'full_name',
                    fieldtype: 'Data',
                    reqd: 1
                }
            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                // Step 1: Create Lead Record
                frappe.call({
                    method: 'frappe.client.insert',
                    args: {
                        doc: {
                            doctype: 'Lead',
                            mobile_no: values.mobile_number,
                            first_name: values.full_name,
                            custom_vehicle_no: values.vehicle_number,
                            type: 'End User',
                            source: 'Walk In',
                            custom_brand: 'P91 CC'
                        }
                    },
                    callback: function(response) {
                        if (response.message) {
                            let lead_id = response.message.name; // Get created Lead ID
                            frappe.msgprint(__('Lead Created Successfully: {0}', [lead_id]));

                            // Step 2: Create Customer Wise Vehicle Record
                            frappe.call({
                                method: 'frappe.client.insert',
                                args: {
                                    doc: {
                                        doctype: 'Customer Wise Vehicle',
                                        vehicle_no: values.vehicle_number, // Map vehicle_no from Lead
                                        document_type: 'Lead',
                                        customer: lead_id, // Set Lead ID
                                        mobile_number: values.mobile_number
                                    }
                                },
                                callback: function(res) {
                                    if (res.message) {
                                        let customer_wise_vehicle_id = res.message.name;
                                        frappe.msgprint(__('Customer Wise Vehicle Created Successfully: {0}', [customer_wise_vehicle_id]));

                                        // Step 3: Update Vehicle Entry Form
                                        frm.set_value('vehicle_number', customer_wise_vehicle_id);
                                        frm.set_value('mobile_number', values.mobile_number);
                                        // frm.set_value('customer_wise_vehicle', customer_wise_vehicle_id);
                                    }
                                }
                            });
                        }
                    }
                });

                dialog.hide();
            }
        });
        dialog.show();
    }
});
