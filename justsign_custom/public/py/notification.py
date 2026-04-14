# import frappe
# from frappe.utils import now_datetime, add_days, getdate, today

# def send_todo_summary():
#     # Get all todos created in last 1 day
#     todos = frappe.get_all(
#         "ToDo",
#         filters={
#             "creation": [">=", add_days(today(), -1)]
#         },
#         fields=["name", "allocated_to", "status", "priority", "creation", "description"]
#     )

#     if not todos:
#         return

#     # Group todos by allocated_to
#     user_todos = {}
#     for todo in todos:
#         if todo.allocated_to:
#             user_todos.setdefault(todo.allocated_to, []).append(todo)

#     # Send email to each user
#     for user, items in user_todos.items():
#         if not user:
#             continue

#         subject = "New ToDo(s) Assigned to You"

#         # Build table
#         rows = ""
#         for t in items:
#             rows += f"""
#                 <tr>
#                     <td>{t.name}</td>
#                     <td>{t.status}</td>
#                     <td>{t.priority or ''}</td>
#                     <td>{getdate(t.creation)}</td>
#                     <td>{t.description or ''}</td>
#                 </tr>
#             """

#         table_html = f"""
#             <p>Hello,</p>
#             <p>The following ToDo(s) were assigned to you in the last 24 hours:</p>
#             <table border="1" cellspacing="0" cellpadding="5">
#                 <tr>
#                     <th>ToDo ID</th>
#                     <th>Status</th>
#                     <th>Priority</th>
#                     <th>Creation Date</th>
#                     <th>Description</th>
#                 </tr>
#                 {rows}
#             </table>
#             <br>
#             <p>Regards,<br>ERPNext</p>
#         """

#         # Send Email
#         frappe.sendmail(
#             recipients=[user],
#             subject=subject,
#             message=table_html
#         )


# import frappe
# from frappe.utils import today, add_days

# def send_todo_summary():
#     # Get yesterday's start and end date
#     yesterday = add_days(today(), -1)
#     start_datetime = yesterday + " 00:00:00"
#     end_datetime = yesterday + " 23:59:59"

#     # Fetch ToDos created yesterday only
#     todos = frappe.get_all(
#         "ToDo",
#         filters={
#             "creation": [">=", start_datetime],
#             "creation": ["<=", end_datetime]
#         },
#         fields=["name", "allocated_to", "status", "priority", "creation", "description"]
#     )

#     if not todos:
#         return

#     # Group todos by allocated_to (user)
#     user_todos = {}
#     for todo in todos:
#         if todo.allocated_to:
#             user_todos.setdefault(todo.allocated_to, []).append(todo)

#     # Send email to each user with their todos
#     for user, items in user_todos.items():
#         if not user:
#             continue

#         subject = "New ToDo(s) Assigned to You"

#         # Build table rows
#         rows = ""
#         for t in items:
#             rows += f"""
#                 <tr>
#                     <td>{t.name}</td>
#                     <td>{t.status}</td>
#                     <td>{t.priority or ''}</td>
#                     <td>{t.creation.strftime('%Y-%m-%d %H:%M')}</td>
#                     <td>{t.description or ''}</td>
#                 </tr>
#             """

#         # Full HTML email body
#         table_html = f"""
#             <p>Hello,</p>
#             <p>The following ToDo(s) were assigned to you yesterday ({yesterday}):</p>
#             <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; width: 100%;">
#                 <tr style="background-color: #f2f2f2;">
#                     <th>ToDo ID</th>
#                     <th>Status</th>
#                     <th>Priority</th>
#                     <th>Creation Date</th>
#                     <th>Description</th>
#                 </tr>
#                 {rows}
#             </table>
#             <br>
#             <p>Regards,<br>ERPNext</p>
#         """

#         # Send Email
#         frappe.sendmail(
#             recipients=[user],
#             subject=subject,
#             message=table_html
#         )



import frappe
from frappe.utils import today, add_days

def send_todo_summary():
    # Get yesterday's start and end date
    yesterday = add_days(today(), -1)
    start_datetime = yesterday + " 00:00:00"
    end_datetime = yesterday + " 23:59:59"

    # Fetch only originally created ToDos (exclude auto-created assignment copies)
    todos = frappe.get_all(
        "ToDo",
        filters={
            "creation": [">=", start_datetime],
            "creation": ["<=", end_datetime],
            "reference_type": ["is", "not set"],   # exclude linked/auto-created todos
            "reference_name": ["is", "not set"]
        },
        fields=["name", "allocated_to", "status", "priority", "creation", "description"]
    )

    if not todos:
        return

    # Group todos by allocated_to (user)
    user_todos = {}
    for todo in todos:
        if todo.allocated_to:
            user_todos.setdefault(todo.allocated_to, []).append(todo)

    # Base URL
    site_url = "https://erp.plus91inc.in"

    # Send email to each user with their todos
    for user, items in user_todos.items():
        if not user:
            continue

        # subject = "New ToDo(s) Assigned to You"
        subject = "Action Needed: Review Yesterday's Assigned Tasks"

        # Build table rows
        rows = ""
        for t in items:
            todo_link = f"{site_url}/app/todo/{t.name}"
            rows += f"""
                <tr>
                    <td><a href="{todo_link}" target="_blank">{t.name}</a></td>
                    <td>{t.status}</td>
                    <td>{t.priority or ''}</td>
                    <td>{t.creation.strftime('%Y-%m-%d %H:%M')}</td>
                    <td>{t.description or ''}</td>
                </tr>
            """

        # Full HTML email body
        table_html = f"""
            <p>Hello,</p>
            <p>The following ToDo(s) were created yesterday ({yesterday}):</p>
            <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th>ToDo ID</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Creation Date</th>
                    <th>Description</th>
                </tr>
                {rows}
            </table>
            <br>
            <p>Regards,<br>ERPNext</p>
        """

        # Send Email
        frappe.sendmail(
            recipients=[user],
            subject=subject,
            message=table_html
        )






import frappe
from frappe.utils import today, formatdate

def send_due_date_reminder():
    today_date = today()

    # Fetch ToDos with due date today (fieldname is 'date')
    todos = frappe.get_all(
        "ToDo",
        filters={
            "date": today_date,          # <-- use 'date' instead of 'due_date'
            "status": ["!=", "Closed"]   # optional: exclude completed todos
        },
        fields=["name", "allocated_to", "status", "priority", "creation", "description", "date"]
    )

    if not todos:
        return

    # Group todos by allocated_to (user)
    user_todos = {}
    for todo in todos:
        if todo.allocated_to:
            user_todos.setdefault(todo.allocated_to, []).append(todo)

    # Base site URL
    site_url = "https://erp.plus91inc.in"

    # Send email to each user
    for user, items in user_todos.items():
        if not user:
            continue

        # subject = f"ToDo(s) Due Today ({today_date})"
        # subject = f"ToDo(s) Which are Due on Today ({today_date})"
        subject = f"Reminder: Tasks Due Today - Please Revie ({today_date})"

        # Build table rows
        rows = ""
        for t in items:
            todo_link = f"{site_url}/app/todo/{t.name}"
            rows += f"""
                <tr>
                    <td><a href="{todo_link}" target="_blank">{t.name}</a></td>
                    <td>{t.status}</td>
                    <td>{t.priority or ''}</td>
                    <td>{formatdate(t.date)}</td>  <!-- use t.date here -->
                    <td>{t.description or ''}</td>
                </tr>
            """

        # Full HTML email body
        table_html = f"""
            <p>Hello,</p>
            <p>The following ToDo(s) are due today ({today_date}):</p>
            <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th>ToDo ID</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Due Date</th>
                    <th>Description</th>
                </tr>
                {rows}
            </table>
            <br>
            <p>Regards,<br>ERPNext</p>
        """

        frappe.sendmail(
            recipients=[user],
            subject=subject,
            message=table_html
        )




import frappe
from frappe.utils import today, formatdate

def send_overdue_todos():
    today_date = today()

    # Fetch all overdue ToDos that are not closed (field is 'date', not 'due_date')
    todos = frappe.get_all(
        "ToDo",
        filters={
            "date": ["<", today_date],   # <-- corrected here
            "status": ["!=", "Closed"]
        },
        fields=["name", "allocated_to", "status", "priority", "creation", "description", "date"]  # <-- corrected here
    )

    if not todos:
        return  # Nothing to send

    site_url = "https://erp.plus91inc.in"

    # Build table rows for all overdue todos
    rows = ""
    for t in todos:
        todo_link = f"{site_url}/app/todo/{t.name}"
        rows += f"""
            <tr>
                <td><a href="{todo_link}" target="_blank">{t.name}</a></td>
                <td>{t.allocated_to or ''}</td>
                <td>{t.status}</td>
                <td>{t.priority or ''}</td>
                <td>{formatdate(t.date)}</td>  <!-- corrected -->
                <td>{t.description or ''}</td>
            </tr>
        """

    table_html = f"""
        <p>Hello Administrator,</p>
        <p>The following ToDo(s) are overdue and still open:</p>
        <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th>ToDo ID</th>
                <th>Allocated To</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Due Date</th>
                <th>Description</th>
            </tr>
            {rows}
        </table>
        <br>
        <p>Regards,<br>ERPNext</p>
    """

    # Get Administrator email
    admin_email = frappe.db.get_single_value("System Settings", "email")

    frappe.sendmail(
        recipients=[admin_email],
        subject=f"Overdue ToDo(s) Report - {today_date}",
        message=table_html
    )




# import frappe
# from frappe.desk.query_report import run as run_report

# def send_camping_wise_lead_report_html():
#     report_name = "Camping Wise Lead Report"
#     recipient = "hp@justsigns.co.in"

#     # Run report
#     result = run_report(
#         report_name=report_name,
#         filters={},
#         user="Administrator"
#     )

#     columns = result.get("columns", [])
#     data = result.get("result", [])

#     if not data:
#         frappe.logger().info("No data found for Camping Wise Lead Report")
#         return

#     # Build HTML table
#     table_html = """
#     <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; width:100%;">
#         <thead style="background-color:#f2f2f2;">
#             <tr>
#     """
#     for col in columns:
#         table_html += f"<th>{col.get('label')}</th>"

#     table_html += "</tr></thead><tbody>"

#     for row in data:
#         table_html += "<tr>"
#         for value in row:
#             table_html += f"<td>{value}</td>"
#         table_html += "</tr>"

#     table_html += "</tbody></table>"

#     # Send email
#     email_html = f"""
#         <p>Hello Team,</p>
#         <p>Please find below the <b>Camping Wise Lead Report</b>.</p>
#         {table_html}
#         <br>
#         <p>Regards,<br>ERPNext System</p>
#     """

#     frappe.sendmail(
#         recipients=[recipient],
#         subject="Daily Camping Wise Lead Report",
#         message=email_html
#     )

#     frappe.db.commit()



import frappe
from frappe.desk.query_report import run as run_report

def send_camping_wise_lead_report_html():
    report_name = "Camping Wise Lead Report"
    recipient = "hp@justsigns.co.in"

    result = run_report(
        report_name=report_name,
        filters={},
        user="Administrator"
    )

    columns = result.get("columns", [])
    data = result.get("result", [])

    if not data:
        return

    # -------- HTML TABLE START --------
    table_html = """
    <table border="1" cellpadding="6" cellspacing="0"
           style="border-collapse:collapse;width:100%;font-size:13px;">
        <thead style="background:#f2f2f2;">
            <tr>
    """

    # Headers (LABELS, not fieldnames)
    for col in columns:
        table_html += f"<th>{col.get('label')}</th>"

    table_html += "</tr></thead><tbody>"

    # Rows
    for row in data:
        table_html += "<tr>"

        # Case 1: row is DICT (normal rows)
        if isinstance(row, dict):
            for col in columns:
                value = row.get(col.get("fieldname"), "")
                table_html += f"<td>{value}</td>"

        # Case 2: row is LIST (Total row)
        else:
            for value in row:
                table_html += f"<td><b>{value}</b></td>"

        table_html += "</tr>"

    table_html += "</tbody></table>"
    # -------- HTML TABLE END --------

    email_html = f"""
        <p>Hello Team,</p>
        <p>Please find below the <b>Camping Wise Lead Report</b>.</p>
        {table_html}
        <br>
        <p>Regards,<br>ERPNext System</p>
    """

    frappe.sendmail(
        recipients=[recipient],
        subject="Daily Camping Wise Lead Report",
        message=email_html
    )

    frappe.db.commit()




# =====================================Send Brand and Cost Center Wise Sales Report=====================================================
# import frappe
# from frappe.utils import today, getdate, get_first_day


# def brand_costcenter_sales_mail():
#     brand_data = get_report_data(group_by="Brand")
#     cost_center_data = get_report_data(group_by="Cost Center")

#     brand_table = make_html_table(
#         brand_data,
#         title="Brand Wise Sales Report"
#     )

#     cost_center_table = make_html_table(
#         cost_center_data,
#         title="Cost Center Wise Sales Report"
#     )

#     email_body = f"""
#         <h3>Daily Sales Summary</h3>
#         {brand_table}
#         <br><br>
#         {cost_center_table}
#     """

#     frappe.sendmail(
#         recipients=["justsignssocial@gmail.com", "hpalrecha@gmail.com"],
#         subject="Daily Brand & Cost Center Wise Sales Report",
#         message=email_body
#     )


# def get_report_data(group_by):
#     today_date = getdate(today())
#     month_start = get_first_day(today_date)
#     year_start = getdate(f"{today_date.year}-01-01")

#     if group_by == "Cost Center":
#         group_field = "so.cost_center"
#     else:
#         group_field = "i.brand"

#     query = f"""
#         SELECT
#             {group_field} AS group_value,

#             SUM(
#                 CASE 
#                     WHEN so.transaction_date = %(today)s
#                     THEN soi.base_net_amount
#                     ELSE 0
#                 END
#             ) AS today_sales,

#             SUM(
#                 CASE
#                     WHEN so.transaction_date BETWEEN %(month_start)s AND %(today)s
#                     THEN soi.base_net_amount
#                     ELSE 0
#                 END
#             ) AS month_sales,

#             SUM(
#                 CASE
#                     WHEN so.transaction_date BETWEEN %(year_start)s AND %(today)s
#                     THEN soi.base_net_amount
#                     ELSE 0
#                 END
#             ) AS ytd_sales

#         FROM `tabSales Order` so
#         INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
#         INNER JOIN `tabItem` i ON i.name = soi.item_code

#         WHERE so.docstatus = 1

#         GROUP BY {group_field}
#         ORDER BY ytd_sales DESC
#     """

#     return frappe.db.sql(
#         query,
#         {
#             "today": today_date,
#             "month_start": month_start,
#             "year_start": year_start
#         },
#         as_dict=True
#     )


# def make_html_table(data, title):
#     if not data:
#         return f"<h4>{title}</h4><p>No data found</p>"

#     rows = ""
#     for row in data:
#         rows += f"""
#             <tr>
#                 <td>{row.group_value or '-'}</td>
#                 <td>{row.today_sales or 0}</td>
#                 <td>{row.month_sales or 0}</td>
#                 <td>{row.ytd_sales or 0}</td>
#             </tr>
#         """

#     return f"""
#         <h4>{title}</h4>
#         <table border="1" cellpadding="6" cellspacing="0" width="100%">
#             <tr>
#                 <th>Name</th>
#                 <th>Today's Sales</th>
#                 <th>Current Month Sales</th>
#                 <th>YTD Sales</th>
#             </tr>
#             {rows}
#         </table>
#     """


import frappe
from frappe.utils import today, getdate, get_first_day


# =========================================================
# MAIN MAIL FUNCTION
# =========================================================
def brand_costcenter_sales_mail():
    brand_data = get_report_data(group_by="Brand")
    cost_center_data = get_report_data(group_by="Cost Center")

    brand_table = make_html_table(
        brand_data,
        title="Brand Wise Sales Report",
        group_by="Brand"
    )

    cost_center_table = make_html_table(
        cost_center_data,
        title="Cost Center Wise Sales Report",
        group_by="Cost Center"
    )

    email_body = f"""
        <h3>Daily Sales Summary</h3>
        {brand_table}
        <br><br>
        {cost_center_table}
    """

    frappe.sendmail(
        recipients=[
            "justsignssocial@gmail.com",
            "hpalrecha@gmail.com"
        ],
        subject="Daily Brand & Cost Center Wise Sales Report",
        message=email_body
    )


# =========================================================
# DATA FETCHING (MATCHES SCRIPT REPORT)
# =========================================================
def get_report_data(group_by):
    today_date = getdate(today())
    month_start = get_first_day(today_date)
    year_start = getdate(f"{today_date.year}-01-01")

    if group_by == "Cost Center":
        group_field = "so.cost_center"
        group_condition = ""
    else:
        group_field = "i.brand"
        group_condition = "AND i.brand != %(excluded_brand)s"

    query = f"""
        SELECT
            {group_field} AS group_value,

            SUM(
                CASE WHEN so.transaction_date = %(today)s
                THEN soi.base_net_amount ELSE 0 END
            ) AS today_sales,

            SUM(
                CASE WHEN so.transaction_date BETWEEN %(month_start)s AND %(today)s
                THEN soi.base_net_amount ELSE 0 END
            ) AS month_sales,

            SUM(
                CASE WHEN so.transaction_date BETWEEN %(year_start)s AND %(today)s
                THEN soi.base_net_amount ELSE 0 END
            ) AS ytd_sales

        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
        INNER JOIN `tabItem` i ON i.name = soi.item_code

        WHERE so.docstatus = 1
        {group_condition}

        GROUP BY {group_field}
        ORDER BY ytd_sales DESC
    """

    rows = frappe.db.sql(
        query,
        {
            "today": today_date,
            "month_start": month_start,
            "year_start": year_start,
            "excluded_brand": "P91 CC"
        },
        as_dict=True
    )

    # ------------------------------------------------
    # EXTRA LOGIC FOR COST CENTER
    # ------------------------------------------------
    if group_by != "Cost Center":
        return rows

    p91_label = "P91 Car care - P91"

    p91_row = next((r for r in rows if r.get("group_value") == p91_label), None)
    others_rows = [r for r in rows if r.get("group_value") != p91_label]

    others_today = sum(r.get("today_sales", 0) for r in others_rows)
    others_month = sum(r.get("month_sales", 0) for r in others_rows)
    others_ytd = sum(r.get("ytd_sales", 0) for r in others_rows)

    p91_today = (p91_row or {}).get("today_sales", 0)
    p91_month = (p91_row or {}).get("month_sales", 0)
    p91_ytd = (p91_row or {}).get("ytd_sales", 0)

    return [{
        "group_value": p91_label,
        "today_sales": p91_today,
        "month_sales": p91_month,
        "ytd_sales": p91_ytd,
        "others_today": others_today,
        "others_month": others_month,
        "others_ytd": others_ytd,
        "p91_minus_others_today": p91_today - others_today,
        "p91_minus_others_month": p91_month - others_month,
        "p91_minus_others_ytd": p91_ytd - others_ytd,
    }]


# =========================================================
# HTML TABLE BUILDER
# =========================================================
def make_html_table(data, title, group_by):
    if not data:
        return f"<h4>{title}</h4><p>No data found</p>"

    # ---------------------------
    # COST CENTER TABLE
    # ---------------------------
    if group_by == "Cost Center":
        header = """
            <tr>
                <th>Cost Center</th>
                <th>Today</th>
                <th>Month</th>
                <th>YTD</th>
                <th>Others Today</th>
                <th>Others Month</th>
                <th>Others YTD</th>
                <th>P91 - Others Today</th>
                <th>P91 - Others Month</th>
                <th>P91 - Others YTD</th>
            </tr>
        """

        rows_html = ""
        for r in data:
            rows_html += f"""
                <tr>
                    <td>{r.get("group_value")}</td>
                    <td>{r.get("today_sales", 0)}</td>
                    <td>{r.get("month_sales", 0)}</td>
                    <td>{r.get("ytd_sales", 0)}</td>
                    <td>{r.get("others_today", 0)}</td>
                    <td>{r.get("others_month", 0)}</td>
                    <td>{r.get("others_ytd", 0)}</td>
                    <td>{r.get("p91_minus_others_today", 0)}</td>
                    <td>{r.get("p91_minus_others_month", 0)}</td>
                    <td>{r.get("p91_minus_others_ytd", 0)}</td>
                </tr>
            """

    # ---------------------------
    # BRAND TABLE
    # ---------------------------
    else:
        header = """
            <tr>
                <th>Brand</th>
                <th>Today</th>
                <th>Month</th>
                <th>YTD</th>
            </tr>
        """

        rows_html = ""
        for r in data:
            rows_html += f"""
                <tr>
                    <td>{r.get("group_value")}</td>
                    <td>{r.get("today_sales", 0)}</td>
                    <td>{r.get("month_sales", 0)}</td>
                    <td>{r.get("ytd_sales", 0)}</td>
                </tr>
            """

    return f"""
        <h4>{title}</h4>
        <table border="1" cellpadding="6" cellspacing="0" width="100%">
            {header}
            {rows_html}
        </table>
    """

# ===================================== End ====================================================