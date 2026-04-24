
import frappe


@frappe.whitelist()
def verify_company_password(password):
	# Get default company (you can customize this)
	company = frappe.defaults.get_user_default("Company")

	if not company:
		return False

	stored_password = frappe.db.get_value(
		"Company",
		"Just Signs India Pvt Ltd",
		"custom_password"
	)

	if password == stored_password:
		return True

	return False
