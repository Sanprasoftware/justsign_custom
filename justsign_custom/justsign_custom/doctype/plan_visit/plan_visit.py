# Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime
from frappe.utils.nestedset import get_descendants_of


class PlanVisit(Document):
	name_field_map = {
		"Lead": "first_name",
		"Prospect": "company_name",
		"Customer": "customer_name",
		"Quotation": "title",
		"Opportunity": "title",
	}
	email_field_map = { 
		"Lead": "email_id",
		"Prospect": "custom_email", 
		"Customer": "email_id",
		"Quotation": "contact_email",
		"Opportunity": "contact_email",
	}
	phone_field_map = {
		"Lead": "mobile_no",
		"Prospect": "custom_phone",
		"Customer": "mobile_no",
		"Quotation": "contact_mobile",
		"Opportunity": "phone",
	}
	extra_query_fields = {
		"Customer": ["customer_primary_contact"],
		"Quotation": ["contact_person", "contact_mobile"],
		"Opportunity": ["contact_person", "contact_mobile"],
	}

	def before_save(self):
		self.allocated_to = frappe.session.user

	def _get_contact_person_details(self, doctype_name, row):
		contact_person_name = row.get(self.name_field_map.get(doctype_name))
		contact_person_number = row.get(self.phone_field_map.get(doctype_name))

		contact_link = None
		if doctype_name == "Customer":
			contact_link = row.get("customer_primary_contact")
		elif doctype_name in ("Quotation", "Opportunity"):
			contact_link = row.get("contact_person")
			contact_person_number = row.get("contact_mobile") or contact_person_number

		# Fallback: resolve Contact linked to this document through Dynamic Link.
		if not contact_link and row.get("name"):
			contact_link = frappe.db.get_value(
				"Dynamic Link",
				{
					"link_doctype": doctype_name,
					"link_name": row.get("name"),
					"parenttype": "Contact",
				},
				"parent",
			)

		if contact_link:
			contact = frappe.db.get_value(
				"Contact",
				contact_link,
				["first_name", "last_name", "mobile_no", "phone"],
				as_dict=1,
			)
			if contact:
				contact_name = " ".join(filter(None, [contact.first_name, contact.last_name]))
				contact_person_name = contact_name or contact_person_name
				contact_person_number = contact.mobile_no or contact.phone or contact_person_number

		return contact_person_name, contact_person_number

	def _append_item(self, doctype_name, row):
		name_field = self.name_field_map.get(doctype_name)
		email_field = self.email_field_map.get(doctype_name)
		phone_field = self.phone_field_map.get(doctype_name)
		contact_person_name, contact_person_number = self._get_contact_person_details(doctype_name, row)

		self.append(
			"items",
			{
				"doctype_name": doctype_name,
				"id": row.get("name"),
				"name1": row.get(name_field),
				"email": row.get(email_field),
				"phone": row.get(phone_field),
				"contact_person_name": contact_person_name,
				"contact_person_number": contact_person_number,
			},
		)

	@frappe.whitelist()
	def single_record(self):
		if not self.doctype_name or not self.id:
			return
		if any(row.doctype_name == self.doctype_name and row.id == self.id for row in self.get("items")):
			return

		source_doc = frappe.get_doc(self.doctype_name, self.id)
		self._append_item(self.doctype_name, source_doc.as_dict())
	
	@frappe.whitelist() 
	def add_items_child(self):
		doc_filter = {}

		if self.form_date and self.to_date:
			doc_filter["creation"] = ["between", [self.form_date, self.to_date]]
		if self.brand:
			doc_filter["custom_brand"] = self.brand 
		# if self.territory:
		# 	doc_filter["territory"] = self.territory

		if self.territory:
			child_territories = get_descendants_of("Territory", self.territory)
			child_territories.append(self.territory)
			doc_filter["territory"] = ["in", child_territories]
		
		if self.customer_group:
			doc_filter["custom_customer_group"] = self.customer_group
		if self.prospect_customer_group:
			doc_filter["customer_group"] = self.prospect_customer_group
			
		if not self.doctype_name:
			return

		fields = [
			"name",
			self.name_field_map.get(self.doctype_name),
			self.email_field_map.get(self.doctype_name),
			self.phone_field_map.get(self.doctype_name),
		]
		fields.extend(self.extra_query_fields.get(self.doctype_name, []))
		fields = list(dict.fromkeys([field for field in fields if field]))

		data = frappe.get_all(self.doctype_name, filters=doc_filter, fields=fields)
		for row in data:
			self._append_item(self.doctype_name, row)
		# frappe.throw(str(data))
	


	def on_submit(self):
		# self.create_field_visit() 
		self.create_field_visits_docs()
	
	# @frappe.whitelist()
	# def create_field_visit(self):
	# 	new_doc = frappe.new_doc("Field Visit") 
	# 	new_doc.plan_visit_id = self.name

	# 	for row in self.get("items"):  ##,{"add_rows":1}
	# 		new_doc.append("items", {  
	# 			"doctype_name": row.doctype_name,
	# 			"id": row.id,
	# 			"name1": row.name1,  
	# 			"phone": row.phone,
	# 			"email": row.email
	# 		})
		
	# 	if new_doc.items:
	# 		new_doc.save()
	# 		self.load_from_db() 
			# self.reload()
	

	# Create Field Visits Doc
	@frappe.whitelist()
	def create_field_visits_docs(self):

		for row in self.get("items"):  ##,{"add_rows":1}
			new_doc = frappe.new_doc("Field Visits")
			new_doc.plan_visit_id = self.name
			new_doc.allocated_to = self.allocated_to
			new_doc.doctype_name= row.doctype_name
			new_doc.name1= row.name1
			new_doc.id= row.id	
			new_doc.phone= row.phone
			new_doc.email= row.email
			new_doc.contact_person_name= row.contact_person_name
			new_doc.contact_person_number= row.contact_person_number

			new_doc.save()
			self.load_from_db()


@frappe.whitelist()
def recurring_plan():
	plan_visits = frappe.get_all(
		"Plan Visit", 
		filters={"is_recurring": 1, "docstatus": 1}, 
		fields=["field_visit_frequency", "name"]
	)

	# frequencies in seconds 
	frequencies = {
		"Daily": 60 * 60 * 24,         # 86400 seconds
		"Weekly": 60 * 60 * 24 * 7,    # 604800 seconds
		"Monthly": 60 * 60 * 24 * 30,  # 2592000 seconds (~30 days)
		"Yearly": 60 * 60 * 24 * 365   # 31536000 seconds (~365 days)
	}

	nowtime = now_datetime()

	# frappe.throw(str(plan_visits))
	for plan_visit in plan_visits:
		field_visit = frappe.get_all(
			"Field Visits", 
			filters={"plan_visit_id": plan_visit.name},
			order_by="creation desc",
			# limit_page_length=1,
			fields=["creation"]
		)
		# frappe.throw(str(field_visit))
	
 
		if field_visit:
			last_visit_time = get_datetime(field_visit[0].creation)
			seconds_diff = (nowtime - last_visit_time).total_seconds()

			# frappe.throw(str(seconds_diff))
			if seconds_diff >= frequencies.get(plan_visit.field_visit_frequency, 0):
				create_field_visit(plan_visit.name)


@frappe.whitelist()
def create_field_visit(pv_id):
	pv_doc = frappe.get_doc("Plan Visit",pv_id)
	for row in pv_doc.items:
		new_doc = frappe.new_doc("Field Visits")
		new_doc.plan_visit_id = pv_id
		new_doc.allocated_to = pv_doc.allocated_to
		new_doc.doctype_name= row.doctype_name
		new_doc.name1= row.name1
		new_doc.id= row.id	
		new_doc.phone= row.phone
		new_doc.email= row.email
		new_doc.contact_person_name= row.contact_person_name
		new_doc.contact_person_number= row.contact_person_number
		new_doc.save()

# @frappe.whitelist()
# def create_field_visit(pv_id):
# 	pv_doc = frappe.get_doc("Plan Visit",pv_id)
# 	new_doc = frappe.new_doc("Field Visit")
# 	new_doc.plan_visit_id = pv_id

# 	for row in pv_doc.items:
# 		new_doc.append("items", {
# 			"doctype_name": row.doctype_name,
# 			"id": row.id,
# 			"name1": row.name1,
# 			"phone": row.phone,
# 			"email": row.email 
# 		})

# 	new_doc.save()





	



  

	
