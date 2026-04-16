import re

import frappe
from frappe import _
from frappe.utils import cint, flt

from justsign_custom.public.py.sales_order import (
    FREIGHT_ACCOUNT_HEAD,
    FREIGHT_CHARGE_DESCRIPTION,
    calculate_freight_amount,
)
from webshop.webshop.shopping_cart import cart as standard_cart
from webshop.webshop.shopping_cart.cart import (
    _get_cart_quotation,
    apply_cart_settings,
    get_cart_quotation,
    set_cart_count,
)


GST_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"


@frappe.whitelist()
def update_cart(
    item_code,
    qty,
    additional_notes=None,
    with_items=False,
    uom=None,
    shipper=None,
    mode=None,
    **kwargs,
):
    quotation = _get_cart_quotation()
    empty_cart = False
    qty = flt(qty)

    if not empty_cart:
        quotation.custom_shipper = shipper
        quotation.custom_mode = mode

    if qty == 0:
        quotation_items = quotation.get("items", {"item_code": ["!=", item_code]})
        if quotation_items:
            quotation.set("items", quotation_items)
        else:
            empty_cart = True
    else:
        warehouse = frappe.get_cached_value(
            "Website Item", {"item_code": item_code}, "website_warehouse"
        )
        quotation_items = quotation.get("items", {"item_code": item_code})

        if not quotation_items:
            row = quotation.append(
                "items",
                {
                    "doctype": "Quotation Item",
                    "item_code": item_code,
                    "qty": qty,
                    "additional_notes": additional_notes,
                    "warehouse": warehouse,
                },
            )
        else:
            row = quotation_items[0]
            row.qty = qty
            row.warehouse = warehouse
            row.additional_notes = additional_notes

        if uom:
            row.uom = uom
            row.conversion_factor = get_conversion_factor(item_code, uom)

    if not empty_cart:
        apply_cart_settings(quotation=quotation)
        apply_freight_to_cart(quotation)

    quotation.flags.ignore_permissions = True
    quotation.payment_schedule = []

    if not empty_cart:
        quotation.save()
    else:
        quotation.delete()
        quotation = None

    set_cart_count(quotation)

    if cint(with_items):
        context = get_cart_quotation(quotation)
        return {
            "items": frappe.render_template("templates/includes/cart/cart_items.html", context),
            "total": frappe.render_template("templates/includes/cart/cart_items_total.html", context),
            "taxes_and_totals": frappe.render_template(
                "templates/includes/cart/cart_payment_summary.html", context
            ),
            "uoms": get_cart_uom_data(),
            "freight_amount": get_freight_amount(quotation) if quotation else 0,
            "shipper": quotation.get("custom_shipper") if quotation else None,
            "mode": quotation.get("custom_mode") if quotation else None,
        }

    return {"name": quotation.name if quotation else None}


@frappe.whitelist()
def set_cart_freight_options(shipper=None, mode=None):
    quotation = _get_cart_quotation()

    quotation.custom_shipper = shipper
    quotation.custom_mode = mode

    apply_cart_settings(quotation=quotation)
    apply_freight_to_cart(quotation)

    quotation.flags.ignore_permissions = True
    quotation.save()

    context = get_cart_quotation(quotation)
    return {
        "total": frappe.render_template("templates/includes/cart/cart_items_total.html", context),
        "taxes_and_totals": frappe.render_template(
            "templates/includes/cart/cart_payment_summary.html", context
        ),
        "freight_amount": get_freight_amount(quotation),
        "shipper": quotation.get("custom_shipper"),
        "mode": quotation.get("custom_mode"),
    }


@frappe.whitelist()
def get_cart_freight_options():
    quotation = _get_cart_quotation()

    return {
        "shippers": get_supplier_options(),
        "shipper": quotation.get("custom_shipper"),
        "mode": quotation.get("custom_mode"),
    }


@frappe.whitelist()
def search_supplier_options(txt=""):
    return get_supplier_options(txt)


def get_supplier_options(txt=""):
    filters = {}
    if txt:
        filters["name"] = ["like", f"%{txt}%"]

    suppliers = frappe.get_all(
        "Supplier",
        filters=filters,
        fields=["name", "supplier_name"],
        limit_page_length=20,
        order_by="supplier_name asc",
        ignore_permissions=True,
    )

    return [
        {
            "name": supplier.name,
            "label": supplier.supplier_name or supplier.name,
        }
        for supplier in suppliers
    ]


def apply_freight_to_cart(quotation):
    freight_amount = calculate_freight_amount(quotation)
    freight_row = get_freight_tax_row(quotation)

    if freight_row:
        freight_row.charge_type = "Actual"
        freight_row.tax_amount = freight_amount
        freight_row.description = freight_row.description or FREIGHT_CHARGE_DESCRIPTION
    elif freight_amount:
        freight_row = quotation.append(
            "taxes",
            {
                "charge_type": "Actual",
                "account_head": FREIGHT_ACCOUNT_HEAD,
                "description": FREIGHT_CHARGE_DESCRIPTION,
                "tax_amount": freight_amount,
            },
        )

    if freight_row:
        set_freight_tax_amounts(freight_row, freight_amount)

    quotation.run_method("calculate_taxes_and_totals")
    freight_row = get_freight_tax_row(quotation)
    if freight_row:
        set_freight_tax_amounts(freight_row, freight_amount)
        quotation.run_method("calculate_taxes_and_totals")


def set_freight_tax_amounts(tax_row, freight_amount):
    tax_row.charge_type = "Actual"
    tax_row.account_head = FREIGHT_ACCOUNT_HEAD
    tax_row.description = tax_row.description or FREIGHT_CHARGE_DESCRIPTION
    tax_row.tax_amount = freight_amount
    tax_row.base_tax_amount = freight_amount
    tax_row.tax_amount_after_discount_amount = freight_amount
    tax_row.base_tax_amount_after_discount_amount = freight_amount


def get_freight_tax_row(quotation):
    return next(
        (tax for tax in quotation.get("taxes", []) if tax.account_head == FREIGHT_ACCOUNT_HEAD),
        None,
    )


def get_freight_amount(quotation):
    row = get_freight_tax_row(quotation)
    return flt(row.tax_amount) if row else 0


@frappe.whitelist()
def get_cart_uom_data():
    quotation = _get_cart_quotation()
    return {
        row.item_code: {
            "selected_uom": row.uom,
            "uoms": get_uom_options(row.item_code),
        }
        for row in quotation.items
    }


def get_uom_options(item_code):
    item = frappe.get_cached_doc("Item", item_code)
    options = {item.stock_uom: 1}

    for row in item.get("uoms"):
        options[row.uom] = flt(row.conversion_factor)

    return [
        {"uom": uom, "conversion_factor": conversion_factor}
        for uom, conversion_factor in options.items()
    ]


def get_conversion_factor(item_code, uom):
    item = frappe.get_cached_doc("Item", item_code)

    if uom == item.stock_uom:
        return 1

    for row in item.get("uoms"):
        if row.uom == uom:
            return flt(row.conversion_factor)

    frappe.throw(_("Invalid UOM {0} for item {1}").format(uom, item_code))


@frappe.whitelist()
def get_profile_status():
    if frappe.session.user == "Guest":
        return {"required": False}

    party = standard_cart.get_party()
    contact_name = frappe.db.get_value("Contact", {"email_id": frappe.session.user})
    has_mobile = bool(frappe.db.get_value("Contact", contact_name, "mobile_no")) if contact_name else False
    has_address = bool(
        frappe.db.exists(
            "Dynamic Link",
            {
                "link_doctype": party.doctype,
                "link_name": party.name,
                "parenttype": "Address",
            },
        )
    )

    gst_number = None
    if party.doctype == "Customer":
        gst_number = frappe.db.get_value("Customer", party.name, "gstin")

    return {
        "required": not (has_mobile and has_address),
        "has_mobile": has_mobile,
        "has_address": has_address,
        "gst_number": gst_number,
    }


@frappe.whitelist()
def save_profile_popup(data):
    data = frappe.parse_json(data)
    party = standard_cart.get_party()

    if data.get("has_gst"):
        gst_number = (data.get("gst_number") or "").strip().upper()
        if not re.match(GST_REGEX, gst_number):
            frappe.throw(_("Please enter a valid GST Number"))

        if party.doctype == "Customer":
            frappe.db.set_value("Customer", party.name, "gstin", gst_number)

    contact_name = frappe.db.get_value("Contact", {"email_id": frappe.session.user})
    if contact_name:
        contact = frappe.get_doc("Contact", contact_name)
        contact.mobile_no = data.get("mobile_no")
        contact.save(ignore_permissions=True)

    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": party.name,
            "address_type": "Billing",
            "address_line1": data.get("address_line1"),
            "city": data.get("city"),
            "state": data.get("state"),
            "country": data.get("country"),
            "pincode": data.get("pincode"),
            "links": [{"link_doctype": party.doctype, "link_name": party.name}],
        }
    )
    address.insert(ignore_permissions=True)

    return {"success": True}


@frappe.whitelist()
def place_order():
    status = get_profile_status()
    if status.get("required"):
        frappe.throw(_("Please complete mobile number and address before checkout"))

    return standard_cart.place_order()
