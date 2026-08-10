import frappe


def execute():
    if not frappe.db.table_exists("Customer"):
        return

    frappe.db.delete(
        "Property Setter",
        {
            "doc_type": "Customer",
            "field_name": "mobile_no",
            "property": "unique",
        },
    )

    frappe.db.sql(
        """
        update `tabCustomer`
        set mobile_no = NULL
        where coalesce(mobile_no, '') = ''
        """
    )

    if _customer_mobile_no_unique_index_exists():
        frappe.db.commit()
        frappe.db.sql("alter table `tabCustomer` drop index `mobile_no`")

    frappe.clear_cache(doctype="Customer")


def _customer_mobile_no_unique_index_exists():
    indexes = frappe.db.sql(
        """
        show index from `tabCustomer`
        where Key_name = 'mobile_no'
            and Column_name = 'mobile_no'
            and Non_unique = 0
        """,
        as_dict=True,
    )

    return bool(indexes)
