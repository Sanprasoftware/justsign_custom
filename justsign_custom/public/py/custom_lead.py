import frappe
import re
from frappe.utils import now_datetime, add_to_date
# import time
  
@frappe.whitelist()  
def assign_sales_partner(doc,method): 
     
    # time.sleep(10)

    # if not (doc.custom_pincode and doc.custom_brand and doc.type):
    #     return
 
    user_lists = frappe.get_all("Sales Partner", fields=["name"])
    matched_users = []

    for user in user_lists:
        user_doc = frappe.get_doc("Sales Partner", user.name)

    # //check is exists or not
    #   frappe.db.exists("table name",{"parent":user.name,"pincodes":doc.custom_pincode})
          
        has_matching_pincode = any(str(row.pincodes) == str(doc.custom_pincode) for row in user_doc.custom_pincode)
        has_matching_brand = any(str(row.brand) == str(doc.custom_brand) for row in user_doc.custom_brand)
        has_matching_type = any(str(row_lead.lead_type) == str(doc.type) for row_lead in user_doc.custom_lead_type)
  
        if has_matching_pincode and has_matching_brand and has_matching_type:
            matched_users.append(user.name)

    if not matched_users:
        frappe.msgprint(f"No matching Sales Partner found for:\nPincode: {doc.custom_pincode}, Brand: {doc.custom_brand}, Lead Type: {doc.type}")
        # doc.custom_lead_status = "Not Assigned" 
        frappe.db.set_value("Lead", doc.name, "custom_lead_status", "Not Assigned")
        
        if doc.custom_sales_partner:
            matched_users = [doc.custom_sales_partner]

    for sales_partner_name in matched_users:
        customer = frappe.get_doc('Sales Partner', sales_partner_name)

        # doc.custom_lead_status =  "Assigned"
        frappe.db.set_value("Lead", doc.name, "custom_lead_status", "Assigned")


        if customer.custom_customer:
            # frappe.db.set_value("Lead", doc.name, "custom_sales_partner_customer", customer.custom_customer)
            doc.custom_sales_partner_customer =  customer.custom_customer
            customer_doc = frappe.get_doc("Customer", customer.custom_customer)
            if customer_doc.email_id:
                # frappe.db.set_value("Lead", doc.name, "custom_customer_email_id", customer_doc.email_id)
                doc.custom_customer_email_id = customer_doc.email_id

        if customer.custom_email:
            # frappe.db.set_value("Lead", doc.name, "custom_sales_partner_email", customer.custom_email)
            doc.custom_sales_partner_email = customer.custom_email

        # Avoid duplicate assignment
        exists = frappe.db.exists("Sales Partner Assigned Lead", {
            "document_type": "Lead",
            "document_id": doc.name,
            # "sales_partner": sales_partner_name
        })
        if exists:
            #  assigned_doc = frappe.get_doc("Sales Partner Assigned Lead", exists)
            #  frappe.throw(str(assigned_doc.sales_partner))     
            assigned_doc = frappe.get_doc("Sales Partner Assigned Lead", exists)

            # Update the fields using the new Lead (doc) info
            assigned_doc.update({
                "document_type": "Lead",
                "lead_type": doc.type,
                "document_id": doc.name,
                "sales_partner": sales_partner_name,
                "lead_name": doc.first_name,
                "lead_email": doc.email_id,
                "lead_city": doc.city,
                "lead_pincode": doc.custom_pincode,
                "lead_status": doc.status,
                "lead_brand": doc.custom_brand,
                "sales_partner_mobile_number" : customer.custom_mobile_no,
                "sales_partner_customer" : customer.custom_customer,
                "lead_mobile_no" : doc.mobile_no,
            })

            assigned_doc.save(ignore_permissions=True)
            frappe.msgprint(f"Updated existing Sales Partner Assigned Lead: {sales_partner_name}")

        else: 
            comments = frappe.get_all("Comment", filters={
                "reference_doctype": "Lead",
                "reference_name": doc.name,  
                "comment_type": "Comment"
            },limit_page_length = 10, fields=["content"])

            comment_text = "\n".join(
                re.sub(r'<[^>]+>', '', c["content"]).strip()
                for c in comments if c.get("content")  
            )
       
            new_doc = frappe.new_doc('Sales Partner Assigned Lead')
            new_doc.document_type = "Lead"
            new_doc.document_id = doc.name 
            new_doc.sales_partner = sales_partner_name
            new_doc.lead_type = doc.type
            new_doc.lead_name = doc.first_name
            new_doc.lead_email = doc.email_id
            new_doc.lead_city = doc.city
            new_doc.lead_pincode = doc.custom_pincode
            new_doc.lead_status = doc.status
            new_doc.lead_brand = doc.custom_brand
            new_doc.sales_partner_mobile_number = customer.custom_mobile_no
            new_doc.sales_partner_customer = customer.custom_customer
            new_doc.lead_mobile_no = doc.mobile_no
            new_doc.lead_comments = comment_text


            # new_doc.update({ 
            #     "document_type": "Lead",
            #     "document_id": doc.name,
            #     "sales_partner": sales_partner_name,
            #     "lead_type": doc.type,
            #     "lead_name": doc.first_name,
            #     "lead_email": doc.email_id,
            #     "lead_city": doc.city,
            #     "lead_pincode": doc.custom_pincode,
            #     "lead_status": doc.status,
            #     "lead_brand": doc.custom_brand,
            #     "sales_partner_mobile_number": customer.custom_mobile_no,
            #     "sales_partner_customer": customer.custom_customer,
            #     "lead_mobile_no": doc.mobile_no,
            #     "lead_comments": comment_text
            # })
            # frappe.msgprint(str(new_doc))
            new_doc.save(ignore_permissions=True)


 
@frappe.whitelist()
def add_comments(comment,name, email=None):
    comment_doc = frappe.new_doc("Comment")
    comment_doc.reference_doctype = "Lead"
    comment_doc.reference_name = name
    comment_doc.comment_email = email
    comment_doc.comment_type = "Comment"
    comment_doc.content = comment
    comment_doc.save()
    return "Success"





# @frappe.whitelist()
# def create_event_with_todos(data):
#     """
#     data = {
#         subject,
#         starts_on,
#         ends_on,
#         duration,
#         description,
#         event_category,
#         lead_name,
#         assign_users: []
#     }
#     """

#     data = frappe.parse_json(data)

#     users = [u["value"] for u in data.get("assign_users", [])]

#     # 1️⃣ Create Event
#     event = frappe.get_doc({
#         "doctype": "Event",
#         "subject": data["subject"],
#         "starts_on": data["starts_on"],
#         "ends_on": data["ends_on"],
#         "event_category": data.get("event_category"),
#         "description": data.get("description"),
#         "event_participants": [{
#             "reference_doctype": "Lead",
#             "reference_docname": data["lead_name"]
#         }],
#         "custom_assign_to": [
#             {"user": user} for user in users
#         ]
#     })

#     event.insert(ignore_permissions=True)

#     # 2️⃣ Create / Update ToDos (SEQUENTIAL & SAFE)
#     for user in data.get("assign_users", []):

#         todo_name = frappe.db.get_value(
#             "ToDo",
#             {
#                 "reference_type": "Event",
#                 "reference_name": event.name,
#                 "allocated_to": user
#             },
#             "name"
#         )

#         if todo_name:
#             frappe.db.set_value(
#                 "ToDo",
#                 todo_name,
#                 {
#                     "description": data["subject"],
#                     "status": "Open",
#                     "date": data["starts_on"]
#                 }
#             )
#         else:
#             todo = frappe.get_doc({
#                 "doctype": "ToDo",
#                 "allocated_to": user,
#                 "reference_type": "Event",
#                 "reference_name": event.name,
#                 "description": data["subject"],
#                 "status": "Open",
#                 "date": data["starts_on"]
#             })
#             todo.insert(ignore_permissions=True)

#     frappe.db.commit()
#     return event.name


@frappe.whitelist()
def create_event_with_todos(data):

    data = frappe.parse_json(data)

    # ✅ Normalize assign_users (string list OR object list)
    users = []
    for u in data.get("assign_users", []):
        if isinstance(u, dict):
            users.append(u.get("value"))
        else:
            users.append(u)

    # 1️⃣ Create Event
    event = frappe.get_doc({
        "doctype": "Event",
        "subject": data["subject"],
        "starts_on": data["starts_on"],
        "ends_on": data["ends_on"],
        "event_category": data.get("event_category"),
        "description": data.get("description"),
        "event_participants": [{
            "reference_doctype": "Lead",
            "reference_docname": data["lead_name"]
        }],
        "custom_assign_to": [
            {"user": user} for user in users
        ]
    })

    event.insert(ignore_permissions=True)

    # 2️⃣ Create / Update ToDos (USE users, NOT raw data)
    for user in users:

        todo_name = frappe.db.get_value(
            "ToDo",
            {
                "reference_type": "Event",
                "reference_name": event.name,
                "allocated_to": user
            },
            "name"
        )

        if todo_name:
            frappe.db.set_value(
                "ToDo",
                todo_name,
                {
                    "description": data["subject"],
                    "status": "Open",
                    "date": data["starts_on"]
                }
            )
        else:
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
def create_event_with_todos_rnr(data):

    data = frappe.parse_json(data)
    lead_name = data.get("lead_name")

    # ✅ Always set start date = Today + 2 days
    starts_on = add_days(now_datetime(), 2)

    session_user = frappe.session.user

    # ✅ Create RNR Event
    event = frappe.get_doc({
        "doctype": "Event",
        "subject": "Followup Call",
        "starts_on": starts_on,
        "event_category": "Call",
        "custom_is_rnr": 1,
        "event_participants": [{
            "reference_doctype": "Lead",
            "reference_docname": lead_name
        }],
        "custom_assign_to": [
            {"user": session_user}
        ]
    })

    event.insert(ignore_permissions=True)

    # ✅ Create RNR ToDo
    frappe.get_doc({
        "doctype": "ToDo",
        "allocated_to": session_user,
        "reference_type": "Event",
        "reference_name": event.name,
        "description": "Followup Call",
        "status": "Open",
        "date": starts_on,
        "custom_is_rnr": 1
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    return event.name
