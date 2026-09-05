import frappe
from frappe.desk.notifications import get_open_count as get_standard_open_count
from frappe.utils import cint, flt
from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import reconcile_dr_cr_note
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import (
    get_party_details,
    get_tax_withholding_rates,
    get_tax_withholding_details,
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
            tax_amount = round(tax_amount)

        doc.append(
            "taxes",
            {
                "category": "Total",
                "add_deduct_tax": "Deduct",
                "charge_type": "Actual",
                "account_head": tax_details.account_head,
                "description": f"{TDS_ON_CHARGES_ROW_PREFIX}{tax_details.description}",
                "tax_amount": tax_amount,
                "cost_center": values.get("cost_center") or get_default_cost_center(doc),
                "is_tax_withholding_account": 1,
                "custom_is_freight_tds_row": 1,
                "custom_tds_source_description": ", ".join(values["source_descriptions"])[:140],
            },
        )

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
