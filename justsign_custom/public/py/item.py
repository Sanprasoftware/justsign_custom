import frappe

@frappe.whitelist()
def set_income_expense_accout_mandetory(doc, method=None):
    if doc.is_stock_item == 0 and doc.is_fixed_asset == 0 and not doc.item_defaults:
        frappe.throw("Please set Income Account and Expense Account in Item Defaults")

    for row in doc.item_defaults:
        if not row.income_account and not row.expense_account:
            frappe.throw("Please set Income Account or Expense Account in Item Defaults")