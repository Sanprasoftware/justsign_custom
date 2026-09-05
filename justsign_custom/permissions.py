import frappe


CK_SALES_ORDER_ROLE = "CK Sales Order"
CK_SALES_ORDER_STATUS = "CK"


def _has_ck_sales_order_role(user=None):
	if user == "Administrator":
		return True

	return CK_SALES_ORDER_ROLE in frappe.get_roles(user)


def _can_view_ck_sales_orders(user=None):
	return _has_ck_sales_order_role(user)


def get_sales_order_permission_query_conditions(user=None, doctype=None):
	if _can_view_ck_sales_orders(user):
		return

	return f"coalesce(`tabSales Order`.`status`, '') != {frappe.db.escape(CK_SALES_ORDER_STATUS)}"


def has_sales_order_permission(doc, ptype=None, user=None, debug=False):
	if _can_view_ck_sales_orders(user):
		return

	if doc.get("status") == CK_SALES_ORDER_STATUS:
		return False


def get_job_cards_permission_query_conditions(user=None, doctype=None):
	if _can_view_ck_sales_orders(user):
		return

	return f"""
		(
			coalesce(`tabJob Cards`.`document_type`, '') != 'Sales Order'
			or coalesce(`tabJob Cards`.`document_id`, '') = ''
			or not exists (
				select 1
				from `tabSales Order`
				where `tabSales Order`.`name` = `tabJob Cards`.`document_id`
					and `tabSales Order`.`status` = {frappe.db.escape(CK_SALES_ORDER_STATUS)}
			)
		)
	"""


def has_job_cards_permission(doc, ptype=None, user=None, debug=False):
	if _can_view_ck_sales_orders(user):
		return

	if doc.get("document_type") != "Sales Order" or not doc.get("document_id"):
		return

	if frappe.db.get_value("Sales Order", doc.get("document_id"), "status") == CK_SALES_ORDER_STATUS:
		return False
