import frappe


LIMITED_STOCK_BALANCE_ROLE = "Show Limited Column SB"
LIMITED_STOCK_BALANCE_COLUMNS = (
	"item_code",
	"item_name",
	"item_group",
	"bal_qty",
	"opening_qty",
	"in_qty",
	"out_qty",
)


@frappe.whitelist()
def run(
	report_name,
	filters=None,
	user=None,
	ignore_prepared_report=False,
	custom_columns=None,
	is_tree=False,
	parent_field=None,
	are_default_filters=True,
):
	from frappe.desk.query_report import run as original_run

	result = original_run(
		report_name=report_name,
		filters=filters,
		user=user,
		ignore_prepared_report=ignore_prepared_report,
		custom_columns=custom_columns,
		is_tree=is_tree,
		parent_field=parent_field,
		are_default_filters=are_default_filters,
	)

	return apply_stock_balance_column_limit(report_name, result, user)


@frappe.whitelist()
def export_query():
	import frappe.desk.query_report as query_report

	original_run = query_report.run

	def limited_run(*args, **kwargs):
		result = original_run(*args, **kwargs)
		report_name = kwargs.get("report_name") or (args[0] if args else None)
		user = kwargs.get("user")
		return apply_stock_balance_column_limit(report_name, result, user)

	query_report.run = limited_run
	try:
		return query_report.export_query()
	finally:
		query_report.run = original_run


def apply_stock_balance_column_limit(report_name, result, user=None):
	if report_name != "Stock Balance" or not user_has_limited_stock_balance_role(user):
		return result

	result = frappe._dict(result)
	column_by_fieldname = {
		column.get("fieldname"): column for column in result.get("columns", []) if column.get("fieldname")
	}

	result.columns = [
		column_by_fieldname[fieldname]
		for fieldname in LIMITED_STOCK_BALANCE_COLUMNS
		if fieldname in column_by_fieldname
	]
	result.result = [limit_row_columns(row) for row in result.get("result", [])]

	return result


def user_has_limited_stock_balance_role(user=None):
	user = user or frappe.session.user
	return LIMITED_STOCK_BALANCE_ROLE in frappe.get_roles(user)


def limit_row_columns(row):
	if isinstance(row, dict):
		return frappe._dict({fieldname: row.get(fieldname) for fieldname in LIMITED_STOCK_BALANCE_COLUMNS})

	return row
