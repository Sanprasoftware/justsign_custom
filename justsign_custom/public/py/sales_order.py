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
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url
  
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

    
