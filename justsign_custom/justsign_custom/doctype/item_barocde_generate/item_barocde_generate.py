# Copyright (c) 2026, sanpra Softwares and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ItemBarocdeGenerate(Document):
	def before_save(self):
		self.create_barcode()
	
	def create_barcode(self):
		if self.item_code and self.qty and self.rate:	
			self.barcode = f"{self.item_code},{self.qty},{self.rate}"
