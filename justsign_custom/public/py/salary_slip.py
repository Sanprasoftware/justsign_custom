import frappe
from frappe.utils import flt

def add_deduction(doc, method=None):
    if doc.custom_set_comp_value_manually != 1:
        if not doc.total_working_days or not doc.absent_days:
            return

        # amount = (doc.gross_pay / doc.total_working_days) * doc.absent_days
        amount = flt(
            (doc.gross_pay / doc.total_working_days) * doc.absent_days,
            2
        )
        # Remove old row if exists
        doc.deductions = [
            d for d in doc.deductions
            if d.salary_component != "Absent Deduction"
        ]

        # Add new row
        doc.append("deductions", {
            "salary_component": "Absent Deduction",
            "amount": amount
        })

        