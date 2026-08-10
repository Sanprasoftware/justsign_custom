frappe.ui.form.on("Journal Entry", {
    onload(frm) {
        if (frm.is_new()) {
            setTimeout(() => {
                frm.set_value("posting_date", null);
            }, 200);
        }
    }
});