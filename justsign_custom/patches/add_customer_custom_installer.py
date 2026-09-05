import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	if not frappe.db.table_exists("Customer"):
		return

	create_custom_fields(
		{
			"Customer": [
				{
					"fieldname": "custom_installer",
					"fieldtype": "Link",
					"label": "Installer",
					"options": "User",
					"insert_after": "mobile_no",
				}
			]
		},
		update=True,
	)

	frappe.clear_cache(doctype="Customer")
