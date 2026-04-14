import frappe

def set_event_public(doc, method):
    doc.event_type = "Public"
 