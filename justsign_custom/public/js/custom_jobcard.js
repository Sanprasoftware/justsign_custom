frappe.ui.form.on('Job Card', {
    refresh: async function(frm) {
            frm.add_custom_button(__('Job Completion'), function () {
                frappe.model.with_doctype('Job Completion', function () {
                    let customer_doc = frappe.model.get_new_doc('Job Completion');
                    customer_doc.document_type = "Job Card";
                    customer_doc.delivery_not_id = frm.doc.name;
                    customer_doc.vehicle_no = frm.doc.custom_vehicle_details;
                    frappe.set_route('Form', 'Job Completion', customer_doc.name);
                });
            },);
        }
});