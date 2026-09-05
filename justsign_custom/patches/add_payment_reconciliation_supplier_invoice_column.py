import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	if not frappe.db.table_exists("Custom Field"):
		return

	custom_fields = {
		"Payment Reconciliation Invoice": [
			{
				"fieldname": "custom_supplier_invoice_debit_note_no",
				"fieldtype": "Data",
				"label": "Supplier Invoice/ Debit Note No",
				"insert_after": "invoice_number",
				"in_list_view": 1,
				"columns": 2,
				"read_only": 1,
			}
		],
		"Payment Reconciliation Payment": [
			{
				"fieldname": "custom_supplier_invoice_debit_note_no",
				"fieldtype": "Data",
				"label": "Supplier Invoice/ Debit Note No",
				"insert_after": "reference_name",
				"in_list_view": 1,
				"columns": 2,
				"read_only": 1,
			}
		],
	}

	create_custom_fields(custom_fields, update=True)

	frappe.clear_cache(doctype="Payment Reconciliation Invoice")
	frappe.clear_cache(doctype="Payment Reconciliation Payment")
