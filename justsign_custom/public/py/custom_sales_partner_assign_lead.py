import frappe
import re

@frappe.whitelist()
def create_opportunity(doc,method):
    exists = frappe.db.exists("Opportunity", {
        "opportunity_from": "Customer", 
        "party_name": doc.document_id,     
        "custom_brand": doc.lead_brand,
    })
    if exists:
        return 

    # new_doc.update({
    #     "title": doc.sales_partner,
    #     "opportunity_from": "Customer",
    #     "party_name": doc.sales_partner_customer,
    #     "custom_brand": doc.lead_brand,  
    #     "custom_sales_partner_name": doc.sales_partner
    # })  
    new_doc = frappe.new_doc('Opportunity')
    new_doc.title = doc.sales_partner
    # new_doc.opportunity_from = "Customer"
    new_doc.opportunity_from = doc.document_type
    new_doc.party_name = doc.document_id
    new_doc.custom_brand = doc.lead_brand
    new_doc.custom_sales_partner_name = doc.sales_partner
    new_doc.custom_lead_id = doc.document_id
    new_doc.save()
    # new_doc.insert(ignore_permissions=True)
