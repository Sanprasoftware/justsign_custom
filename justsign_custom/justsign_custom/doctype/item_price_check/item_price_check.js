// Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Price Check", {
	item(frm) {
        frappe.call({
            method: "get_item_price_list_item_wise",
            doc: frm.doc,
            callback: function(r){
                if(r.message){
                    frm.refresh_field("table_otqy");
                }
            }
        })
	},
    item_group(frm) {
        frappe.call({
            method: "get_item_price_list_item_group_wise",
            doc: frm.doc,
            callback: function(r){
                if(r.message){
                    frm.refresh_field("table_otqy");
                }
            }
        })
	},
});  
