frappe.ui.form.on('Sales Order', {
    custom_shipper(frm) {
        apply_freight_rule(frm);
    },
    custom_mode(frm) {
        apply_freight_rule(frm);
    },
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
        if (frm.doc.customer) {
            frm.set_query('custom_select_package', function() {
                return {
                    filters: {
                        customer: frm.doc.customer  // Match customer field
                    }
                };
            });
            frm.set_query('custom_vehicle_details', function() {
                return {
                    filters: {
                        customer: frm.doc.customer  // Match customer field
                    }
                };
            });
        }
        if (frm.doc.docstatus == 1)
        {
            frm.add_custom_button(__('Create Job Card'), async function () {
                frappe.model.with_doctype('Job Cards', async function () {
                    let job_card_doc = frappe.model.get_new_doc('Job Cards');
                    job_card_doc.document_type = "Sales Order";
                    job_card_doc.document_id = frm.doc.name;
                    job_card_doc.customer = frm.doc.customer;
                    job_card_doc.vehicle_details = frm.doc.custom_vehicle_details;

                    await frappe.call({ 
                        method: 'frappe.client.get',
                        args: {
                            doctype: 'Sales Order',
                            name: frm.doc.name // Fetch details for the current Sales Order
                        },
                        callback: async function (response) {
                            if (response.message) {
                                let sales_order_doc = response.message;

                                // Clear existing items in the Job Card (child table)
                                job_card_doc.items = [];

                                // Add items from the Sales Order to the Job Card
                                sales_order_doc.items.forEach(row => {
                                    let child = job_card_doc.items.push({
                                        item_code: row.item_code,
                                        item_name: row.item_name,
                                        uom: row.uom,
                                        qty: row.qty
                                    });
                                });
                                frappe.set_route('Form', 'Job Cards', job_card_doc.name);
                            }
                        }
                    });
                });
            });
        }
    
    },
});


frappe.ui.form.on('Sales Order Item', {
    item_code: async function (frm, cdt, cdn) {
        let row = locals[cdt][cdn]; // Get the child row
        if (!row.item_code) return;

        setTimeout(() => apply_freight_rule(frm), 700);

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
        frm.call({
            // method:"justsign_custom.custom_pyfile.custom_python.custom_product_bundel_itm",
            method:"justsign_custom.custom_pyfile.custom_python.custom_bud_item",
            args:{
                doc : frm.doc,
                item_code : row.item_code
            },
            callback:(r)=>{
                frm.clear_table("custom_items_bundle")
                r.message.forEach(buditem => {
                    const child = frm.add_child('custom_items_bundle')
                    child.item_code = buditem.item_code,
                    child.qty = buditem.qty,
                    child.description = buditem.description
                    child.uom = buditem.uom
                    child.parent_item = buditem.parent_item
                })
                frm.refresh_fields()
            }
        })
    },
    qty(frm) {
        apply_freight_rule(frm);
    },
    rate(frm) {
        apply_freight_rule(frm);
    },
    amount(frm) {
        apply_freight_rule(frm);
    },
    items_remove(frm){
        apply_freight_rule(frm);
        frm.call({
            method:"justsign_custom.custom_pyfile.custom_python.custom_bud_item",
            args:{
                doc : frm.doc,
                item_code : "None", 
            },
            callback:(r)=>{
                frm.clear_table("custom_items_bundle")
                r.message.forEach(buditem => {
                    const child = frm.add_child('custom_items_bundle')
                    child.item_code = buditem.item_code,
                    child.qty = buditem.qty,
                    child.description = buditem.description
                    child.uom = buditem.uom
                    child.parent_item = buditem.parent_item
                })
                frm.refresh_fields()
            }
        })
    }
});

function apply_freight_rule(frm) {
    if (frm.doc.docstatus !== 0) {
        return;
    }

    clearTimeout(frm.freight_rule_timeout);
    frm.freight_rule_timeout = setTimeout(() => {
        frappe.call({
            method: "justsign_custom.public.py.sales_order.get_freight_rule_result",
            args: {
                doc: frm.doc
            },
            freeze: false,
            callback: function(r) {
                if (!r.message) {
                    return;
                }

                frm.clear_table("taxes");
                (r.message.taxes || []).forEach(tax => {
                    let row = frm.add_child("taxes");
                    Object.keys(tax).forEach(fieldname => {
                        if (!["doctype", "name", "parent", "parentfield", "parenttype", "idx"].includes(fieldname)) {
                            row[fieldname] = tax[fieldname];
                        }
                    });
                });

                if (frm.fields_dict.custom_freight_amount) {
                    frm.set_value("custom_freight_amount", r.message.freight_amount || 0);
                }

                frm.refresh_field("taxes");
                frm.script_manager.trigger("calculate_taxes_and_totals");
            }
        });
    }, 300);
}

frappe.ui.form.on('Custom Bundle Item', {
    item_code(frm, cdt, cdn) {
        set_custom_bundle_batch_query(frm, cdt, cdn);
    },
    warehouse(frm, cdt, cdn) {
        set_custom_bundle_batch_query(frm, cdt, cdn);
    }
});

function set_custom_bundle_batch_query(frm, cdt, cdn) {
    const row = locals[cdt][cdn] || {};
    const warehouse = row.warehouse || frm.doc.set_warehouse;
    const item_code = row.item_code;

    frm.fields_dict.custom_items_bundle.grid.get_field('batch').get_query = function (doc, cdt, cdn) {
        const d = locals[cdt][cdn] || {};
        const wh = d.warehouse || frm.doc.set_warehouse;
        const item = d.item_code;

        if (!item) {
            return {};
        }

        return { 
            query: "erpnext.controllers.queries.get_batch_no",
            filters: {
                item_code: item,
                warehouse: wh
            }
        };
    };
}
