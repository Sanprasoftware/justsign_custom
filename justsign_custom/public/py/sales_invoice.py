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
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url, flt
from frappe.utils.file_manager import save_file, get_file
from frappe.core.doctype.communication.email import make



@frappe.whitelist()
def create_and_attach_pdf(doctype, docname): 
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
