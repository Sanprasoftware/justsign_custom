# Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ItemPriceCheck(Document):

	@frappe.whitelist()
	def get_item_price_list_item_wise(self):
		item_price_list = frappe.get_all("Item Price", {"item_code": self.item}, ["item_code", "item_name", "brand", "price_list", "price_list_rate"])
		# frappe.throw(str(item_price_list))

		self.set("table_otqy", [])

		for row in item_price_list:
			# frappe.msgprint(str(row.item_code))
			self.append("table_otqy", {
				"item_code": row.item_code,
				"item_name": row.item_name,
				"brand": row.brand,
				"price_list": row.price_list,
				"rate": row.price_list_rate
			})
		return self

	@frappe.whitelist()
	def get_item_price_list_item_group_wise(self):
		# Clear existing child table
		self.set("table_otqy", [])

		# Get all items in the selected item group
		items = frappe.get_all("Item", {"item_group": self.item_group}, ["name", "item_code"])

		for item in items:
			# Get price list for each item
			item_price_list = frappe.get_all(
				"Item Price",
				{"item_code": item.item_code},
				["item_code", "item_name", "brand", "price_list", "price_list_rate"]
			)

			# Append each row to the child table
			for price in item_price_list:
				self.append("table_otqy", {
					"item_code": price.item_code,
					"item_name": price.item_name,
					"brand": price.brand,
					"price_list": price.price_list,
					"rate": price.price_list_rate
				})

		# Optional: save document if you want to persist
		return self

		# frappe.msgprint(f"{len(self.table_otqy)} rows added to table_otqy")



	
	