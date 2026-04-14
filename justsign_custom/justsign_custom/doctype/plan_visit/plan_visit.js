// Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Plan Visit", {
	add_data(frm) {
        if(!frm.doc.doctype_name){
             frappe.throw("Please fill all mandatory filters: Doctype Name, From Date, and To Date.");
        }
         frm.call({
            method:"add_items_child", 
            doc:frm.doc,
            freeze: true,  
            callback: function(r) {
                if (!r.exc) {
 
                    frm.set_value("doctype_name", "");
                    frm.set_value("territory", "");
                    frm.set_value("brand", ""); 
                    frm.set_value("customer_group", "");
                    frm.set_value("prospect_customer_group", "");
                }
            }
        })      
	},
    id(frm){
        if (!frm.doc.id || !frm.doc.doctype_name || frm.__single_record_call_in_progress) {
            return;
        }

        frm.__single_record_call_in_progress = true;
        frm.call({
            method: "single_record",
            doc: frm.doc,
            callback: function(r) {
                if (!r.exc) {
                    frm.set_value("id", "");
                    frm.set_value("doctype_name", "");
                }
            }
        }).always(() => {
            frm.__single_record_call_in_progress = false;
        })
    }    
});
    
