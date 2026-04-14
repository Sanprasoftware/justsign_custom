# Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCards(Document):
	
	def on_update(self):
		installer_user = frappe.get_value("Customer", self.customer, "custom_installer")
		# frappe.msgprint("Hii")
		# frappe.throw(str(installer_user))
		frappe.db.set_value("Job Cards", self.name, "installer", installer_user)