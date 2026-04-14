// // Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
// // For license information, please see license.txt

frappe.ui.form.on("Customer Wise Vehicle", {
    select_vehicle: function(frm) {
        if (!frm.doc.select_vehicle) {
            return;
        }
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Vehicle List',
                name: frm.doc.select_vehicle
            },
            callback: function(response) {
                if (response.message) {
                    let vehicle_doc = response.message;
                    frm.set_value('brand', vehicle_doc.brand);
                    frm.set_value('model', vehicle_doc.model);
                    // frm.set_value('category', vehicle_doc.category);
                    frm.set_value('vehicle_type', vehicle_doc.vehicle_type);

                    frm.clear_table('items');
                    vehicle_doc.items.forEach(row => {
                        let child = frm.add_child('items');
                        child.item = row.item_code;
                        child.item_name = row.item_name;
                        child.uom = row.uom;
                        child.qty = row.qty;
                    });
                    frm.refresh_field('items');
                }
            }
        });
    }
    // refresh: function (frm) {
	// 	// frm.refresh_field('item_ot')		
	// 	frm.call({
	// 		method:'getvehino',
	// 		doc: frm.doc
	// 	});
	// }
});


