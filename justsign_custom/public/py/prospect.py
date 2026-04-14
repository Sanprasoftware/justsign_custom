import frappe
import re


@frappe.whitelist()
def add_comments(comment,name, email=None):
    comment_doc = frappe.new_doc("Comment")
    comment_doc.reference_doctype = "Prospect"
    comment_doc.reference_name = name
    comment_doc.comment_email = email
    comment_doc.comment_type = "Comment"
    comment_doc.content = comment
    comment_doc.save()
    return "Success"
  

@frappe.whitelist()
def check_customer_exists(prospect_name): 
    """Check if a Customer already exists for this Prospect"""
    customer = frappe.db.get_value("Customer", {"prospect_name": prospect_name}, "name")
    return customer or ""


# @frappe.whitelist()
# def check_opportunity_exists(prospect_name): 
#     """Check if an Opportunity already exists for this Prospect"""
#     opportunity = frappe.db.get_value("Opportunity", {"party_name": prospect_name}, "name")
#     return opportunity or ""






import frappe

@frappe.whitelist()
def create_event_with_todos_prospect(data):

    data = frappe.parse_json(data)

    users = []
    for u in data.get("assign_users", []):
        users.append(u.get("value") if isinstance(u, dict) else u)

    event = frappe.get_doc({
        "doctype": "Event",
        "subject": data["subject"],
        "starts_on": data["starts_on"],
        "ends_on": data.get("ends_on"),
        "event_category": data.get("event_category"),
        "description": data.get("description"),
        "event_participants": [{
            "reference_doctype": "Prospect",
            "reference_docname": data["prospect_name"]
        }],
        "custom_assign_to": [{"user": u} for u in users]
    })

    event.insert(ignore_permissions=True)

    for user in users:
        frappe.get_doc({
            "doctype": "ToDo",
            "allocated_to": user,
            "reference_type": "Event",
            "reference_name": event.name,
            "description": data["subject"],
            "status": "Open",
            "date": data["starts_on"]
        }).insert(ignore_permissions=True)

    frappe.db.commit()
    return event.name



from frappe.utils import add_days, now_datetime
import frappe

@frappe.whitelist()
def create_event_with_todos_rnr_prospect(data):

    data = frappe.parse_json(data)

    description = data.get("description")


    starts_on = add_days(now_datetime(), 2)
    session_user = frappe.session.user

    event = frappe.get_doc({
        "doctype": "Event",
        "subject": "Followup Call",
        "starts_on": starts_on,
        "event_category": "Call",
        "description": description,
        "custom_is_rnr": 1,
        "event_participants": [{
            "reference_doctype": "Prospect",
            "reference_docname": data["prospect_name"]
        }],
        "custom_assign_to": [{"user": session_user}]
    })

    event.insert(ignore_permissions=True)

    frappe.get_doc({
        "doctype": "ToDo",
        "allocated_to": session_user,
        "reference_type": "Event",
        "reference_name": event.name,
        "description": "Followup Call",
        "status": "Open",
        "date": starts_on,
        "description": description,
        "custom_is_rnr": 1
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    return event.name
