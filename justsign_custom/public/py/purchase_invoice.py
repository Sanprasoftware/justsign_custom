import frappe

def validate_is_return(doc, method=None):
    if doc.is_return == 1:
        for row in doc.taxes:
            if row.tax_amount > 0:
                frappe.throw("Taxes values must be negative")