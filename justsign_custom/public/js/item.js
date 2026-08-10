frappe.ui.form.on('Item', {
	item_group(frm) {
		frappe.db.get_value("Item Group", frm.doc.item_group, "custom__is_service_group", (r) => {
            if (r && r.custom__is_service_group == 1) {
                frm.set_value("is_stock_item", 0);
                frm.set_df_property("is_stock_item", "read_only", 1);
                frm.set_df_property("is_fixed_asset", "read_only", 1);
            }             
	    }
    )}
})
