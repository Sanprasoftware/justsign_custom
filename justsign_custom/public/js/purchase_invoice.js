frappe.ui.form.on('Purchase Invoice', {
    onload: function(frm) {
        setup_purchase_tax_tds_grid(frm);
        setup_purchase_tax_charge_type_sync(frm);
    },
    onload_post_render: async function(frm) {
        if (frm.is_new() && !frm.__posting_date_cleared) {
            frm.__posting_date_cleared = true;
            frm.set_df_property('posting_date', 'hidden', 0);
            await frm.set_value('set_posting_time', 1);
            await frm.set_value('posting_date', '');
            frm.set_df_property('posting_date', 'read_only', 0);
            frm.refresh_field('posting_date');
        }
    },
    refresh: function (frm) {
        setup_purchase_tax_tds_grid(frm);
        setup_purchase_tax_charge_type_sync(frm);
        refresh_purchase_tax_tds_rows(frm);

        frm.fields_dict.custom_discount.grid.get_field("purchase_invoice_id").get_query = function() {
            return {
                filters: {
                    supplier: frm.doc.supplier,
                    status: ["in", ["Unpaid", "Overdue", "Partly Paid"]],
                }
            };
        };
    },
    supplier: function (frm) {
        frm.fields_dict.custom_discount.grid.get_field("purchase_invoice_id").get_query = function() {
            return {
                filters: {
                    supplier: frm.doc.supplier,
                    status: ["in", ["Unpaid", "Overdue", "Partly Paid"]],
                    
                }
            };
        };
    },

});

frappe.ui.form.on("Purchase Taxes and Charges", {
    account_head: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.account_head) {
            frappe.model.set_value(cdt, cdn, {
                apply_tds: 0,
                tax_withholding_category: "",
            });
            return;
        }

        get_account_tds_defaults(row.account_head, function(values) {
                if (!values || !values.apply_tds) {
                    frappe.model.set_value(cdt, cdn, {
                        apply_tds: 0,
                        tax_withholding_category: "",
                    });
                    refresh_purchase_tax_tds_rows(frm, false);
                    return;
                }

                if (!get_purchase_tax_tds_amount(row)) {
                    frappe.model.set_value(cdt, cdn, {
                        apply_tds: 0,
                        tax_withholding_category: "",
                    });
                    refresh_purchase_tax_tds_rows(frm, false);
                    return;
                }

                frappe.model.set_value(cdt, cdn, "apply_tds", 1);

                if (values.tax_withholding_category && !row.tax_withholding_category) {
                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "tax_withholding_category",
                        values.tax_withholding_category
                    );
                }

                refresh_purchase_tax_tds_rows(frm, false);
            }
        );
    },

    apply_tds: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.apply_tds) {
            frappe.model.set_value(cdt, cdn, "tax_withholding_category", "");
            refresh_purchase_tax_tds_rows(frm);
            return;
        }

        set_purchase_tax_tds_category_from_account(frm, cdt, cdn);
    },

    tax_amount: function(frm, cdt, cdn) {
        set_purchase_tax_tds_from_amount(frm, cdt, cdn);
    },

    tax_amount_after_discount_amount: function(frm, cdt, cdn) {
        set_purchase_tax_tds_from_amount(frm, cdt, cdn);
    },
});

function setup_purchase_tax_tds_grid(frm) {
    if (frm.__purchase_tax_tds_grid_setup) {
        return;
    }

    frm.__purchase_tax_tds_grid_setup = true;
    $(frm.wrapper).on("grid-row-render", function(_event, grid_row) {
        if (grid_row.grid.df.fieldname !== "taxes") {
            return;
        }

        setTimeout(function() {
            sync_purchase_tax_charge_type(grid_row);
        }, 0);
        toggle_purchase_tax_tds_row(grid_row);
    });
}

function sync_purchase_tax_charge_type(grid_row) {
    if (grid_row.doc.doctype !== "Purchase Taxes and Charges") {
        return;
    }

    let charge_type_field = null;
    try {
        charge_type_field = grid_row.get_field("charge_type");
    } catch {
        return;
    }

    if (!charge_type_field || charge_type_field.__js_charge_type_sync) {
        return;
    }

    charge_type_field.__js_charge_type_sync = true;
    charge_type_field.$input.on("change select-change", function() {
        const value = charge_type_field.get_input_value();
        if (value && grid_row.doc.charge_type !== value) {
            frappe.model.set_value(
                grid_row.doc.doctype,
                grid_row.doc.name,
                "charge_type",
                value
            );
        }
    });
}

function setup_purchase_tax_charge_type_sync(frm) {
    if (frm.__purchase_tax_charge_type_sync) {
        return;
    }

    frm.__purchase_tax_charge_type_sync = true;
    $(frm.wrapper).on("change select-change", "[data-fieldname='charge_type']", function() {
        const grid_row = $(this).closest(".grid-row").data("grid_row");
        if (!grid_row || grid_row.grid.df.fieldname !== "taxes") {
            return;
        }

        const row = grid_row.doc;
        const value = $(this).val();
        if (row.doctype === "Purchase Taxes and Charges" && value && row.charge_type !== value) {
            frappe.model.set_value(row.doctype, row.name, "charge_type", value);
        }
    });
}

function refresh_purchase_tax_tds_rows(frm, refresh_grid = true) {
    (frm.doc.taxes || []).forEach(function(row) {
        if (!get_purchase_tax_tds_amount(row)) {
            row.apply_tds = 0;
            row.tax_withholding_category = "";
        } else if (!row.apply_tds && row.tax_withholding_category) {
            row.tax_withholding_category = "";
        }
    });

    (frm.fields_dict.taxes.grid.grid_rows || []).forEach(toggle_purchase_tax_tds_row);
    if (refresh_grid) {
        frm.refresh_field("taxes");
    }
}

function toggle_purchase_tax_tds_row(grid_row) {
    const row = grid_row.doc;
    const can_apply_tds = !!row.account_head && !row.custom_is_freight_tds_row;

    grid_row.toggle_editable("apply_tds", can_apply_tds);
    grid_row.toggle_editable("tax_withholding_category", !!row.apply_tds);
}

function set_purchase_tax_tds_from_amount(frm, cdt, cdn) {
    const row = locals[cdt][cdn];

    if (!get_purchase_tax_tds_amount(row)) {
        frappe.model.set_value(cdt, cdn, {
            apply_tds: 0,
            tax_withholding_category: "",
        });
        refresh_purchase_tax_tds_rows(frm);
        return;
    }

    if (!row.account_head) {
        refresh_purchase_tax_tds_rows(frm);
        return;
    }

    set_purchase_tax_tds_category_from_account(frm, cdt, cdn);
}

function set_purchase_tax_tds_category_from_account(frm, cdt, cdn) {
    const row = locals[cdt][cdn];

    if (!row.account_head) {
        refresh_purchase_tax_tds_rows(frm);
        return;
    }

    get_account_tds_defaults(row.account_head, function(values) {
            frappe.model.set_value(cdt, cdn, "apply_tds", 1);

            if (values.tax_withholding_category) {
                frappe.model.set_value(
                    cdt,
                    cdn,
                    "tax_withholding_category",
                    values.tax_withholding_category
                );
            }

            refresh_purchase_tax_tds_rows(frm);
        }
    );
}

function get_purchase_tax_tds_amount(row) {
    return Math.abs(
        flt(row.base_tax_amount_after_discount_amount)
        || flt(row.base_tax_amount)
        || flt(row.tax_amount_after_discount_amount)
        || flt(row.tax_amount)
    );
}

function get_account_tds_defaults(account, callback) {
    frappe.model.with_doc("Account", account, function() {
        const account_doc = frappe.model.get_doc("Account", account) || {};
        callback({
            apply_tds: cint(account_doc.custom_apply_tds),
            tax_withholding_category: account_doc.custom_tax_withholding_category,
        });
    });
}
