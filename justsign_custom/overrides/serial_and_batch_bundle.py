import frappe
from frappe import bold
from frappe.utils import flt

from erpnext.stock.doctype.serial_and_batch_bundle.serial_and_batch_bundle import (
	SerialandBatchBundle,
)


class CustomSerialandBatchBundle(SerialandBatchBundle):
	def validate_quantity(self, row, qty_field=None):
		qty_field = self.get_qty_field(row, qty_field=qty_field)
		qty = self.get_comparable_row_qty(row, qty_field)

		precision = row.precision
		if abs(abs(flt(self.total_qty, precision)) - abs(flt(qty, precision))) > 0.01:
			total_qty = frappe.format_value(abs(flt(self.total_qty)), "Float", row)
			set_qty = frappe.format_value(abs(flt(row.get(qty_field))), "Float", row)
			self.throw_error_message(
				f"Total quantity {total_qty} in the Serial and Batch Bundle {bold(self.name)} does not match with the quantity {set_qty} for the Item {bold(self.item_code)} in the {self.voucher_type} # {self.voucher_no}"
			)

	def get_comparable_row_qty(self, row, qty_field):
		qty = row.get(qty_field)

		if qty_field == "qty" and row.get("stock_qty"):
			return row.get("stock_qty")

		if (
			self.voucher_type in {"Purchase Receipt", "Purchase Invoice"}
			and qty_field == "rejected_qty"
			and row.get("uom")
			and row.get("stock_uom")
			and row.get("uom") != row.get("stock_uom")
			and flt(row.get("conversion_factor"))
		):
			return flt(qty) * flt(row.get("conversion_factor"))

		return qty
