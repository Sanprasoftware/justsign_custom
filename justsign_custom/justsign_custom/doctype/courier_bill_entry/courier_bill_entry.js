// Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Courier Bill Entry", {
    async attach(frm) {
        if (!frm.doc.attach) {
            frappe.msgprint("Please attach an Excel file first.");
            return;
        } 
  
        await frm.call({
            method: "attch_excel_file",
            doc: frm.doc,
            freeze: true,
            callback() {
                frm.refresh_field("items");
            }
        });
    },  

   
    async click(frm) {
        await frm.call({
            method: "match_sales_invoices",
            doc: frm.doc,
            freeze: true,
            callback(r) {
                frm.refresh_field("items");
                // frm.trigger("filter_transporter_rows");
            }
        });
    },

    //  filter_transporter_rows(frm) {
    //     const selectedTransporter = frm.doc.transporter;

    //     const matching_rows = frm.doc.items.filter(row => row.transporter_name === selectedTransporter);

    //     frm.clear_table("items");

    //     matching_rows.forEach(row => {
    //         let new_row = frm.add_child("items");
    //         Object.assign(new_row, row);
    //     });

    //     frm.refresh_field("items");
    // }
});
