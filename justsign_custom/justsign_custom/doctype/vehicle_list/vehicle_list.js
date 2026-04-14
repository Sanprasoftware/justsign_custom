// Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle List Item", {
    async item_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code) {
            try {
                console.log("Call")
                let item = await frappe.db.get_doc('Item', row.item_code);
                if (item.item_group === "PPF") {
                    console.log("Call1")
                    let item_group = await frappe.db.get_doc('Item Group', item.item_group);
                    if (item_group.custom_qty) {
                        console.log(item_group.custom_qty)
                        frappe.model.set_value(cdt, cdn, 'qty', item_group.custom_qty);
                        frm.refresh_field('items'); // Refresh the child table UI
                    }
                }
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        }
    }
});
