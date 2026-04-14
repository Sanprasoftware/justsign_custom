import frappe
from frappe import _
from frappe.utils import get_link_to_form
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list

@frappe.whitelist()
def custom_bud_item(doc, item_code):
    doc = frappe.parse_json(doc)
    existing_items = []
    if item_code == "None":
        for i in doc.get('items', []):
            for c in doc.get('custom_items_bundle', []):
                if i.get('item_code') == c.get('parent_item'):
                    existing_items.append({
                        'item_code': c.get('item_code'),
                        'qty': c.get('qty'),
                        'uom': c.get('uom'),
                        'description': c.get('description'),
                        'parent_item':  i.get('item_code')
                    })
    else:
        for i in doc.get('items', []):
            if i.get('item_code') != item_code:
                for c in doc.get('custom_items_bundle', []):
                    if i.get('item_code') == c.get('parent_item'):
                        existing_items.append({
                            'item_code': c.get('item_code'),
                            'qty': c.get('qty'),
                            'uom': c.get('uom'),
                            'description': c.get('description'),
                            'parent_item':  i.get('item_code')
                        })
            else:
                child_items = frappe.get_all("Custom Bundle Item", {'parent': item_code}, ['item_code', 'qty', 'uom', 'description'])
                for ch in child_items:
                    existing_items.append({
                        'item_code': ch.item_code, 
                        'qty': ch.qty,
                        'uom': ch.uom,
                        'description': ch.description,
                        'parent_item': item_code
                    })

    return existing_items



@frappe.whitelist()
def custom_product_bundel_itm(doc, item_code):
    doc.custom_items_bundle.clear()
    for i in doc.item:
        child_item = frappe.get_all("Custom Bundle Item",{'parent':item_code},['item_code','qty','uom','description'])
        for c in child_item:
            doc.append('custom_items_bundle', {
                'item_code': c.item_code,
                'qty': c.qty,
                'uom': c.uom,
                'parent_item': i.item_code,
            })

def patch_make_packing_list():
    from erpnext.stock.doctype import packed_item
    packed_item.packed_item.make_packing_list = custom_make_packing_list
    print("hello")  

def custom_make_packing_list(doc,method=None):
    "Make/Update packing list for Product Bundle Item."
    frappe.throw("hello")
    if not doc.packed_items:
        if doc.get("_action") and doc._action == "update_after_submit":
            return

        parent_items_price, reset = {}, False
        set_price_from_children = frappe.db.get_single_value("Selling Settings", "editable_bundle_item_rates")

        stale_packed_items_table = get_indexed_packed_items_table(doc)

        reset = reset_packing_list(doc)

        for item_row in doc.get("items"):
            if is_product_bundle(item_row.item_code):
                for bundle_item in get_product_bundle_items(item_row.item_code):
                    pi_row = add_packed_item_row(
                        doc=doc,
                        packing_item=bundle_item,
                        main_item_row=item_row,
                        packed_items_table=stale_packed_items_table,
                        reset=reset,
                    )
                    item_data = get_packed_item_details(bundle_item.item_code, doc.company)
                    update_packed_item_basic_data(item_row, pi_row, bundle_item, item_data)
                    update_packed_item_stock_data(item_row, pi_row, bundle_item, item_data, doc)
                    update_packed_item_price_data(pi_row, item_data, doc)
                    update_packed_item_from_cancelled_doc(item_row, bundle_item, pi_row, doc)

                    if set_price_from_children:  # create/update bundle item wise price dict
                        update_product_bundle_rate(parent_items_price, pi_row, item_row)

        if parent_items_price:
            set_product_bundle_rate_amount(doc, parent_items_price)  # set price in bundle item


@frappe.whitelist()
def before_save(self, action):
    if not self.custom_phone:
        for lead_row in self.leads:
            mobile_no = frappe.get_value("Lead", lead_row.lead, "mobile_no")
            if mobile_no:
                self.custom_phone = mobile_no
                break
    for i in self.leads:
        frappe.set_value("Lead",i.lead, "status", "Prospect")
@frappe.whitelist()
def on_trash(self, action):
    for i in self.leads:
        frappe.set_value("Lead",i.lead, "status", "Lead")

@frappe.whitelist()
def cust_set_status(self, action):
    if self.prospect_name:
        prospect_cust = frappe.get_doc("Prospect", self.prospect_name)
        if not self.mobile_no:
            if prospect_cust.custom_phone:
                self.mobile_no = prospect_cust.custom_phone
            else:
                for lead_row in prospect_cust.leads:
                    mobile_no = frappe.get_value("Lead", lead_row.lead, "mobile_no")
                    if mobile_no:
                        self.mobile_no = mobile_no
                        break
        for lead_row in prospect_cust.leads:
            frappe.set_value("Lead",lead_row.lead, "status", "Converted")
@frappe.whitelist()
def cust_del_set_status(self, action):
    if self.prospect_name:
        prospect_cust = frappe.get_doc("Prospect", self.prospect_name)
        for lead_row in prospect_cust.leads:
            frappe.set_value("Lead",lead_row.lead, "status", "Prospect")


@frappe.whitelist()
def salesinvocie_after_save(self, action):
    if self.custom_customer_vehicle_no:
        for i in self.items:
            group = frappe.db.get_value("Item", i.item_code, 'item_group')
            if group == "Package":
                exist = frappe.db.exists("Packages", i.item_code)
                if exist:
                    package = frappe.get_doc("Packages", i.item_code)
                    bp = frappe.new_doc("Book Package")
                    bp.customer = self.customer,
                    bp.vehicle_no = self.custom_customer_vehicle_no,
                    bp.si_id = self.name,
                    pkg_mat = frappe.db.get_value("Packages", i.item_code, 'package_amount') or 0
                    bp.package_amount = pkg_mat,
                    for p_item in package.items:
                        bp.append('book_package_item', {
                            'item_code': p_item.item,
                            'qty':p_item.qty,
                        })
                    bp.save()
                    frappe.msgprint(f"Book Package {bp.name} created successfully!")

@frappe.whitelist()
def delivery_note_submit(self, action):
    cust_group = frappe.get_value("Customer", self.customer, "customer_group")

    if self.docstatus == 0 and self.custom_select_package and cust_group == "P91 Car Care":
        job_card = None
        if frappe.db.exists("Job Cards", {"document_type": "Delivery Note", "document_id": self.name}):
            job_card = frappe.get_doc("Job Cards", {"document_type": "Delivery Note", "document_id": self.name})
        else:
            frappe.throw(f"Please Create Job Card")
        if job_card.status != "Completed":
            frappe.throw(f"Please complete Job Card: {get_link_to_form('Job Cards', job_card.name)}")

        job_card = frappe.db.exists("Job Completion", { "delivery_not_id": self.name})
        if not job_card:
            frappe.throw(f"Please complete Job Completion")


# @frappe.whitelist()
# def remove_deleted(doc, item):
