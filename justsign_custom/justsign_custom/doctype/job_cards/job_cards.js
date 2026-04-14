// Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Cards", {
	refresh(frm) {  
        frm.add_custom_button(__('Add Vehicle Checklist'), function () {
            frappe.model.with_doctype('Vehicle Checklist Log', function () {
                let customer_doc = frappe.model.get_new_doc('Vehicle Checklist Log');
                customer_doc.delivery_not_id = frm.doc.name;
                customer_doc.vehicle_no = frm.doc.vehicle_details;
                frappe.set_route('Form', 'Vehicle Checklist Log', customer_doc.name);
            });
        },);

        if (!frm.doc.__islocal && frm.doc.status !== "In Progress" && frm.doc.status !== "Completed" && frm.doc.status == "Acknowledge") {
            frm.add_custom_button(__('Start'), async function() {
                await frm.set_value('status', 'In Progress');
                await frm.save();
                await frm.reload_doc()
            }).addClass('btn-primary');
        } 
        
        // if (!frm.doc.status) {
        //     frm.add_custom_button(__('Acknowledge'), async function() {
        //         await frm.set_value('status', 'Acknowledge');
        //         await frm.save();
        //         await frm.reload_doc()
        //     }).addClass('btn-success');
        // }
                
                // Add 'Completed' button
                if (frm.doc.status === "In Progress") {
                    frm.add_custom_button(__('Completed'),async function() {
                        await frm.set_value('status', 'Completed');
                        await frm.save();
                        await frm.reload_doc()
            }).addClass('btn-success');
        }
        frm.add_custom_button(__('Make Payment'), function () {
            frappe.model.with_doctype('Payment Entry', function () {
                let pay_doc = frappe.model.get_new_doc('Payment Entry');
                pay_doc.custom_job_cards = frm.doc.name;
                frappe.set_route('Form', 'Payment Entry', pay_doc.name);
            });
        },);
	},
    // after_save: function(frm) {
    //     if (frm.doc.customer) {
    //         frappe.db.get_value("Customer", frm.doc.customer, "custom_installer")
    //             .then(r => {
    //                 if (r && r.message) {
    //                     // frappe.throw(r.message.custom_installer);
    //                     frappe.db.set_value("Job Cards", frm.doc.name, "installer", r.message.custom_installer);
    //                 }
    //             })
    //     }
    // },
    // after_save: function(frm) {
    //     if (frm.doc.status == "Completed" && frm.doc.document_type == "Sales Order" ) 
    //     {
    //         frappe.db.set_value("Sales Order", frm.doc.document_id, "custom_job_cards", frm.doc.name);
    //     }
    //     else if (frm.doc.status == "Completed" && frm.doc.document_type == "Delivery Note") 
    //     {
    //         frappe.db.set_value("Delivery Note", frm.doc.document_id, "custom_job_card", frm.doc.name);
    //     }
    // },
    // before_delete: function(frm) {
    //     if (frm.doc.status == "Completed" && frm.doc.document_type == "Sales Order" ) 
    //     {
    //         frappe.db.set_value("Sales Order", frm.doc.document_id, "custom_job_cards", '');
    //     }
    //     else if (frm.doc.status == "Completed" && frm.doc.document_type == "Delivery Note") 
    //     {
    //         frappe.db.set_value("Delivery Note", frm.doc.document_id, "custom_job_card", '');
    //     }
    // }
});



