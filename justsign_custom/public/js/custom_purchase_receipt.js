(() => {
	if (!window.erpnext?.buying?.BuyingController) {
		return;
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
})();
