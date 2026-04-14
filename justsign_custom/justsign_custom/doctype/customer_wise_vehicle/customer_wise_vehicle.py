# Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CustomerWiseVehicle(Document):
	pass
	# @frappe.whitelist()
	# def getvehino(self):
	# 	if self.customer:
	# 		customer_info = frappe.db.get_value("Customer", self.customer, "lead_name", as_dict=True)        
	# 		lead_name = customer_info.get("lead_name")
	# 		if lead_name:
	# 			lead_entry = frappe.db.get_value("Lead", lead_name, "custom_vehicle_entry_id", as_dict=True)        
	# 			vehicle_entry_id = lead_entry.get("custom_vehicle_entry_id")

	# 			vehicle_entry = frappe.db.get_value("Vehicle Entry", vehicle_entry_id, "vehicle_number", as_dict=True)
	# 			vehicle_number = vehicle_entry.get("vehicle_number")
	# 			self.vehicle_no = vehicle_number
	# 			return vehicle_number




	# @frappe.whitelist()
	# def veh_details(self):
		# # Fetch vehicle info as a dictionary
		# all_info = frappe.db.get_value("Vehicle Info", self.vehicle_number, 
		# 	["vin_number", "model", "year_of_purchased", "insurance_provider", "vehicle_type", 
		# 		"vehicle_brand", "vehicle_category", "bike_brand", "bike_category"], as_dict=True)

		# # Assign values correctly
		# self.vin_number = all_info.get("vin_number")
		# self.model = all_info.get("model")
		# self.purchase_year = all_info.get("year_of_purchased")
		# self.vehicle_type = all_info.get("vehicle_type")

		# # Conditional assignment based on vehicle type
		# if all_info.get("vehicle_type") == "Car":
		# 	self.brand = all_info.get("vehicle_brand")
		# 	self.category = all_info.get("vehicle_category")
		# else:
		# 	self.brand = all_info.get("bike_brand")
		# 	self.category = all_info.get("bike_category")
		





