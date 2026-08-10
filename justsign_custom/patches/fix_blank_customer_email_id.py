import frappe


def execute():
    if not frappe.db.table_exists("Customer"):
        return

    frappe.db.delete(
        "Property Setter",
        {
            "doc_type": "Customer",
            "field_name": "email_id",
            "property": "unique",
        },
    )

    frappe.db.sql(
        """
        update `tabCustomer`
        set email_id = NULL
        where coalesce(email_id, '') = ''
        """
    )

    if _customer_email_id_unique_index_exists():
        frappe.db.commit()
        frappe.db.sql("alter table `tabCustomer` drop index `email_id`")

    frappe.clear_cache(doctype="Customer")


def _customer_email_id_unique_index_exists():
    indexes = frappe.db.sql(
        """
        show index from `tabCustomer`
        where Key_name = 'email_id'
            and Column_name = 'email_id'
            and Non_unique = 0
        """,
        as_dict=True,
    )

    return bool(indexes)
