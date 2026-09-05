import frappe


CLIENT_SCRIPT_NAME = "Payment Reconciliation Supplier Invoice Debit Note No"


def execute():
	if not frappe.db.table_exists("Client Script"):
		return

	script = get_client_script()

	if frappe.db.exists("Client Script", CLIENT_SCRIPT_NAME):
		doc = frappe.get_doc("Client Script", CLIENT_SCRIPT_NAME)
		doc.script = script
		doc.enabled = 1
		doc.save()
	else:
		frappe.get_doc(
			{
				"doctype": "Client Script",
				"name": CLIENT_SCRIPT_NAME,
				"dt": "Payment Reconciliation",
				"view": "Form",
				"enabled": 1,
				"script": script,
			}
		).insert()

	frappe.clear_cache(doctype="Payment Reconciliation")


def get_client_script():
	return r"""
frappe.ui.form.on("Payment Reconciliation", {
	refresh(frm) {
		setTimeout(() => {
			justsign_custom_replace_get_unreconciled_entries_button(frm);
		}, 0);
		justsign_custom_fetch_supplier_invoice_debit_note_no(frm);
	},
});

function justsign_custom_replace_get_unreconciled_entries_button(frm) {
	if (!frm.doc.receivable_payable_account) {
		return;
	}

	frm.remove_custom_button(__("Get Unreconciled Entries"));
	frm.add_custom_button(__("Get Unreconciled Entries"), () => {
		justsign_custom_get_unreconciled_entries(frm);
	});
	frm.change_custom_button_type(__("Get Unreconciled Entries"), null, "primary");
}

async function justsign_custom_get_unreconciled_entries(frm) {
	frappe.model.clear_table(frm.doc, "allocation");

	const response = await frappe.call({
		method: "justsign_custom.payment_reconciliation.get_unreconciled_entries",
		args: {
			doc: frm.doc,
		},
		freeze: true,
		freeze_message: __("Getting unreconciled entries"),
	});

	["invoices", "payments", "allocation"].forEach((table_field) => {
		frappe.model.clear_table(frm.doc, table_field);
		(response.message?.[table_field] || []).forEach((source_row) => {
			const target_row = frm.add_child(table_field);
			Object.keys(source_row).forEach((fieldname) => {
				if (
					![
						"doctype",
						"name",
						"owner",
						"creation",
						"modified",
						"modified_by",
						"parent",
						"parentfield",
						"parenttype",
						"idx",
						"docstatus",
					].includes(fieldname)
				) {
					target_row[fieldname] = source_row[fieldname];
				}
			});
		});
	});

	await justsign_custom_fetch_supplier_invoice_debit_note_no(frm);
	frm.refresh_fields();
	frm.refresh();

	if (!(frm.doc.payments.length || frm.doc.invoices.length)) {
		frappe.throw({
			message: __("No Unreconciled Invoices and Payments found for this party and account"),
		});
	} else if (!frm.doc.invoices.length) {
		frappe.throw({ message: __("No Outstanding Invoices found for this party") });
	} else if (!frm.doc.payments.length) {
		frappe.throw({ message: __("No Unreconciled Payments found for this party") });
	}
}

async function justsign_custom_fetch_supplier_invoice_debit_note_no(frm) {
	const invoice_rows = (frm.doc.invoices || []).filter(
		(row) => row.invoice_type === "Purchase Invoice" && row.invoice_number
	);
	const payment_rows = (frm.doc.payments || []).filter(
		(row) => row.reference_type === "Purchase Invoice" && row.reference_name
	);

	const purchase_invoice_names = [
		...new Set([
			...invoice_rows.map((row) => row.invoice_number),
			...payment_rows.map((row) => row.reference_name),
		]),
	];

	if (!purchase_invoice_names.length) {
		[...(frm.doc.invoices || []), ...(frm.doc.payments || [])].forEach((row) => {
			row.custom_supplier_invoice_debit_note_no = "";
		});
		frm.refresh_field("invoices");
		frm.refresh_field("payments");
		return;
	}

	const response = await frappe.call({
		method: "justsign_custom.payment_reconciliation.get_supplier_invoice_debit_note_nos",
		args: {
			purchase_invoice_names,
		},
	});
	const bill_no_by_invoice = response.message || {};

	(frm.doc.invoices || []).forEach((row) => {
		row.custom_supplier_invoice_debit_note_no =
			row.invoice_type === "Purchase Invoice" ? bill_no_by_invoice[row.invoice_number] || "" : "";
	});

	(frm.doc.payments || []).forEach((row) => {
		row.custom_supplier_invoice_debit_note_no =
			row.reference_type === "Purchase Invoice" ? bill_no_by_invoice[row.reference_name] || "" : "";
	});

	frm.refresh_field("invoices");
	frm.refresh_field("payments");
}
"""
