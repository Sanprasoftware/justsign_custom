// Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Completion", {
    on_submit: function(frm) {
        if (frm.doc.delivery_not_id) {
            frappe.db.set_value("Delivery Note", frm.doc.delivery_not_id, "custom_job_completion_id", frm.doc.name)
                .then(response => {
                    if (!response.exc) {
                        frappe.msgprint(__('Delivery Note updated successfully!'));
                    }
                });
        }
    },
});
