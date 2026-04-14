# Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FieldVisits(Document):
	
	def before_save(self):
		self.get_opportunity()

	def on_submit(self):
		self.get_session_user()

	@frappe.whitelist()
	def get_session_user(self): 
		# frappe.throw(str(frappe.session.user))
		self.visited_by = frappe.session.user
		# frappe.set_value("Field Visits", self.name, "allocated_to", frappe.session.user) 
	
	@frappe.whitelist()
	def create_event(self, data):
		data = frappe.parse_json(data)

		event = frappe.new_doc("Event")
		event.subject = data.get("subject")
		event.starts_on = data.get("starts_on")
		event.ends_on = data.get("ends_on")
		event.description = data.get("description")
		# event.custom_assign_to = data.get("assign_users", [])
		for user in data.get("assign_users", []):
			event.append("custom_assign_to", {
				"user": user
			})

		# Always link the created Event back to this Field Visit.
		event.append("event_participants", {
			"reference_doctype": "Field Visits",
			"reference_docname": self.name
		})

		# Also link the Event to the dynamic target selected in Field Visit.
		if self.doctype_name and self.id:
			event.append("event_participants", {
				"reference_doctype": self.doctype_name,
				"reference_docname": self.id
			})
		event.save()
		return event.name

	@frappe.whitelist()
	def add_opportunity_comment(self, opportunity_id, content):
		if not opportunity_id:
			frappe.throw("Opportunity is required")

		if not content:
			frappe.throw("Comment is required")

		opportunity = frappe.db.get_value(
			"Opportunity",
			opportunity_id,
			["opportunity_from", "party_name"],
			as_dict=True,
		)

		if not opportunity:
			frappe.throw(f"Opportunity {opportunity_id} not found")

		comment_values = {
			"doctype": "Comment",
			"comment_type": "Comment",
			"content": content,
			"comment_email": frappe.session.user,
			"comment_by": frappe.session.user,
		}

		# Add comment on Opportunity
		frappe.get_doc({
			**comment_values,
			"reference_doctype": "Opportunity",
			"reference_name": opportunity_id,
		}).insert(ignore_permissions=True)

		# Add same comment on source document (Lead / Prospect / Customer / etc.)
		if opportunity.opportunity_from and opportunity.party_name:
			frappe.get_doc({
				**comment_values,
				"reference_doctype": opportunity.opportunity_from,
				"reference_name": opportunity.party_name,
			}).insert(ignore_permissions=True)

		return {"status": "success"}
	
	# @frappe.whitelist()
	# def get_opportunity(self):
	# 	# frappe.throw("huu")
	# 	opportunity = frappe.get_all("Opportunity", filters={"party_name": self.id, "status": "Open"}, fields=["name", "status", "customer_name"])
	# 	# frappe.msgprint(str(opportunity))
	# 	for row in opportunity:
	# 		self.append("opportunity_table", {
	# 			"opportunity_id": row.name,
	# 			"customer_name": row.customer_name
	# 		})

	def get_opportunity(self):

		# Ensure table field exists before using append
		if not self.meta.get_field("opportunity_table"):
			return

		# Clear old rows to avoid duplicates
		self.set("opportunity_table", [])

		opportunities = frappe.get_all(
			"Opportunity",
			filters={
				"party_name": self.id,
				"status": "Open"
			},
			fields=["name", "customer_name"]
		)

		for row in opportunities:
			self.append("opportunity_table", {
				"opportunity_id": row.name,
				"customer_name": row.customer_name
			})
