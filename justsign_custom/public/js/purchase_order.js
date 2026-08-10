frappe.ui.form.on('Purchase Order', {
    onload(frm) {
        if (frm.is_new()) {
            setTimeout(() => {
                frm.set_value("transaction_date", null);
            }, 200);
        }
    }
});
