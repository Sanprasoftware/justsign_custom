import frappe


CLIENT_SCRIPT_NAME = "Payment Reconciliation Supplier Invoice Debit Note No"


def execute():
	if not frappe.db.table_exists("Client Script"):
		return

	script = get_client_script()

	if frappe.db.exists("Client Script", CLIENT_SCRIPT_NAME):
		doc = frappe.get_doc("Client Script", CLIENT_SCRIPT_NAME)
		doc.dt = "Payment Reconciliation"
		doc.view = "Form"
		doc.enabled = 1
		doc.script = script
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
		justsign_custom_fetch_supplier_invoice_debit_note_no(frm);
	},
});

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
