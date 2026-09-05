import frappe


def get_dashboard_data(data):
	data = frappe._dict(data)
	data.setdefault("non_standard_fieldnames", {})
	data.non_standard_fieldnames["Journal Entry"] = "custom_payroll_entry"

	return data
