frappe.ui.form.on("Lead Campaign", {
    add(frm) {
        if (!frm.doc.document_type || !frm.doc.form_date || !frm.doc.to_date) {
            frappe.msgprint("Please fill all mandatory filters: Document Type, From Date, and To Date.");
            return;
        }

      
        // Clear all related child tables
        frm.clear_table("lead");
        frm.clear_table("customer");  
        frm.clear_table("prospect");   
        frm.clear_table("quotation");  
        frm.clear_table("opportunity");
        frm.clear_table("territorys");

        frm.call({
            method:"get_data", 
            doc:frm.doc,
            freeze: true
        })    
         
    }  
});