import frappe

@frappe.whitelist()
def create_event_with_todos_customer(data):

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
            "reference_doctype": "Customer",
            "reference_docname": data["customer_name"]
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




import frappe
from frappe.utils import add_days, now_datetime

@frappe.whitelist()
def create_event_with_todos_rnr_customer(data):

    data = frappe.parse_json(data)

    description = data.get("description") or "Followup Call"
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
            "reference_doctype": "Customer",
            "reference_docname": data["customer_name"]
        }],
        "custom_assign_to": [{"user": session_user}]
    })

    event.insert(ignore_permissions=True)

    frappe.get_doc({
        "doctype": "ToDo",
        "allocated_to": session_user,
        "reference_type": "Event",
        "reference_name": event.name,
        "description": description,
        "status": "Open",
        "date": starts_on,
        "custom_is_rnr": 1
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    return event.name
