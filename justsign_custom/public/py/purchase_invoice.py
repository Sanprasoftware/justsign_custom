import frappe
from frappe.desk.notifications import get_open_count as get_standard_open_count
from frappe.utils import cint, flt
from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import reconcile_dr_cr_note
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import (
    get_party_details,
    get_tax_row_for_tds,
    get_tax_withholding_rates,
    get_tax_withholding_details,
    normal_round,
)

TDS_ON_CHARGES_ROW_PREFIX = "TDS on Charges - "

def validate_is_return(doc, method=None):
    if doc.is_return == 1:
        for row in doc.taxes:
            if row.tax_amount > 0:
                frappe.throw("Taxes values must be negative")


#******************************************************************
def validate_custom_discount(doc, method=None):
    discount_total = sum(flt(row.amount) for row in doc.custom_discount)
    invoice_total = abs(flt(doc.grand_total))

    if discount_total > invoice_total:
        frappe.throw(
            f"Discount total ({discount_total}) cannot be greater than Invoice Total ({invoice_total})."
        )


def apply_freight_tds(doc, method=None):
    if doc.docstatus == 2 or doc.get("_action") == "update_after_submit" or doc.is_return:
        return

    remove_custom_freight_tds_rows(doc)
    set_account_tds_defaults(doc)

    source_rows = get_freight_tds_source_rows(doc)
    if not source_rows:
        return

    grouped_rows = {}
    for row in source_rows:
        if not row.get("tax_withholding_category"):
            frappe.throw(f"Row {row.idx}: Tax Withholding Category is required when Apply TDS is checked.")

        category = row.tax_withholding_category
        grouped_rows.setdefault(
            category,
            {
                "taxable_amount": 0,
                "base_taxable_amount": 0,
                "source_descriptions": [],
                "cost_center": row.cost_center,
            },
        )
        grouped_rows[category]["taxable_amount"] += abs(
            flt(row.tax_amount_after_discount_amount) or flt(row.tax_amount)
        )
        grouped_rows[category]["base_taxable_amount"] += abs(
            flt(row.base_tax_amount_after_discount_amount) or flt(row.base_tax_amount)
        )
        grouped_rows[category]["source_descriptions"].append(row.description or row.account_head)

    for category, values in grouped_rows.items():
        validate_freight_tds_category(category, doc.posting_date)
        tax_details = get_tax_withholding_details(category, doc.posting_date, doc.company)
        if not tax_details:
            frappe.throw(
                f"Tax Withholding Category {category} does not have an account for company {doc.company}."
            )

        tax_amount = get_freight_tds_amount(doc, category, tax_details, values)
        if not tax_amount:
            continue

        if cint(tax_details.round_off_tax_amount):
            tax_amount = normal_round(tax_amount)

        # Keep the generated deduction row identical to ERPNext's Supplier TDS
        # row. Only the taxable base is custom: it is the selected charge row(s),
        # rather than the invoice item net total.
        tds_row = get_tax_row_for_tds(tax_details, tax_amount)
        tds_row.update(
            {
                "description": f"{TDS_ON_CHARGES_ROW_PREFIX}{tds_row.get('description') or ''}",
                "tax_withholding_category": category,
                "cost_center": values.get("cost_center") or get_default_cost_center(doc),
                "is_tax_withholding_account": 1,
                "custom_is_freight_tds_row": 1,
                "custom_tds_source_description": ", ".join(values["source_descriptions"])[:140],
            }
        )
        doc.append("taxes", tds_row)

    if any(row.get("custom_is_freight_tds_row") for row in doc.taxes):
        doc.calculate_taxes_and_totals()
        if doc.get("base_grand_total") is not None:
            doc.set_total_in_words()


def remove_custom_freight_tds_rows(doc):
    for row in list(doc.get("taxes", [])):
        if row.get("custom_is_freight_tds_row"):
            doc.remove(row)


def set_account_tds_defaults(doc):
    account_defaults = get_account_tds_defaults(doc)

    for row in doc.get("taxes", []):
        if row.get("custom_is_freight_tds_row"):
            continue

        defaults = account_defaults.get(row.get("account_head")) or {}
        if not get_freight_tds_taxable_amount(row):
            row.apply_tds = 0
            row.tax_withholding_category = None
            continue

        if not row.get("apply_tds"):
            row.tax_withholding_category = None
            continue

        if row.get("apply_tds") and defaults.get("tax_withholding_category") and not row.get("tax_withholding_category"):
            row.tax_withholding_category = defaults.get("tax_withholding_category")


def get_account_tds_defaults(doc):
    accounts = [row.account_head for row in doc.get("taxes", []) if row.get("account_head")]
    if not accounts:
        return {}

    account_rows = frappe.get_all(
        "Account",
        filters={"name": ["in", list(set(accounts))]},
        fields=["name", "custom_apply_tds", "custom_tax_withholding_category"],
    )

    return {
        row.name: {
            "apply_tds": cint(row.custom_apply_tds),
            "tax_withholding_category": row.custom_tax_withholding_category,
        }
        for row in account_rows
    }


@frappe.whitelist()
def get_account_tds_defaults_for_row(account):
    if not account:
        return {}

    row = frappe.db.get_value(
        "Account",
        account,
        ["custom_apply_tds", "custom_tax_withholding_category"],
        as_dict=True,
    )
    if not row:
        return {}

    return {
        "apply_tds": cint(row.custom_apply_tds),
        "tax_withholding_category": row.custom_tax_withholding_category,
    }


def get_freight_tds_source_rows(doc):
    rows = []
    for row in doc.get("taxes", []):
        if row.get("custom_is_freight_tds_row"):
            continue

        if not row.get("apply_tds"):
            continue

        if row.get("add_deduct_tax") == "Deduct":
            frappe.throw(f"Row {row.idx}: Apply TDS can be used only on added tax/charge rows.")

        taxable_amount = get_freight_tds_taxable_amount(row)
        if not taxable_amount:
            row.apply_tds = 0
            row.tax_withholding_category = None
            continue

        rows.append(row)

    return rows


def get_freight_tds_taxable_amount(row):
    return abs(
        flt(row.get("base_tax_amount_after_discount_amount"))
        or flt(row.get("base_tax_amount"))
        or flt(row.get("tax_amount_after_discount_amount"))
        or flt(row.get("tax_amount"))
    )


def get_freight_tds_amount(doc, category, tax_details, values):
    party_type, party = get_party_details(doc)
    if party_type != "Supplier":
        return 0

    parties = get_parties_with_same_pan(party_type, party)
    previous_taxable_amount = get_previous_freight_tds_taxable_amount(doc, parties, category, tax_details)
    previous_tax_deducted = get_previous_freight_tds_deducted_amount(doc, parties, category, tax_details)

    current_taxable_amount = flt(values["base_taxable_amount"])
    if previous_tax_deducted:
        taxable_amount_for_tds = current_taxable_amount
    else:
        taxable_amount_for_tds = get_taxable_amount_after_threshold(
            current_taxable_amount, previous_taxable_amount, tax_details
        )

    if taxable_amount_for_tds <= 0:
        return 0

    conversion_rate = flt(doc.get("conversion_rate")) or 1
    taxable_amount = taxable_amount_for_tds / conversion_rate
    return taxable_amount * flt(tax_details.rate) / 100


def validate_freight_tds_category(category, posting_date):
    tax_withholding = frappe.get_doc("Tax Withholding Category", category)
    try:
        get_tax_withholding_rates(tax_withholding, posting_date)
    except Exception:
        frappe.throw(
            f"Tax Withholding Category {category} does not have a rate for posting date {posting_date}."
        )


def get_taxable_amount_after_threshold(current_amount, previous_amount, tax_details):
    single_threshold = flt(tax_details.get("threshold"))
    cumulative_threshold = flt(tax_details.get("cumulative_threshold"))

    if not single_threshold and not cumulative_threshold:
        return current_amount

    if single_threshold and current_amount >= single_threshold:
        return current_amount

    total_amount = previous_amount + current_amount
    if cumulative_threshold and total_amount >= cumulative_threshold:
        if cint(tax_details.get("tax_on_excess_amount")):
            return total_amount - cumulative_threshold
        return total_amount

    return 0


def get_parties_with_same_pan(party_type, party):
    parties = [party]
    if not frappe.get_meta(party_type).has_field("pan"):
        return parties

    pan = frappe.db.get_value(party_type, party, "pan")
    if pan:
        parties = frappe.get_all(party_type, filters={"pan": pan}, pluck="name") or parties

    return parties


def get_previous_freight_tds_taxable_amount(doc, parties, category, tax_details):
    return flt(
        frappe.db.sql(
            """
            select sum(abs(coalesce(tax.base_tax_amount_after_discount_amount, tax.base_tax_amount, 0)))
            from `tabPurchase Taxes and Charges` tax
            inner join `tabPurchase Invoice` invoice
                on invoice.name = tax.parent
            where tax.parenttype = 'Purchase Invoice'
                and tax.apply_tds = 1
                and tax.tax_withholding_category = %(category)s
                and ifnull(tax.custom_is_freight_tds_row, 0) = 0
                and invoice.company = %(company)s
                and invoice.supplier in %(parties)s
                and invoice.posting_date between %(from_date)s and %(to_date)s
                and invoice.is_opening = 'No'
                and invoice.docstatus = 1
                and invoice.name != %(current_invoice)s
            """,
            {
                "category": category,
                "company": doc.company,
                "parties": tuple(parties),
                "from_date": tax_details.from_date,
                "to_date": tax_details.to_date,
                "current_invoice": doc.name or "",
            },
        )[0][0]
    )


def get_previous_freight_tds_deducted_amount(doc, parties, category, tax_details):
    return flt(
        frappe.db.sql(
            """
            select sum(abs(coalesce(tax.base_tax_amount_after_discount_amount, tax.base_tax_amount, 0)))
            from `tabPurchase Taxes and Charges` tax
            inner join `tabPurchase Invoice` invoice
                on invoice.name = tax.parent
            where tax.parenttype = 'Purchase Invoice'
                and ifnull(tax.custom_is_freight_tds_row, 0) = 1
                and tax.account_head = %(account_head)s
                and invoice.company = %(company)s
                and invoice.supplier in %(parties)s
                and invoice.posting_date between %(from_date)s and %(to_date)s
                and invoice.is_opening = 'No'
                and invoice.docstatus = 1
                and invoice.name != %(current_invoice)s
            """,
            {
                "account_head": tax_details.account_head,
                "company": doc.company,
                "parties": tuple(parties),
                "from_date": tax_details.from_date,
                "to_date": tax_details.to_date,
                "current_invoice": doc.name or "",
            },
        )[0][0]
    )


def get_default_cost_center(doc):
    if doc.get("taxes"):
        return doc.taxes[0].cost_center

    return frappe.get_cached_value("Company", doc.company, "cost_center")


def get_dashboard_data(data):
    data = frappe._dict(data)
    data.method = "justsign_custom.public.py.purchase_invoice.get_purchase_invoice_open_count"
    return data


@frappe.whitelist()
def get_purchase_invoice_open_count(doctype, name, items=None):
    out = get_standard_open_count(doctype, name, items)

    if doctype != "Purchase Invoice":
        return out

    requested_items = frappe.parse_json(items) if isinstance(items, str) else items
    if requested_items and "Purchase Invoice" not in requested_items:
        return out

    linked_invoices = get_custom_discount_linked_purchase_invoices(name)
    if not linked_invoices:
        return out

    count_data = out.get("count") or {}
    internal_links = count_data.setdefault("internal_links_found", [])
    external_links = count_data.setdefault("external_links_found", [])

    existing_purchase_invoice_names = []
    for row in internal_links:
        if row.get("doctype") == "Purchase Invoice":
            existing_purchase_invoice_names.extend(row.get("names") or [])

    for row in external_links[:]:
        if row.get("doctype") == "Purchase Invoice":
            external_links.remove(row)

    names = _unique_names(existing_purchase_invoice_names + linked_invoices)
    if not names:
        return out

    purchase_invoice_link = {
        "doctype": "Purchase Invoice",
        "open_count": 0,
        "count": len(names),
        "names": names,
    }

    for index, row in enumerate(internal_links):
        if row.get("doctype") == "Purchase Invoice":
            internal_links[index] = purchase_invoice_link
            break
    else:
        internal_links.append(purchase_invoice_link)

    return out


def get_custom_discount_linked_purchase_invoices(purchase_invoice):
    doc = frappe.get_doc("Purchase Invoice", purchase_invoice)
    names = [
        row.purchase_invoice_id
        for row in doc.get("custom_discount", [])
        if row.get("purchase_invoice_id")
    ]

    reverse_links = frappe.get_all(
        "PI Child",
        filters={
            "parenttype": "Purchase Invoice",
            "purchase_invoice_id": purchase_invoice,
        },
        pluck="parent",
        order_by=None,
    )
    names.extend(reverse_links)

    return _unique_names(name for name in names if name != purchase_invoice)


def _unique_names(names):
    unique = []
    seen = set()
    for name in names:
        if name and name not in seen:
            unique.append(name)
            seen.add(name)
    return unique


def create_discount_reconciliation_journal_entries(doc, method=None):
    if isinstance(doc, str):
        doc = frappe.get_doc("Purchase Invoice", doc)

    if not doc.is_return:
        return

    discount_rows = [
        row for row in doc.get("custom_discount", [])
        if row.get("purchase_invoice_id") and flt(row.get("amount")) > 0
    ]
    if not discount_rows:
        return

    for row in discount_rows:
        target_invoice = frappe.db.get_value(
            "Purchase Invoice",
            row.purchase_invoice_id,
            ["supplier", "credit_to", "outstanding_amount", "conversion_rate"],
            as_dict=True,
        )
        if not target_invoice:
            frappe.throw(f"Row {row.idx}: Purchase Invoice {row.purchase_invoice_id} not found.")

        if target_invoice.supplier != doc.supplier:
            frappe.throw(
                f"Row {row.idx}: Purchase Invoice {row.purchase_invoice_id} belongs to a different supplier."
            )

        payable_account = target_invoice.credit_to or doc.credit_to
        if _discount_reconciliation_exists(doc, row, payable_account):
            continue

        amount = flt(row.amount)
        if amount > flt(target_invoice.outstanding_amount):
            frappe.throw(
                f"Row {row.idx}: Amount {amount} cannot be greater than outstanding amount "
                f"{flt(target_invoice.outstanding_amount)} for {row.purchase_invoice_id}."
            )

        if amount > abs(flt(doc.outstanding_amount)):
            frappe.throw(
                f"Row {row.idx}: Amount {amount} cannot be greater than debit note outstanding amount "
                f"{abs(flt(doc.outstanding_amount))} for {doc.name}."
            )

        reconcile_dr_cr_note(
            [
                frappe._dict(
                    {
                        "voucher_type": "Purchase Invoice",
                        "voucher_no": doc.name,
                        "against_voucher_type": "Purchase Invoice",
                        "against_voucher": row.purchase_invoice_id,
                        "account": payable_account,
                        "party_type": "Supplier",
                        "party": doc.supplier,
                        "allocated_amount": amount,
                        "unadjusted_amount": abs(flt(doc.outstanding_amount)),
                        "dr_or_cr": "debit_in_account_currency",
                        "currency": doc.currency,
                        "company": doc.company,
                        "exchange_rate": target_invoice.conversion_rate or doc.conversion_rate or 1,
                        "cost_center": doc.cost_center,
                        "debit_or_credit_note_posting_date": doc.posting_date,
                        "difference_amount": 0,
                    }
                )
            ],
            doc.company,
        )


def create_linked_purchase_receipt_returns(doc, method=None):
    if isinstance(doc, str):
        doc = frappe.get_doc("Purchase Invoice", doc)

    if not doc.get("is_return") or not doc.get("custom_with_stock"):
        return

    source_invoice = get_return_source_purchase_invoice(doc)
    receipt_items_by_receipt = get_return_receipt_items_by_receipt(doc, source_invoice)
    if not receipt_items_by_receipt:
        frappe.throw(
            "With Stock is checked, but no linked Purchase Receipt rows were found for this debit note."
        )

    for purchase_receipt, return_items in receipt_items_by_receipt.items():
        if linked_purchase_receipt_return_exists(doc.name, purchase_receipt):
            continue

        purchase_return = make_linked_purchase_receipt_return(
            doc,
            purchase_receipt,
            return_items,
        )
        purchase_return.flags.ignore_permissions = True
        purchase_return.insert(ignore_permissions=True)
        purchase_return.submit()


def cancel_linked_purchase_receipt_returns(doc, method=None):
    if isinstance(doc, str):
        doc = frappe.get_doc("Purchase Invoice", doc)

    if not doc.get("is_return"):
        return

    for purchase_return in get_linked_purchase_receipt_returns(doc.name):
        purchase_return_doc = frappe.get_doc("Purchase Receipt", purchase_return.name)
        if purchase_return_doc.docstatus == 1:
            purchase_return_doc.flags.ignore_permissions = True
            purchase_return_doc.cancel()


def get_return_source_purchase_invoice(doc):
    if not doc.get("return_against"):
        return None

    return frappe.get_doc("Purchase Invoice", doc.return_against)


def get_return_receipt_items_by_receipt(doc, source_invoice=None):
    source_items = {
        row.name: row
        for row in (source_invoice.get("items") if source_invoice else [])
    }
    receipt_items_by_po_detail = get_purchase_receipt_items_by_po_detail(doc, source_items)
    receipt_items_by_receipt = {}

    for row in doc.get("items", []):
        source_row = source_items.get(row.get("purchase_invoice_item")) or row
        receipt_item_refs = get_purchase_receipt_item_refs(
            row,
            source_row,
            receipt_items_by_po_detail,
        )

        if not receipt_item_refs:
            continue

        for receipt_ref in receipt_item_refs:
            factor = receipt_ref.get("factor") or 1
            purchase_receipt = receipt_ref.purchase_receipt
            pr_detail = receipt_ref.pr_detail
            receipt_items_by_receipt.setdefault(purchase_receipt, {})
            receipt_item = receipt_items_by_receipt[purchase_receipt].setdefault(
                pr_detail,
                frappe._dict(
                    {
                        "qty": 0,
                        "received_qty": 0,
                        "rejected_qty": 0,
                        "stock_qty": 0,
                        "amount": 0,
                        "base_amount": 0,
                        "net_amount": 0,
                        "base_net_amount": 0,
                    }
                ),
            )
            receipt_item.qty += flt(row.get("qty")) * factor
            receipt_item.received_qty += (flt(row.get("received_qty")) or flt(row.get("qty"))) * factor
            receipt_item.rejected_qty += flt(row.get("rejected_qty")) * factor
            receipt_item.stock_qty += flt(row.get("stock_qty")) * factor
            receipt_item.amount += flt(row.get("amount")) * factor
            receipt_item.base_amount += flt(row.get("base_amount")) * factor
            receipt_item.net_amount += flt(row.get("net_amount")) * factor
            receipt_item.base_net_amount += flt(row.get("base_net_amount")) * factor

    return receipt_items_by_receipt


def get_purchase_receipt_items_by_po_detail(doc, source_items):
    po_details = set()
    for row in doc.get("items", []):
        source_row = source_items.get(row.get("purchase_invoice_item")) or row
        po_detail = row.get("po_detail") or source_row.get("po_detail")
        if po_detail and not (row.get("purchase_receipt") or source_row.get("purchase_receipt")):
            po_details.add(po_detail)

    if not po_details:
        return {}

    receipt_items = frappe.db.sql(
        """
        select item.name, item.parent, item.purchase_order_item, item.qty
        from `tabPurchase Receipt Item` item
        inner join `tabPurchase Receipt` receipt
            on receipt.name = item.parent
        where item.purchase_order_item in %(po_details)s
            and receipt.docstatus = 1
            and ifnull(receipt.is_return, 0) = 0
        order by item.creation asc
        """,
        {"po_details": tuple(po_details)},
        as_dict=True,
    )

    receipt_items_by_po_detail = {}
    for row in receipt_items:
        receipt_items_by_po_detail.setdefault(row.purchase_order_item, []).append(row)

    return receipt_items_by_po_detail


def get_purchase_receipt_item_refs(row, source_row, receipt_items_by_po_detail):
    purchase_receipt = row.get("purchase_receipt") or source_row.get("purchase_receipt")
    pr_detail = row.get("pr_detail") or source_row.get("pr_detail")
    if purchase_receipt and pr_detail:
        return [
            frappe._dict(
                {
                    "purchase_receipt": purchase_receipt,
                    "pr_detail": pr_detail,
                    "factor": 1,
                }
            )
        ]

    po_detail = row.get("po_detail") or source_row.get("po_detail")
    receipt_items = receipt_items_by_po_detail.get(po_detail, [])
    if not receipt_items:
        return []

    return allocate_purchase_receipt_item_refs(row, receipt_items)


def allocate_purchase_receipt_item_refs(row, receipt_items):
    qty_to_return = abs(flt(row.get("qty")))
    if not qty_to_return:
        return []

    receipt_refs = []
    remaining_qty = qty_to_return
    for receipt_item in receipt_items:
        receipt_qty = abs(flt(receipt_item.qty))
        if not receipt_qty:
            continue

        allocated_qty = min(remaining_qty, receipt_qty)
        if not allocated_qty:
            break

        receipt_refs.append(
            frappe._dict(
                {
                    "purchase_receipt": receipt_item.parent,
                    "pr_detail": receipt_item.name,
                    "factor": allocated_qty / qty_to_return,
                }
            )
        )
        remaining_qty -= allocated_qty

    return receipt_refs


def linked_purchase_receipt_return_exists(purchase_invoice, purchase_receipt):
    return bool(get_linked_purchase_receipt_returns(purchase_invoice, purchase_receipt))


def get_linked_purchase_receipt_returns(purchase_invoice, purchase_receipt=None):
    conditions = ""
    values = {
        "remarks": f"%Auto-created from Purchase Invoice {purchase_invoice}%",
    }
    if purchase_receipt:
        conditions = "and return_against = %(purchase_receipt)s"
        values["purchase_receipt"] = purchase_receipt

    return frappe.db.sql(
        f"""
        select name, return_against
        from `tabPurchase Receipt`
        where is_return = 1
            and docstatus < 2
            and remarks like %(remarks)s
            {conditions}
        """,
        values,
        as_dict=True,
    )


def make_linked_purchase_receipt_return(doc, purchase_receipt, return_items):
    from erpnext.controllers.sales_and_purchase_return import make_return_doc

    purchase_return = make_return_doc("Purchase Receipt", purchase_receipt)
    purchase_return.posting_date = doc.posting_date
    purchase_return.posting_time = doc.posting_time
    purchase_return.set_posting_time = doc.set_posting_time
    purchase_return.remarks = (
        f"Auto-created from Purchase Invoice {doc.name}"
    )

    filtered_items = []
    for item in purchase_return.get("items", []):
        return_item = return_items.get(item.get("purchase_receipt_item"))
        if not return_item:
            continue

        set_purchase_receipt_return_item_qty(item, return_item)
        filtered_items.append(item)

    purchase_return.set("items", filtered_items)
    if not purchase_return.get("items"):
        frappe.throw(
            f"No matching rows found to create Purchase Receipt return for {purchase_receipt}."
        )

    purchase_return.run_method("set_missing_values")
    purchase_return.run_method("calculate_taxes_and_totals")
    return purchase_return


def set_purchase_receipt_return_item_qty(item, return_item):
    item.qty = -abs(flt(return_item.qty))
    # A Purchase Receipt return may only return accepted stock. ERPNext validates
    # that received_qty equals qty + rejected_qty, and does not allow a non-zero
    # rejected_qty on a return. The Purchase Invoice's received/rejected values
    # cannot be copied independently without violating those constraints.
    item.rejected_qty = 0
    item.received_qty = item.qty

    if item.get("stock_qty") is not None:
        item.stock_qty = -abs(flt(return_item.stock_qty) or flt(item.qty) * flt(item.conversion_factor))

    if item.get("received_stock_qty") is not None:
        item.received_stock_qty = item.stock_qty

    for fieldname in ("amount", "base_amount", "net_amount", "base_net_amount"):
        if item.get(fieldname) is not None:
            item.set(fieldname, -abs(flt(return_item.get(fieldname))))


def _discount_reconciliation_exists(doc, row, payable_account):
    return frappe.db.sql(
        """
        select target.parent
        from `tabJournal Entry Account` target
        inner join `tabJournal Entry Account` source
            on source.parent = target.parent
        inner join `tabJournal Entry` journal
            on journal.name = target.parent
        where journal.docstatus = 1
            and journal.voucher_type = 'Debit Note'
            and target.account = %(account)s
            and target.party_type = 'Supplier'
            and target.party = %(supplier)s
            and target.reference_type = 'Purchase Invoice'
            and target.reference_name = %(target_invoice)s
            and target.debit_in_account_currency = %(amount)s
            and source.account = %(account)s
            and source.party_type = 'Supplier'
            and source.party = %(supplier)s
            and source.reference_type = 'Purchase Invoice'
            and source.reference_name = %(return_invoice)s
            and source.credit_in_account_currency = %(amount)s
        limit 1
        """,
        {
            "account": payable_account,
            "supplier": doc.supplier,
            "target_invoice": row.purchase_invoice_id,
            "return_invoice": doc.name,
            "amount": flt(row.amount),
        },
    )
