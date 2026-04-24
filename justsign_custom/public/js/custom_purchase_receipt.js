(() => {
	const PATCH_FLAG = "justsign_custom_rejected_purchase_uom_patch";
	const FORM_PATCH_FLAG = "justsign_custom_purchase_receipt_patch";

	const get_entries_total_qty = (entries) => {
		return (entries || []).reduce((total, row) => total + Math.abs(flt(row.qty) || 1.0), 0);
	};

	const should_use_purchase_uom_for_bundle = (item) => {
		if (!item) {
			return false;
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

	const patch_selector = () => {
		if (
			!erpnext?.SerialBatchPackageSelector ||
			erpnext.SerialBatchPackageSelector.prototype[PATCH_FLAG]
		) {
			return !!erpnext?.SerialBatchPackageSelector;
		}

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

		erpnext.SerialBatchPackageSelector.prototype[PATCH_FLAG] = true;
		return true;
	};

	const patch_buying_controller = () => {
		if (
			!erpnext?.buying?.BuyingController ||
			erpnext.buying.BuyingController.prototype[PATCH_FLAG]
		) {
			return !!erpnext?.buying?.BuyingController;
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
				item.use_purchase_uom_for_rejected_bundle = false;

				const selector_item = {
					...item,
					rejected_qty:
						Math.abs(flt(item.rejected_qty || item.qty)) *
						flt(item.conversion_factor || 1, precision("conversion_factor", item)),
				};

				new erpnext.SerialBatchPackageSelector(me.frm, selector_item, (bundle) => {
					if (!bundle) {
						return;
					}

					let qty = Math.abs(bundle.total_qty);
					if (doc.is_return) {
						qty = qty * -1;
					}

					let update_values = {
						rejected_serial_and_batch_bundle: bundle.name,
						use_serial_batch_fields: 0,
						rejected_qty:
							qty / flt(item.conversion_factor || 1, precision("conversion_factor", item)),
					};

					if (bundle.warehouse) {
						update_values.rejected_warehouse = bundle.warehouse;
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

				const selector = new erpnext.SerialBatchPackageSelector(me.frm, item, (bundle) => {
					if (!bundle) {
						return;
					}

					let qty = Math.abs(bundle.total_qty);
					if (doc.is_return) {
						qty = qty * -1;
					}

					let update_values = {
						serial_and_batch_bundle: bundle.name,
						use_serial_batch_fields: 0,
						qty: qty / flt(item.conversion_factor || 1, precision("conversion_factor", item)),
					};

					if (bundle.warehouse) {
						update_values.warehouse = bundle.warehouse;
					}

					frappe.model.set_value(item.doctype, item.name, update_values);
				});

				selector.qty = Math.abs(flt(item.qty));
			});
		};

		erpnext.buying.BuyingController.prototype[PATCH_FLAG] = true;
		return true;
	};

	const install_patch = () => patch_selector() && patch_buying_controller();

	const queue_patch_retry = () => {
		if (install_patch()) {
			return;
		}

		setTimeout(install_patch, 0);
	};

	queue_patch_retry();

	frappe.ui.form.on("Purchase Receipt", {
		setup() {
			queue_patch_retry();
		},
		refresh(frm) {
			if (!frm[FORM_PATCH_FLAG]) {
				frm[FORM_PATCH_FLAG] = true;
			}

			queue_patch_retry();
		},
	});
})();
