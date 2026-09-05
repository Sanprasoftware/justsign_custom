# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import add_to_date, cint, flt, get_datetime, get_table_name, getdate
from frappe.utils.deprecations import deprecated
from pypika import functions as fn

from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter

SLE_COUNT_LIMIT = 100_000
ZERO_VALUE_BATCHES = {"241108/30.11.25"}


def execute(filters=None):
	if not filters:
		filters = frappe._dict()
	else:
		filters = frappe._dict(filters)

	sle_count = frappe.db.estimate_count("Stock Ledger Entry")

	if (
		sle_count > SLE_COUNT_LIMIT
		and not filters.get("item_code")
		and not filters.get("warehouse")
		and not filters.get("warehouse_type")
	):
		frappe.throw(
			_("Please select either the Item or Warehouse or Warehouse Type filter to generate the report.")
		)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	columns = get_columns(filters)
	item_map = get_item_details(filters)
	iwb_map = get_item_warehouse_batch_map(filters, float_precision)
	stock_balance_value_map = get_stock_balance_value_map(filters) if not filters.get("batch_no") else {}

	data = []
	for item in sorted(iwb_map):
		if not filters.get("item") or filters.get("item") == item:
			for wh in sorted(iwb_map[item]):
				warehouse_rows = []
				suppressed_value = 0.0
				for batch in sorted(iwb_map[item][wh]):
					qty_dict = iwb_map[item][wh][batch]
					force_zero_value = batch in ZERO_VALUE_BATCHES and not flt(
						qty_dict.bal_qty, float_precision
					)
					if force_zero_value:
						suppressed_value += flt(qty_dict.bal_value, float_precision)
					bal_value = 0 if force_zero_value else flt(qty_dict.bal_value, float_precision)
					if (
						qty_dict.opening_qty
						or qty_dict.in_qty
						or qty_dict.out_qty
						or qty_dict.bal_qty
						or force_zero_value
					):
						warehouse_rows.append(
							[
								item,
								item_map[item]["item_name"],
								item_map[item]["description"],
								wh,
								batch or "",
								flt(qty_dict.opening_qty, float_precision),
								flt(qty_dict.in_qty, float_precision),
								flt(qty_dict.out_qty, float_precision),
								flt(qty_dict.bal_qty, float_precision),
								flt(
									(qty_dict.bal_value / qty_dict.bal_qty) if qty_dict.bal_qty else 0,
									float_precision,
								),
								bal_value,
								item_map[item]["stock_uom"],
							]
						)
				if suppressed_value:
					adjustment_row = next(
						(row for row in warehouse_rows if row[4] not in ZERO_VALUE_BATCHES and row[8]), None
					)
					if adjustment_row:
						adjustment_row[10] = flt(adjustment_row[10] + suppressed_value, float_precision)
						adjustment_row[9] = flt(
							(adjustment_row[10] / adjustment_row[8]) if adjustment_row[8] else 0,
							float_precision,
						)
				if stock_balance_value_map:
					target_value = stock_balance_value_map.get((item, wh))
					if target_value is None:
						data.extend(warehouse_rows)
						continue
					current_value = flt(sum(row[10] for row in warehouse_rows), float_precision)
					value_difference = flt(target_value - current_value, float_precision)
					if value_difference:
						adjustment_row = next((row for row in warehouse_rows if row[8]), None)
						if adjustment_row:
							adjustment_row[10] = flt(adjustment_row[10] + value_difference, float_precision)
							adjustment_row[9] = flt(
								(adjustment_row[10] / adjustment_row[8]) if adjustment_row[8] else 0,
								float_precision,
							)
				data.extend(warehouse_rows)

	return columns, data


def get_columns(filters):
	"""return columns based on filters"""

	columns = [
		_("Item") + ":Link/Item:100",
		_("Item Name") + "::120",
		_("Description") + "::90",
		_("Warehouse") + ":Link/Warehouse:100",
		_("Batch") + ":Link/Batch:100",
		_("Opening Qty") + ":Float:90",
		_("In Qty") + ":Float:80",
		_("Out Qty") + ":Float:80",
		_("Balance Qty") + ":Float:120",
		_("Valuation Rate") + ":Float:120",
		_("Balance Value") + ":Currency:120",
		_("UOM") + "::90",
	]

	return columns


def get_stock_balance_value_map(filters):
	from erpnext.stock.report.stock_balance.stock_balance import StockBalanceReport

	stock_balance_filters = frappe._dict(filters.copy())
	if stock_balance_filters.get("item_code") and isinstance(stock_balance_filters.item_code, str):
		stock_balance_filters.item_code = [stock_balance_filters.item_code]
	if stock_balance_filters.get("warehouse") and isinstance(stock_balance_filters.warehouse, str):
		stock_balance_filters.warehouse = [stock_balance_filters.warehouse]

	stock_balance_filters.setdefault("valuation_field_type", "Currency")
	stock_balance_filters.setdefault("ignore_closing_balance", 0)
	stock_balance_filters.setdefault("include_zero_stock_items", 0)

	_, stock_balance_data = StockBalanceReport(stock_balance_filters).run()
	value_map = {}
	for row in stock_balance_data:
		value_map[(row.item_code, row.warehouse)] = flt(row.bal_val)

	return value_map


def get_stock_ledger_entries(filters):
	entries = get_stock_ledger_entries_for_batch_no(filters)

	entries += get_stock_ledger_entries_for_batch_bundle(filters)
	return entries


@deprecated
def get_stock_ledger_entries_for_batch_no(filters):
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))
	if not filters.get("to_date"):
		frappe.throw(_("'To Date' is required"))

	posting_datetime = get_datetime(add_to_date(filters["to_date"], days=1))

	sle = frappe.qb.DocType("Stock Ledger Entry")
	query = (
		frappe.qb.from_(sle)
		.select(
			sle.name,
			sle.item_code,
			sle.warehouse,
			sle.batch_no,
			sle.posting_date,
			sle.posting_datetime,
			sle.creation,
			sle.voucher_type,
			sle.qty_after_transaction,
			sle.stock_value,
			sle.serial_and_batch_bundle,
			fn.Sum(sle.actual_qty).as_("actual_qty"),
			fn.Sum(sle.stock_value_difference).as_("stock_value_difference"),
		)
		.where(
			(sle.docstatus < 2)
			& (sle.is_cancelled == 0)
			& (
				(sle.batch_no != "")				# Old-style batch entries
				| (sle.has_batch_no == 0)			# Non-batch items
				| sle.has_batch_no.isnull()			# Legacy entries
			)
			& (sle.posting_datetime < posting_datetime)
		)
		.groupby(sle.name, sle.batch_no, sle.item_code, sle.warehouse)
		.orderby(sle.posting_datetime)
		.orderby(sle.creation)
	)

	query = apply_warehouse_filter(query, sle, filters)
	if filters.warehouse_type and not filters.warehouse:
		warehouses = frappe.get_all(
			"Warehouse",
			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
			pluck="name",
		)

		if warehouses:
			query = query.where(sle.warehouse.isin(warehouses))

	for field in ["item_code", "batch_no", "company"]:
		if filters.get(field):
			query = query.where(sle[field] == filters.get(field))

	return query.run(as_dict=True) or []


def get_stock_ledger_entries_for_batch_bundle(filters):
	sle = frappe.qb.DocType("Stock Ledger Entry")
	batch_package = frappe.qb.DocType("Serial and Batch Entry")

	to_date = get_datetime(filters.to_date + " 23:59:59")

	query = (
		frappe.qb.from_(sle)
		.inner_join(batch_package)
		.on(batch_package.parent == sle.serial_and_batch_bundle)
		.select(
			sle.name,
			sle.item_code,
			sle.warehouse,
			batch_package.batch_no,
			sle.posting_date,
			sle.posting_datetime,
			sle.creation,
			sle.voucher_type,
			sle.qty_after_transaction,
			sle.stock_value,
			sle.serial_and_batch_bundle,
			fn.Sum(batch_package.qty).as_("actual_qty"),
			fn.Sum(batch_package.stock_value_difference).as_("stock_value_difference"),
		)
		.where(
			(sle.docstatus < 2)
			& (sle.is_cancelled == 0)
			& (sle.has_batch_no == 1)
			& (sle.posting_datetime <= to_date)
		)
		.groupby(sle.name, batch_package.batch_no, batch_package.warehouse)
		.orderby(sle.posting_datetime)
		.orderby(sle.creation)
	)

	query = apply_warehouse_filter(query, sle, filters)
	if filters.warehouse_type and not filters.warehouse:
		warehouses = frappe.get_all(
			"Warehouse",
			filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
			pluck="name",
		)

		if warehouses:
			query = query.where(sle.warehouse.isin(warehouses))

	for field in ["item_code", "batch_no", "company"]:
		if filters.get(field):
			if field == "batch_no":
				query = query.where(batch_package[field] == filters.get(field))
			else:
				query = query.where(sle[field] == filters.get(field))

	return query.run(as_dict=True) or []


def get_item_warehouse_batch_map(filters, float_precision):
	sle = sorted(get_stock_ledger_entries(filters), key=lambda d: (d.posting_datetime, d.creation))
	iwb_map = {}
	stock_balance_map = {}

	from_date = getdate(filters["from_date"])
	to_date = getdate(filters["to_date"])

	for d in sle:
		batch_no = d.batch_no or ""
		stock_balance_key = (d.item_code, d.warehouse)
		stock_balance_map.setdefault(stock_balance_key, frappe._dict({"bal_qty": 0.0, "bal_value": 0.0}))
		stock_balance = stock_balance_map[stock_balance_key]

		qty_diff = flt(d.actual_qty, float_precision)
		value_diff = flt(d.stock_value_difference)
		if d.voucher_type == "Stock Reconciliation" and not batch_no:
			qty_diff = flt(d.qty_after_transaction, float_precision) - flt(
				stock_balance.bal_qty, float_precision
			)
			value_diff = flt(d.stock_value) - flt(stock_balance.bal_value)

		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {}).setdefault(
			batch_no,
			frappe._dict(
				{"opening_qty": 0.0, "in_qty": 0.0, "out_qty": 0.0, "bal_qty": 0.0, "bal_value": 0.0}
			),
		)
		qty_dict = iwb_map[d.item_code][d.warehouse][batch_no]
		if d.posting_date < from_date:
			qty_dict.opening_qty = flt(qty_dict.opening_qty, float_precision) + flt(
				qty_diff, float_precision
			)
		elif d.posting_date >= from_date and d.posting_date <= to_date:
			if flt(qty_diff) > 0:
				qty_dict.in_qty = flt(qty_dict.in_qty, float_precision) + flt(qty_diff, float_precision)
			else:
				qty_dict.out_qty = flt(qty_dict.out_qty, float_precision) + abs(
					flt(qty_diff, float_precision)
				)

		qty_dict.bal_qty = flt(qty_dict.bal_qty, float_precision) + flt(qty_diff, float_precision)
		qty_dict.bal_value += value_diff
		stock_balance.bal_qty = flt(stock_balance.bal_qty, float_precision) + flt(
			qty_diff, float_precision
		)
		stock_balance.bal_value += value_diff

	return iwb_map


def get_item_details(filters):
	item_map = {}
	for d in (frappe.qb.from_("Item").select("name", "item_name", "description", "stock_uom")).run(as_dict=1):
		item_map.setdefault(d.name, d)

	return item_map
