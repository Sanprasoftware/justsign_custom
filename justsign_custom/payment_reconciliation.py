import json

import frappe
from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import (
	PaymentReconciliation,
)


@frappe.whitelist()
def get_unreconciled_entries(doc):
	doc = frappe.parse_json(doc)
	payment_reconciliation = PaymentReconciliation(doc)
	payment_reconciliation.get_unreconciled_entries()
	return payment_reconciliation.as_dict()


@frappe.whitelist()
def get_supplier_invoice_debit_note_nos(purchase_invoice_names):
	if isinstance(purchase_invoice_names, str):
		purchase_invoice_names = json.loads(purchase_invoice_names)

	purchase_invoice_names = list(filter(None, set(purchase_invoice_names or [])))
	if not purchase_invoice_names:
		return {}

	return frappe._dict(
		frappe.get_all(
			"Purchase Invoice",
			filters={"name": ("in", purchase_invoice_names)},
			fields=["name", "bill_no"],
			as_list=True,
		)
	)
