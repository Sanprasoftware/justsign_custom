frappe.ui.form.on('Quotation', {
    custom_vehicle_details: async function(frm) {
        if (frm.doc.custom_vehicle_details) {
            // Get the selected vehicle from 'Customer Wise Vehicle'
            const select_vehicle = (await frappe.db.get_value("Customer Wise Vehicle", frm.doc.custom_vehicle_details, "select_vehicle")).message.select_vehicle;

            if (select_vehicle) {
                // Get the category linked to the selected vehicle
                const category = (await frappe.db.get_value("Vehicle List", select_vehicle, "category")).message.category;

                if (category) {
                    // Fetch item list based on category
                    await frappe.call({
                        method: "justsign_custom.justsign_custom.utilities.get_category_items",
                        args: {
                            category: category
                        },
                        callback: function(response) {
                            item_list = response.message; 
                            console.log(item_list);
                        }
                    });
                }
            }
        } else {
            item_list = [];
            console.log("No vehicle selected");
        }
        frm.refresh_fields();
        
        setTimeout(() => {
            frm.set_query("item_code", "items", function(doc, cdt, cdn) {
                let d = locals[cdt][cdn];
                return {
                    filters: {
                        'item_code': ["in", item_list]
                    }
                };
            });
        }, 100);
    },
    refresh: async function(frm) {
        if (frm.doc.party_name) {
            frm.set_query('custom_vehicle_details', function() {
                return {
                    filters: {
                        customer: frm.doc.party_name  // Match customer field
                    }
                };
            });
        }    
    },
});


frappe.ui.form.on('Quotation Item', {
    
    item_code: async function (frm, cdt, cdn) {
        let row = locals[cdt][cdn]; // Get the child row
        if (!row.item_code) return;

        // Fetch the selected vehicle from "Customer Wise Vehicle"
        let veh_type_res = await frappe.db.get_value("Customer Wise Vehicle", { name: frm.doc.custom_vehicle_details }, "select_vehicle");
        if (!veh_type_res || !veh_type_res.message || !veh_type_res.message.select_vehicle) return;

        let veh_type = veh_type_res.message.select_vehicle;

        // Fetch vehicle details from "Vehicle List"
        let veh_data_res = await frappe.db.get_value("Vehicle List", { name: veh_type }, ["item_group", "qty"]);
        if (!veh_data_res || !veh_data_res.message) return;

        let veh_group = veh_data_res.message.item_group;
        let veh_qty = veh_data_res.message.qty;

        // Fetch item details
        let item = await frappe.db.get_doc('Item', row.item_code);
        let qty_to_set = (item.item_group === veh_group) ? veh_qty : 1;

        frappe.model.set_value(cdt, cdn, 'qty', qty_to_set);

        // Fetch package amount from "Packages"
        let pkg_type_res = await frappe.db.get_value("Packages", { name: row.item_code }, "package_amount");

        if (pkg_type_res && pkg_type_res.message && pkg_type_res.message.package_amount) {
            let package_amount = pkg_type_res.message.package_amount;

            // Override standard rate calculation after a short delay
            setTimeout(() => {
                frappe.model.set_value(cdt, cdn, 'rate', package_amount);
                frm.refresh_field('items'); // Refresh the child table UI
            }, 500); // Delay ensures our value is set last
        }
    }
});


