import frappe
from frappe.utils import nowdate


def check_due_todos():
    todos = frappe.get_all("ToDo", 
        filters={
            "date": nowdate(), 
            "docstatus": ["!=", 2],
            "status": ["!=", "Closed"],
            "custom_is_due_date": 0
         },  
        fields=["name", "docstatus","status", "custom_is_due_date"])
    
    for todo in todos:
        frappe.db.set_value("ToDo", todo.name, "custom_is_due_date", 1)
  


def update_due_checkbox(doc, method):
    """Check due_date and update checkbox if today"""
    if doc.date == nowdate():
        # Only update if not already checked
        if not doc.custom_is_due_date:
            frappe.db.set_value("ToDo", doc.name, "custom_is_due_date", 1)
