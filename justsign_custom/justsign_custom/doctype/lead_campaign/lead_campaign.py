# Copyright (c) 2025, sanprasoftwares@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re
  
class LeadCampaign(Document):
	@frappe.whitelist()
	def get_data(self):
		# Lead Filter 
		lead_filters = {}  
		if self.brand:
			lead_filters["custom_brand"] = self.brand 
		if self.lead_type:
			lead_filters["type"] = self.lead_type
		if self.status:
			lead_filters["status"] = self.status  
		if self.territory:
			lead_filters["territory"] =["in",[i.territory for i in self.territory]] 
		if self.source:
			lead_filters["source"] = self.source
		if self.customer_group:
			lead_filters["custom_customer_group"] =["in",[i.customer_group for i in self.customer_group]]
		if self.campaign_names:
			lead_filters["campaign_name"] = self.campaign_names
		if self.form_date and self.to_date:
			lead_filters["creation"] = ["between", [self.form_date, self.to_date]]
		
		

		# Customer Filters 
		customer_filters = {}
		if self.customer_group:
			customer_filters["customer_group"] =["in",[i.customer_group for i in self.customer_group]]
		if self.territory:
			customer_filters["territory"] =["in",[i.territory for i in self.territory]] 
		if self.default_price_list:
			customer_filters["default_price_list"] = self.default_price_list
		if self.form_date and self.to_date:
			customer_filters["creation"] = ["between", [self.form_date, self.to_date]]
		

		# prospect filters 
		prospect_filters = {} 
		if self.customer_group:
			prospect_filters["customer_group"] =["in",[i.customer_group for i in self.customer_group]]
		if self.status:
			prospect_filters["status"] = self.status
		if self.territory:
			prospect_filters["territory"] =["in",[i.territory for i in self.territory]] 
		if self.form_date and self.to_date:
			prospect_filters["creation"] = ["between", [self.form_date, self.to_date]]

		# Quotation Filters 
		quotation_filters = {}
		if self.quotation_status:  
			quotation_filters["status"] = self.quotation_status
		if self.form_date and self.to_date:
			quotation_filters["creation"] = ["between", [self.form_date, self.to_date]]

		# Opportunity Filters   
		opportunity_filters = {} 
		if self.opportunity_type:
			opportunity_filters["opportunity_type"] = self.opportunity_type
		if self.opportunity_from:
			opportunity_filters["opportunity_from"] = self.opportunity_from
		if self.campaign_name:
			opportunity_filters["custom_campaign_name"] = self.campaign_name
		if self.opportunity_status:
			opportunity_filters["status"] = self.opportunity_status
		if self.form_date and self.to_date:
			opportunity_filters["creation"] = ["between", [self.form_date, self.to_date]]

		# territory_filter = {}
		# if self.territory:
		# 	territory_filter["name"] = self.territory
		# if self.form_date and self.to_date:
		# 	territory_filter["creation"] = ["between", [self.form_date, self.to_date]]
  

		doctypeMap = {
			"Lead": { 
				"table": "lead",
				"fields": ["name", "first_name", "phone", "email_id", "type", "custom_brand", "status"],
				"filters":lead_filters,
				"table_fields":{"name":"id","first_name":"name1","phone":"phone","email_id":"email","type":"lead_type","custom_brand":"brand","status":"status"}
				},
			"Customer": {
			    "table": "customer",
			    "fields": ["name", "customer_name", "mobile_no", "email_id"],
				"filters":customer_filters,
				"table_fields": {"name":"id", "customer_name":"name1","mobile_no":"phone","email_id":"email"}
			},  
			"Prospect": {  
			    "table": "prospect",
			    "fields": ["name", "prospect_owner", "custom_email", "custom_phone"],
				"filters":prospect_filters,
				"table_fields": {"name": "id", "prospect_owner":"email", "custom_email":"email", "custom_phone":"phone"}
			},	
			"Quotation": {  
			    "table": "quotation",
			    "fields": ["name", "party_name", "contact_email", "contact_mobile"],
				"filters":quotation_filters,
				"table_fields": {"name":"id", "party_name":"name1","contact_email":"email", "contact_mobile":"phone"}
			},
			"Opportunity": {
			    "table": "opportunity",
			    "fields": ["name", "title", "contact_email", "contact_mobile"],
				"filters":opportunity_filters,
				"table_fields": {"name":"id", "title":"name1", "contact_email":"email","contact_mobile":"phone"} 
			},
			# "Territory": {
			# 	"table": "territorys",
			# 	"fields": ["name"],
			# 	"filters":territory_filter,
			# 	"table_fields": {"name": "id"}
			# }
		}          
		
		for doctype, config in doctypeMap.items():
			if self.document_type == doctype:
				data = frappe.get_all(doctype,filters=config["filters"], fields=config["fields"])
				# frappe.throw(f'{doctype}===={config["filters"]}====={config["fields"]}')
				for item in data:  
					data_dict = {}
					for key,value in item.items():
						data_dict[config["table_fields"][key]] = value
					
					# "comment_type": "Comment"
					# "comment_type":Comment  
					comments = frappe.get_all("Comment", filters={"reference_doctype":doctype,"comment_type": "Comment", "reference_name": item["name"]}, fields=["content"])
					comment_text = "\n".join(
						re.sub(r'<[^>]+>', '', c["content"]).strip()
						for c in comments if c.get("content")
					)
					data_dict["comment"] = comment_text or ""
					self.append(config["table"],data_dict)
		  