import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	if not frappe.db.table_exists("Journal Entry"):
		return

	create_custom_fields(
		{
			"Journal Entry": [
				{
					"fieldname": "custom_payroll_entry",
					"fieldtype": "Link",
					"label": "Payroll Entry",
					"options": "Payroll Entry",
					"insert_after": "company",
					"read_only": 1,
				}
			]
		},
		update=True,
	)

	if frappe.db.table_exists("Journal Entry Account"):
		frappe.db.sql(
			"""
			update `tabJournal Entry` je
			inner join (
				select parent, min(reference_name) as payroll_entry
				from `tabJournal Entry Account`
				where reference_type = 'Payroll Entry'
				and ifnull(reference_name, '') != ''
				group by parent
			) refs on refs.parent = je.name
			set je.custom_payroll_entry = refs.payroll_entry
			where ifnull(je.custom_payroll_entry, '') = ''
			"""
		)

		frappe.db.sql(
			"""
			update `tabJournal Entry Account`
			set reference_type = null, reference_name = null
			where reference_type = 'Payroll Entry'
			"""
		)

	frappe.clear_cache(doctype="Journal Entry")
