/* global frappe, __ */

// Account-level TDS is calculated on the server during the normal Purchase
// Invoice save lifecycle. This client code only keeps the editable tax row in
// sync with its Account master and removes stale generated rows before save.
frappe.ui.form.on("Purchase Taxes and Charges", {
	account_head(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.apply_tds) return;

		set_tds_category_from_account(frm, cdt, cdn);
	},

	apply_tds(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.apply_tds) {
			frappe.model.set_value(cdt, cdn, "tax_withholding_category", "");
			remove_generated_charge_tds_rows(frm);
			return;
		}

		set_tds_category_from_account(frm, cdt, cdn);
	},
});

function set_tds_category_from_account(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	if (!row.account_head) {
		frappe.model.set_value(cdt, cdn, "tax_withholding_category", "");
		return;
	}
	const account = row.account_head;

	frappe.call({
		method: "justsign_custom.public.py.purchase_invoice.get_account_tds_defaults_for_row",
		args: { account },
		callback(response) {
			const current_row = locals[cdt][cdn];
			if (!current_row || !current_row.apply_tds || current_row.account_head !== account) return;

			const defaults = response.message || {};
			if (defaults.tax_withholding_category) {
				frappe.model.set_value(cdt, cdn, "tax_withholding_category", defaults.tax_withholding_category);
			} else {
				frappe.model.set_value(cdt, cdn, "tax_withholding_category", "");
				frappe.msgprint({
					message: __(
						"Set a Tax Withholding Category on Account {0} before applying TDS to this charge.",
						[account]
					),
					indicator: "orange",
				});
			}
		},
	});
}

function remove_generated_charge_tds_rows(frm) {
	const taxes = frm.doc.taxes || [];
	if (!taxes.some((row) => row.custom_is_freight_tds_row)) return;

	const active_categories = new Set(
		taxes
			.filter((row) => row.apply_tds && !row.custom_is_freight_tds_row)
			.map((row) => row.tax_withholding_category)
			.filter(Boolean)
	);
	const retained_rows = taxes.filter(
		(row) => !row.custom_is_freight_tds_row || active_categories.has(row.tax_withholding_category)
	);
	if (retained_rows.length === taxes.length) return;

	// Use the standard grid-table pattern so row indexes and the form's dirty
	// state stay correct after a deduction row is removed.
	frm.clear_table("taxes");
	retained_rows.forEach((row) => frm.add_child("taxes", row));
	frm.refresh_field("taxes");
}
