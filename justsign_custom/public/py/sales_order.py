# # import frappe

# # frappe.whitelist()
# # def create_job_cards(doc,method):
# #     if doc.customer:
# #         new_doc = frappe.new_doc('Job Cards')
# #         new_doc.customer = doc.customer
# #         new_doc.date = doc.transaction_date
# #         new_doc.document_type = "Sales Order"
# #         new_doc.status = "In Progress"
# #         new_doc.vehicle_details = doc.custom_vehicle_details
# #         new_doc.expected_delivery_date = doc.delivery_date
# #         new_doc.vehicle_type = doc.custom_vehicle_type
# #         new_doc.brand = doc.custom_brand
# #         new_doc.model = doc.custom_model
# #         new_doc.category = doc.custom_category
# #         new_doc.color = doc.custom_color
# #         new_doc.vin_number = doc.custom_vin_number

# #         for row in doc.items:
# #             new_doc.append("items", {
# #                 "item_code": row.item_code,
# #                 "item_name": row.item_name,
# #                 "uom": row.uom,
# #                 "qty": row.qty,
# #             })
        
# #         for data in doc.custom_installer_:
# #             new_doc.installer = data.user


# #         new_doc.save(ignore_permissions=True)




# # @frappe.whitelist()
# # def add_installer_filter(customer):
# #     data = frappe.get_all("Customer Installer Child Table",{"parent":customer},pluck="installer")
# #     # frappe.throw(str(data))
# #     return data


# import frappe
# from frappe.utils.file_manager import save_file
# from frappe.utils.pdf import get_pdf
# from frappe.utils import get_url
  
# def create_and_attach_pdf(doc, method):
#     pdf_content = get_pdf(frappe.get_print(doc.doctype, doc.name, print_format=None))

#     filedoc = frappe.get_doc({  
#         "doctype": "File",
#         "file_name": f"{doc.name}.pdf",  
#         "attached_to_doctype": doc.doctype,
#         "attached_to_name": doc.name,
#         "is_private": 0,  
#         "content": pdf_content,
#         "decode": False  
#     })
#     filedoc.save(ignore_permissions=True)
#     public_url = get_url(filedoc.file_url)
#     frappe.msgprint(f"PDF Generated: <a href='{public_url}' target='_blank'>{public_url}</a>")

    

import frappe
from frappe.utils import flt
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url


FREIGHT_CHARGE_DESCRIPTION = "Freight Charges"
FREIGHT_ACCOUNT_HEAD = "Freight Outwards - JS"
  
def create_and_attach_pdf(doc, method):
    pdf_content = get_pdf(frappe.get_print(doc.doctype, doc.name, print_format="Test Sales Order Print Format"))

    filedoc = frappe.get_doc({  
        "doctype": "File",
        "file_name": f"{doc.name}.pdf",  
        "attached_to_doctype": doc.doctype,
        "attached_to_name": doc.name,
        "is_private": 0,  
        "content": pdf_content,
        "decode": False  
    })
    filedoc.save(ignore_permissions=True)
    public_url = get_url(filedoc.file_url)
    frappe.msgprint(f"PDF Generated: <a href='{public_url}' target='_blank'>{public_url}</a>")

    

def apply_freight_rule(doc, method=None):
    """Apply custom Freight Rule amount on Sales Order taxes."""
    freight_amount = calculate_freight_amount(doc)

    if doc.meta.has_field("custom_freight_amount"):
        doc.custom_freight_amount = freight_amount

    freight_tax_row = get_existing_freight_tax_row(doc)

    if not freight_amount:
        if freight_tax_row:
            freight_tax_row.tax_amount = 0
        return

    if freight_tax_row:
        freight_tax_row.charge_type = "Actual"
        freight_tax_row.account_head = FREIGHT_ACCOUNT_HEAD
        freight_tax_row.description = freight_tax_row.description or FREIGHT_CHARGE_DESCRIPTION
        freight_tax_row.tax_amount = freight_amount
        return

    doc.append(
        "taxes",
        {
            "charge_type": "Actual",
            "account_head": FREIGHT_ACCOUNT_HEAD,
            "description": FREIGHT_CHARGE_DESCRIPTION,
            "tax_amount": freight_amount,
        },
    )


@frappe.whitelist()
def get_freight_rule_result(doc):
    doc = frappe.get_doc(frappe.parse_json(doc))
    apply_freight_rule(doc)

    return {
        "freight_amount": doc.get("custom_freight_amount") or calculate_freight_amount(doc),
        "taxes": [tax.as_dict() for tax in doc.get("taxes", [])],
    }


def calculate_freight_amount(doc):
    total_freight = 0

    for rule in get_applicable_freight_rules(doc):
        if rule.calculate_based_on == "Fix Price":
            total_freight += calculate_fix_price_freight(doc, rule)
        elif rule.calculate_based_on == "Qty Wise":
            total_freight += calculate_qty_wise_freight(doc, rule)
        elif rule.calculate_based_on == "Amount Wise":
            total_freight += calculate_amount_wise_freight(doc, rule)
        elif rule.calculate_based_on == "Weight Wise":
            total_freight += calculate_weight_wise_freight(doc, rule)
        elif rule.calculate_based_on == "Percentage Wise":
            total_freight += calculate_percentage_wise_freight(doc, rule)

    return flt(total_freight, doc.precision("total_taxes_and_charges") or 2)


def get_applicable_freight_rules(doc):
    filters = {}
    transporter = doc.get("transporter") or doc.get("custom_shipper")
    mode = doc.get("mode_of_transport") or doc.get("custom_mode")

    rules = frappe.get_all(
        "Freight Rule",
        filters=filters,
        fields=["name", "shipper", "mode", "modified"],
        order_by="modified desc",
    )

    applicable_rules = []
    for rule in rules:
        if rule.shipper and transporter and rule.shipper != transporter:
            continue
        if rule.shipper and not transporter:
            continue
        if rule.mode and mode and rule.mode != mode:
            continue
        if rule.mode and not mode:
            continue

        applicable_rules.append(frappe.get_doc("Freight Rule", rule.name))

    return applicable_rules


def calculate_fix_price_freight(doc, rule):
    amount = 0
    for item in doc.items:
        matching_rows = get_matching_rule_rows(rule.shipping_rule_item_wise, item, rule.apply_on)
        amount += sum(flt(row.currency_dhog) for row in matching_rows)

    return amount


def calculate_qty_wise_freight(doc, rule):
    amount = 0
    item_group_qty = {}

    for item in doc.items:
        item_rows = get_item_rule_rows(rule.fright_role_qty_wise, item, rule.apply_on)
        if item_rows:
            slab = get_best_slab(item_rows, "qty", flt(item.qty))
            if slab:
                amount += flt(slab.amount)
            continue

        item_group = get_sales_order_item_group(item)
        if not item_group:
            continue

        group_rows = get_item_group_rule_rows(rule.fright_role_qty_wise, item_group, rule.apply_on)
        if group_rows:
            item_group_qty[item_group] = item_group_qty.get(item_group, 0) + flt(item.qty)

    for item_group, qty in item_group_qty.items():
        group_rows = get_item_group_rule_rows(rule.fright_role_qty_wise, item_group, rule.apply_on)
        slab = get_best_slab(group_rows, "qty", qty)
        if slab:
            amount += flt(slab.amount)

    return amount


def calculate_amount_wise_freight(doc, rule):
    amount = 0
    for item in doc.items:
        matching_rows = get_matching_rule_rows(rule.fright_role_amount_wise, item, rule.apply_on)
        item_amount = flt(item.amount)

        for row in matching_rows:
            min_amount = flt(row.min_amount)
            max_amount = flt(row.max_amount)

            if item_amount >= min_amount and item_amount <= max_amount:
                amount += flt(row.amount)
                break

    return amount


def calculate_weight_wise_freight(doc, rule):
    amount = 0
    for item in doc.items:
        matching_rows = get_matching_rule_rows(rule.fright_role_weight_wise, item, rule.apply_on)
        item_weight = get_item_weight(item) * flt(item.qty)
        slab = get_best_slab(matching_rows, "weight", item_weight)
        if slab:
            amount += flt(slab.amount)

    return amount


def calculate_percentage_wise_freight(doc, rule):
    amount = 0
    for item in doc.items:
        matching_rows = get_matching_rule_rows(rule.fright_role_percentage_wise, item, rule.apply_on)
        for row in matching_rows:
            amount += (flt(item.amount) * flt(row.percentage) / 100) + flt(row.extra_amount)

    return amount


def get_matching_rule_rows(rows, item, apply_on):
    item_rows = []
    item_group_rows = []
    item_group = get_sales_order_item_group(item)

    for row in rows:
        row_doctype = (
            row.get("item")
            or row.get("select_item__item_group")
            or row.get("select_doctype")
            or apply_on
        )
        row_value = row.get("item_or_item_group")

        if row_doctype == "Item" and row_value == item.item_code:
            item_rows.append(row)
        elif row_doctype == "Item Group" and row_value == item_group:
            item_group_rows.append(row)

    return item_rows or item_group_rows


def get_item_rule_rows(rows, item, apply_on=None):
    matching_rows = []

    for row in rows:
        if get_rule_row_doctype(row, apply_on) == "Item" and row.get("item_or_item_group") == item.item_code:
            matching_rows.append(row)

    return matching_rows


def get_item_group_rule_rows(rows, item_group, apply_on=None):
    matching_rows = []

    for row in rows:
        if get_rule_row_doctype(row, apply_on) == "Item Group" and row.get("item_or_item_group") == item_group:
            matching_rows.append(row)

    return matching_rows


def get_rule_row_doctype(row, apply_on=None):
    return (
        row.get("item")
        or row.get("select_item__item_group")
        or row.get("select_doctype")
        or apply_on
    )


def get_sales_order_item_group(item):
    return item.get("item_group") or frappe.db.get_value("Item", item.item_code, "item_group")


def get_best_slab(rows, fieldname, value):
    for row in rows:
        threshold = flt(row.get(fieldname))
        if value == threshold:
            return row

    return None


def get_item_weight(item):
    if item.get("weight_per_unit"):
        return flt(item.weight_per_unit)

    return flt(frappe.db.get_value("Item", item.item_code, "weight_per_unit"))


def remove_existing_freight_charge(doc):
    doc.set(
        "taxes",
        [
            tax
            for tax in doc.get("taxes", [])
            if tax.get("description") != FREIGHT_CHARGE_DESCRIPTION
        ],
    )


def get_existing_freight_tax_row(doc):
    for tax in doc.get("taxes", []):
        if tax.get("account_head") == FREIGHT_ACCOUNT_HEAD:
            return tax

    return None
cd