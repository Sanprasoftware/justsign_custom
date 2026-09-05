# import frappe
# import requests
# from frappe.utils.pdf import get_pdf
# from frappe.utils import get_url, flt
# from frappe.utils.file_manager import save_file

# @frappe.whitelist()
# def create_and_attach_pdf(doctype, docname): 
#     doc = frappe.get_doc(doctype, docname)

#     pdf_content = get_pdf(
#         frappe.get_print(doctype, docname, print_format="TS Sales Invoice")
#     )

#     # Avoid path separators in file names (e.g. "ST/502/25-26")
#     safe_name = docname.replace("/", "-").replace("\\", "-")
#     file_name = f"{safe_name}.pdf"

#     # Save or update file
#     filedoc = save_file(file_name, pdf_content, doctype, docname, is_private=0)

#     public_url = get_url(filedoc.file_url)

#     # Update the submitted doc via save so on_update_after_submit (webhooks) fires.
#     doc.custom_pdf_link = public_url
#     doc.custom_send_whatsapp = 1
#     doc.save(ignore_permissions=True)

#     # Send payload directly to n8n
#     contact_name = None
#     contact_no = None
#     if doc.contact_person:
#         contact_name, contact_no = frappe.db.get_value(
#             "Contact",
#             doc.contact_person,
#             ["first_name", "mobile_no"],
#         ) or (None, None)
#         if not contact_no:
#             contact_no = frappe.db.get_value("Contact", doc.contact_person, "phone")

#     def _json_safe(value):
#         if value is None:
#             return None
#         if hasattr(value, "total_seconds"):
#             return value.total_seconds()
#         if hasattr(value, "isoformat"):
#             return value.isoformat()
#         return value

#     items_payload = []
#     for row in doc.items:
#         items_payload.append(
#             {
#                 "item_code": row.get("item_code") or None,
#                 "item_name": row.get("item_name") or None,
#                 "brand": row.get("brand") or None,
#                 "qty": flt(row.get("qty")) if row.get("qty") is not None else None,
#             }
#         )

#     delivery_date = getattr(doc, "delivery_date", None)
#     if not delivery_date:
#         delivery_date = doc.items[0].delivery_date if doc.items and hasattr(doc.items[0], "delivery_date") else None

#     payload = {
#         "name": doc.name,
#         "customer": doc.customer,
#         "irn": doc.irn,
#         "e_waybill_status": doc.e_waybill_status,
#         "company": doc.company,
#         "posting_date": _json_safe(doc.posting_date),
#         "posting_time": _json_safe(doc.posting_time),
#         "grand_total": flt(doc.grand_total) if doc.grand_total is not None else None,
#         "delivery_date": _json_safe(delivery_date),
#         "custom_pdf_link": doc.custom_pdf_link,
#         "contact_person_name": contact_name,
#         "contact_person_no": contact_no,
#         "transporter": doc.transporter,
#         "mode_of_transport": doc.mode_of_transport,
#         "lr_date": _json_safe(doc.lr_date),
#         "lr_no": doc.lr_no,
#         "items": items_payload,
        
#     }

#     try:
#         requests.post(
#             "https://n8n.subspace.money/webhook/c12fe4db-7e3a-4ea8-9734-c9a32dcb5f10",
#             json=payload,
#             timeout=5,
#         )
#     except Exception:
#         frappe.log_error(
#             title="Send WhatsApp Webhook Failed",
#             message=frappe.get_traceback(),
#         )

#     return public_url



# import frappe
# from frappe.utils.pdf import get_pdf
# from frappe.core.doctype.communication.email import make

# def send_invoice_email(doc, method):

#     # 1️⃣ Generate Sales Invoice PDF
#     html = frappe.get_print("Sales Invoice", doc.name, print_format="TS Sales Invoice")
#     sales_invoice_pdf = get_pdf(html)

#     attachments = [
#         {
#             "fname": f"{doc.name}.pdf",
#             "fcontent": sales_invoice_pdf
#         }
#     ]

#     # 2️⃣ Attach Item-wise custom PDF
#     for row in doc.items:
#         if row.item_code:
#             custom_file = frappe.db.get_value("Item", row.item_code, "custom_attach")

#             if custom_file:
#                 try:
#                     file_doc = frappe.get_doc("File", {"file_url": custom_file})
#                     file_content = file_doc.get_content()

#                     attachments.append({
#                         "fname": file_doc.file_name,
#                         "fcontent": file_content
#                     })

#                 except Exception as e:
#                     frappe.log_error(f"Could not attach file for item {row.item_code}: {e}")

#     # 3️⃣ Recipient Email
#     recipient_email = doc.contact_email or doc.customer_email_id or None
#     if not recipient_email:
#         frappe.log_error("Sales Invoice Email Failed: No Email in Customer or Contact")
#         return

#     # 4️⃣ Build Custom HTML Body (Replace variables)
#     customer_person = doc.contact_person or doc.customer or "Customer"

#     email_html = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>New Sales Invoice Raised</title>
#     </head>
#     <body>
#         <p>Dear {customer_person},</p>
#         <p>Your Sales Invoice has been created. 
#         Please check the attached PDF for full details.</p>
    
#         <p>Thank you.</p>
#     </body>
#     </html>
#     """

#     # 5️⃣ Send Email
#     make(
#         recipients=[recipient_email],
#         subject=f"Sales Invoice {doc.name}",
#         content=email_html,
#         attachments=attachments,
#         send_email=True,
#         is_html=True
#     )


import frappe
import requests
from frappe.desk.notifications import get_open_count as get_standard_open_count
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url, flt
from frappe.utils.file_manager import save_file, get_file
from frappe.core.doctype.communication.email import make
from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import reconcile_dr_cr_note



@frappe.whitelist()
def create_and_attach_pdf(doctype, docname=None):
    if hasattr(doctype, "doctype") and hasattr(doctype, "name"):
        doc = doctype
        doctype = doc.doctype
        docname = doc.name
    else:
        doc = frappe.get_doc(doctype, docname)

    pdf_content = get_pdf(
        frappe.get_print(doctype, docname, print_format="TS Sales Invoice")
    )

    # Avoid path separators in file names (e.g. "ST/502/25-26")
    safe_name = docname.replace("/", "-").replace("\\", "-")
    file_name = f"{safe_name}.pdf"

    # Save or update file
    filedoc = save_file(file_name, pdf_content, doctype, docname, is_private=0)

    public_url = get_url(filedoc.file_url)

    # Update the submitted doc via save so on_update_after_submit (webhooks) fires.
    doc.custom_pdf_link = public_url
    doc.custom_send_whatsapp = 1
    doc.save(ignore_permissions=True)

    # Send payload directly to n8n
    contact_name = None
    contact_no = None
    if doc.contact_person:
        contact_name, contact_no = frappe.db.get_value(
            "Contact",
            doc.contact_person,
            ["first_name", "mobile_no"],
        ) or (None, None)
        if not contact_no:
            contact_no = frappe.db.get_value("Contact", doc.contact_person, "phone")

    def _json_safe(value):
        if value is None:
            return None
        if hasattr(value, "total_seconds"):
            return value.total_seconds()
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return value

    items_payload = []
    for row in doc.items:
        items_payload.append(
            {
                "item_code": row.get("item_code") or None,
                "item_name": row.get("item_name") or None,
                "brand": row.get("brand") or None,
                "qty": flt(row.get("qty")) if row.get("qty") is not None else None,
            }
        )

    delivery_date = getattr(doc, "delivery_date", None)
    if not delivery_date:
        delivery_date = doc.items[0].delivery_date if doc.items and hasattr(doc.items[0], "delivery_date") else None

    payload = {
        "name": doc.name,
        "customer": doc.customer,
        "irn": doc.irn,
        "e_waybill_status": doc.e_waybill_status,
        "company": doc.company,
        "posting_date": _json_safe(doc.posting_date),
        "posting_time": _json_safe(doc.posting_time),
        "grand_total": flt(doc.grand_total) if doc.grand_total is not None else None,
        "delivery_date": _json_safe(delivery_date),
        "custom_pdf_link": doc.custom_pdf_link,
        "contact_person_name": contact_name,
        "contact_person_no": contact_no,
        "transporter": doc.transporter, 
        "mode_of_transport": doc.mode_of_transport,
        "lr_date": _json_safe(doc.lr_date),
        "lr_no": doc.lr_no,
        "items": items_payload,
    }

    try:
        requests.post(
            "https://n8n.subspace.money/webhook/c12fe4db-7e3a-4ea8-9734-c9a32dcb5f10",
            json=payload,
            timeout=5,
        )
    except Exception:
        frappe.log_error(
            title="Send WhatsApp Webhook Failed",
            message=frappe.get_traceback(),
        )

    return public_url





def send_invoice_email(doc, method):
    # 1️⃣ Generate Sales Invoice PDF
    html = frappe.get_print("Sales Invoice", doc.name, print_format="TS Sales Invoice")
    sales_invoice_pdf = get_pdf(html)

    attachments = [
        {
            "fname": f"{doc.name}.pdf",
            "fcontent": sales_invoice_pdf
        }
    ]

    # 2️⃣ Attach Item-wise custom PDF
    for row in doc.items:
        if row.item_code:
            custom_file = frappe.db.get_value("Item", row.item_code, "custom_attach")

            if custom_file:
                try:
                    file_name, file_content = get_file(custom_file)
                    if isinstance(file_content, str):
                        file_content = file_content.encode()

                    # Ensure unique names so multiple attachments aren't collapsed
                    safe_item = (row.get("item_code") or "item").replace("/", "-").replace("\\", "-")
                    attachment_name = f"{row.get('idx')}_{safe_item}_{file_name}"

                    attachments.append(
                        {
                            "fname": attachment_name,
                            "fcontent": file_content,
                        }
                    )

                except Exception as e:
                    frappe.log_error(f"Could not attach file for item {row.item_code}: {e}")

    # 3️⃣ Recipient Email
    recipient_email = doc.contact_email or doc.customer_email_id or None
    if not recipient_email:
        frappe.log_error("Sales Invoice Email Failed: No Email in Customer or Contact")
        return

    # 4️⃣ Build Custom HTML Body (Replace variables)
    customer_person = doc.contact_person or doc.customer or "Customer"

    email_html = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>New Sales Invoice Has Been Raised</title>
        </head>
        <body>
            <p>Dear {customer_person},</p>

            <p>We are pleased to inform you that a Sales Invoice has been generated based on our recent discussions and your confirmed order. You can view the invoice details by clicking the PDF link below.</p>

            <p>If you have any questions or notice any discrepancies, please feel free to get in touch with us at <a href="mailto:accounts@plus91inc.in">accounts@plus91inc.in</a>. We’ll be happy to assist you.</p>

            <p>We appreciate your continued trust in Just Signs and look forward to supporting you.</p>

            <p>Best regards,</p>
            <p><strong>Just Signs</strong></p>
            <p>080 4336 5954</p>
        </body>
        </html>"""

    # 5️⃣ Send Email
    make(
        recipients=[recipient_email],
        subject=f"Sales Invoice {doc.name}",
        content=email_html,
        attachments=attachments,
        send_email=True,
        is_html=True
    )


def validate_is_return(doc, method=None):
    if doc.is_return == 1:
        for row in doc.taxes:
            if row.tax_amount > 0:
                frappe.throw("Taxes values must be negative")


#********************************************************************
def validate_custom_discount(doc, method=None):
    discount_total = sum(flt(row.amount) for row in doc.custom_discount)
    invoice_total = abs(flt(doc.grand_total))

    if discount_total > invoice_total:
        frappe.throw(
            f"Discount total ({discount_total}) cannot be greater than Invoice Total ({invoice_total})."
        )


def get_dashboard_data(data):
    data = frappe._dict(data)
    data.method = "justsign_custom.public.py.sales_invoice.get_sales_invoice_open_count"
    return data


@frappe.whitelist()
def get_sales_invoice_open_count(doctype, name, items=None):
    out = get_standard_open_count(doctype, name, items)

    if doctype != "Sales Invoice":
        return out

    requested_items = frappe.parse_json(items) if isinstance(items, str) else items
    if requested_items and "Sales Invoice" not in requested_items:
        return out

    linked_invoices = get_custom_discount_linked_sales_invoices(name)
    if not linked_invoices:
        return out

    count_data = out.get("count") or {}
    internal_links = count_data.setdefault("internal_links_found", [])
    external_links = count_data.setdefault("external_links_found", [])

    existing_sales_invoice_names = []
    for row in internal_links:
        if row.get("doctype") == "Sales Invoice":
            existing_sales_invoice_names.extend(row.get("names") or [])

    for row in external_links[:]:
        if row.get("doctype") == "Sales Invoice":
            external_links.remove(row)

    names = _unique_names(existing_sales_invoice_names + linked_invoices)
    if not names:
        return out

    sales_invoice_link = {
        "doctype": "Sales Invoice",
        "open_count": 0,
        "count": len(names),
        "names": names,
    }

    for index, row in enumerate(internal_links):
        if row.get("doctype") == "Sales Invoice":
            internal_links[index] = sales_invoice_link
            break
    else:
        internal_links.append(sales_invoice_link)

    return out


def get_custom_discount_linked_sales_invoices(sales_invoice):
    doc = frappe.get_doc("Sales Invoice", sales_invoice)
    names = [
        row.sales_invoice_id
        for row in doc.get("custom_discount", [])
        if row.get("sales_invoice_id")
    ]

    reverse_links = frappe.get_all(
        "SI Child",
        filters={
            "parenttype": "Sales Invoice",
            "sales_invoice_id": sales_invoice,
        },
        pluck="parent",
        order_by=None,
    )
    names.extend(reverse_links)

    return _unique_names(name for name in names if name != sales_invoice)


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
        doc = frappe.get_doc("Sales Invoice", doc)

    if not doc.is_return:
        return

    discount_rows = [
        row for row in doc.get("custom_discount", [])
        if row.get("sales_invoice_id") and flt(row.get("amount")) > 0
    ]
    if not discount_rows:
        return

    for row in discount_rows:
        target_invoice = frappe.db.get_value(
            "Sales Invoice",
            row.sales_invoice_id,
            ["customer", "debit_to", "outstanding_amount", "conversion_rate"],
            as_dict=True,
        )
        if not target_invoice:
            frappe.throw(f"Row {row.idx}: Sales Invoice {row.sales_invoice_id} not found.")

        if target_invoice.customer != doc.customer:
            frappe.throw(
                f"Row {row.idx}: Sales Invoice {row.sales_invoice_id} belongs to a different customer."
            )

        receivable_account = target_invoice.debit_to or doc.debit_to
        if _discount_reconciliation_exists(doc, row, receivable_account):
            continue

        amount = flt(row.amount)
        if amount > flt(target_invoice.outstanding_amount):
            frappe.throw(
                f"Row {row.idx}: Amount {amount} cannot be greater than outstanding amount "
                f"{flt(target_invoice.outstanding_amount)} for {row.sales_invoice_id}."
            )

        if amount > abs(flt(doc.outstanding_amount)):
            frappe.throw(
                f"Row {row.idx}: Amount {amount} cannot be greater than credit note outstanding amount "
                f"{abs(flt(doc.outstanding_amount))} for {doc.name}."
            )

        reconcile_dr_cr_note(
            [
                frappe._dict(
                    {
                        "voucher_type": "Sales Invoice",
                        "voucher_no": doc.name,
                        "against_voucher_type": "Sales Invoice",
                        "against_voucher": row.sales_invoice_id,
                        "account": receivable_account,
                        "party_type": "Customer",
                        "party": doc.customer,
                        "allocated_amount": amount,
                        "unadjusted_amount": abs(flt(doc.outstanding_amount)),
                        "dr_or_cr": "credit_in_account_currency",
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


def _discount_reconciliation_exists(doc, row, receivable_account):
    return frappe.db.sql(
        """
        select target.parent
        from `tabJournal Entry Account` target
        inner join `tabJournal Entry Account` source
            on source.parent = target.parent
        inner join `tabJournal Entry` journal
            on journal.name = target.parent
        where journal.docstatus = 1
            and journal.voucher_type = 'Credit Note'
            and target.account = %(account)s
            and target.party_type = 'Customer'
            and target.party = %(customer)s
            and target.reference_type = 'Sales Invoice'
            and target.reference_name = %(target_invoice)s
            and target.credit_in_account_currency = %(amount)s
            and source.account = %(account)s
            and source.party_type = 'Customer'
            and source.party = %(customer)s
            and source.reference_type = 'Sales Invoice'
            and source.reference_name = %(return_invoice)s
            and source.debit_in_account_currency = %(amount)s
        limit 1
        """,
        {
            "account": receivable_account,
            "customer": doc.customer,
            "target_invoice": row.sales_invoice_id,
            "return_invoice": doc.name,
            "amount": flt(row.amount),
        },
    )
