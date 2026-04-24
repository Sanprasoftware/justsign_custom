(() => {
	if (!window.erpnext?.buying?.BuyingController) {
		return;
	}

	const get_entries_total_qty = (entries) => {
		return (entries || []).reduce((total, row) => total + Math.abs(flt(row.qty) || 1.0), 0);
	};

	const should_use_purchase_uom_for_bundle = (item) => {
		if (!item) {
			return false;
		}

		if (item.is_rejected) {
			return !!item.use_purchase_uom_for_rejected_bundle;
		}

		return !!item.use_purchase_uom_for_bundle;
	};

	const get_expected_bundle_qty = (item) => {
		if (!item) {
			return 0;
		}

		return Math.abs(flt(item.is_rejected ? item.rejected_qty : item.qty));
	};

	const normalize_bundle_entries = (selector, entries) => {
		const item = selector.item;

		if (
			!should_use_purchase_uom_for_bundle(item) ||
			flt(item.conversion_factor || 1) === 1
		) {
			return entries;
		}

		const expected_qty = get_expected_bundle_qty(item);
		const total_qty = get_entries_total_qty(entries);
		const conversion_factor = flt(
			item.conversion_factor || 1,
			precision("conversion_factor", item)
		);

		if (!expected_qty || !conversion_factor) {
			return entries;
		}

		const expected_stock_qty = flt(
			expected_qty * conversion_factor,
			precision("stock_qty", item)
		);

		if (Math.abs(total_qty - expected_stock_qty) > 0.01) {
			return entries;
		}

		return entries.map((row) => ({
			...row,
			qty: flt(flt(row.qty || 1.0) / conversion_factor, precision("qty", item)),
		}));
	};

	if (
		erpnext.SerialBatchPackageSelector &&
		!erpnext.SerialBatchPackageSelector.prototype
			.justsign_custom_rejected_purchase_uom_patch
	) {
		const original_update_bundle_entries =
			erpnext.SerialBatchPackageSelector.prototype.update_bundle_entries;

		erpnext.SerialBatchPackageSelector.prototype.update_bundle_entries = function () {
			const original_get_values = this.dialog.get_values.bind(this.dialog);

			this.dialog.get_values = (...args) => {
				const values = original_get_values(...args);

				if (values?.entries) {
					values.entries = normalize_bundle_entries(this, values.entries);
				}

				return values;
			};

			try {
				return original_update_bundle_entries.call(this);
			} finally {
				this.dialog.get_values = original_get_values;
			}
		};

		erpnext.SerialBatchPackageSelector.prototype.justsign_custom_rejected_purchase_uom_patch =
			true;
	}

	erpnext.buying.BuyingController.prototype.add_serial_batch_for_rejected_qty = function (
		doc,
		cdt,
		cdn
	) {
		let item = locals[cdt][cdn];
		let me = this;
		let fields = ["has_batch_no", "has_serial_no"];

		frappe.db.get_value("Item", item.item_code, fields).then((r) => {
			if (!(r.message && (r.message.has_batch_no || r.message.has_serial_no))) {
				return;
			}

			fields.forEach((field) => {
				item[field] = r.message[field];
			});

			item.type_of_transaction = doc.is_return ? "Outward" : "Inward";
			item.is_rejected = true;
			item.use_purchase_uom_for_rejected_bundle = true;

			new erpnext.SerialBatchPackageSelector(me.frm, item, (r) => {
				if (!r) {
					return;
				}

				let qty = Math.abs(r.total_qty);
				if (doc.is_return) {
					qty = qty * -1;
				}

				let update_values = {
					rejected_serial_and_batch_bundle: r.name,
					use_serial_batch_fields: 0,
					rejected_qty: qty,
				};

				if (r.warehouse) {
					update_values.rejected_warehouse = r.warehouse;
				}

				frappe.model.set_value(item.doctype, item.name, update_values);
			});
		});
	};

	erpnext.buying.BuyingController.prototype.add_serial_batch_bundle = function (doc, cdt, cdn) {
		let item = locals[cdt][cdn];
		let me = this;
		let fields = ["has_batch_no", "has_serial_no"];

		frappe.db.get_value("Item", item.item_code, fields).then((r) => {
			if (!(r.message && (r.message.has_batch_no || r.message.has_serial_no))) {
				return;
			}

			fields.forEach((field) => {
				item[field] = r.message[field];
			});

			item.type_of_transaction = item.qty > 0 ? "Inward" : "Outward";
			item.is_rejected = false;
			item.use_purchase_uom_for_bundle = true;

			new erpnext.SerialBatchPackageSelector(me.frm, item, (r) => {
				if (!r) {
					return;
				}

				let qty = Math.abs(r.total_qty);
				if (doc.is_return) {
					qty = qty * -1;
				}

				let update_values = {
					serial_and_batch_bundle: r.name,
					use_serial_batch_fields: 0,
					qty: qty / flt(item.conversion_factor || 1, precision("conversion_factor", item)),
				};

				if (r.warehouse) {
					update_values.warehouse = r.warehouse;
				}

				frappe.model.set_value(item.doctype, item.name, update_values);
			});
		});
	};
})();
