# Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VehicleEntry(Document):
	@frappe.whitelist()
	def getvehino(self):
		cust_name = frappe.get_value("Customer", {'mobile_no': self.mobile_number}, "name")
		if not cust_name:
			return []
		vehi_data = frappe.get_list("Customer Wise Vehicle",filters={'customer': cust_name},pluck="name")
		
		return vehi_data
	@frappe.whitelist()
	def get_entries(self):
		cust_name = frappe.get_value("Customer",{"mobile_no":self.mobile_number},"name")
		entries = frappe.get_all("Customer Wise Vehicle",{"document_type":"Customer","customer":cust_name},pluck="name")
		return entries

	@frappe.whitelist()
	def get_vehicle(self):
		cust_name = None
		if frappe.db.exists("Customer Wise Vehicle",self.vehicle_number):
			cust_name = frappe.get_doc("Customer Wise Vehicle",self.vehicle_number)
			self.mobile_number = cust_name.mobile_number
			self.document_type = cust_name.document_type
			self.custome_vehicle = cust_name.name
			self.lead = cust_name.customer
			# cust_lead = frappe.get_doc("Lead", {'mobile_no': self.mobile_number})
			# self.lead = cust_lead.name
		else:
			self.mobile_number = ""
			self.custome_vehicle = ""
			self.lead = ""
			self.document_type = ""
	@frappe.whitelist()
	def get_lead(self):
		cust_lead = None
		if frappe.db.exists("Lead", {'mobile_no': self.mobile_number}):
			cust_lead = frappe.get_doc("Lead", {'mobile_no': self.mobile_number})
			self.document_type = "Lead"
			self.lead = cust_lead.name
		else:
			self.lead = ""
			self.document_type = ""


