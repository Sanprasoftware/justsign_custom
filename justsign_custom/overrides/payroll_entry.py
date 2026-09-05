import frappe
from frappe import _
from frappe.utils import get_link_to_form

from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry


class CustomPayrollEntry(PayrollEntry):
	def validate_payroll_payable_account(self):
		account_type = frappe.db.get_value("Account", self.payroll_payable_account, "account_type")

		if account_type != "Payable":
			frappe.throw(
				_(
					"Account type should be set {0} for payroll payable account {1}, please set and try again"
				).format(
					frappe.bold(_("Payable")),
					frappe.bold(get_link_to_form("Account", self.payroll_payable_account)),
				)
			)

	def make_journal_entry(self, accounts, currencies, *args, **kwargs):
		for row in accounts:
			if row.get("reference_type") == self.doctype and row.get("reference_name") == self.name:
				row["reference_type"] = None
				row["reference_name"] = None

		journal_entry = super().make_journal_entry(accounts, currencies, *args, **kwargs)

		if frappe.get_meta("Journal Entry").has_field("custom_payroll_entry"):
			journal_entry.db_set("custom_payroll_entry", self.name, update_modified=False)

		return journal_entry

	def cancel_linked_journal_entries(self):
		journal_entries = self.get_linked_journal_entries()

		for je in journal_entries:
			journal_entry_payment_ledgers = frappe.get_all(
				"Payment Ledger Entry",
				{"voucher_type": "Journal Entry", "voucher_no": je, "docstatus": 1},
				distinct=True,
			)

			for pl in journal_entry_payment_ledgers:
				payment_ledger_entry = frappe.get_doc("Payment Ledger Entry", pl)
				payment_ledger_entry.flags.ignore_permissions = True
				payment_ledger_entry.cancel()

			journal_entry = frappe.get_doc("Journal Entry", je)
			journal_entry.flags.ignore_permissions = True
			journal_entry.cancel()

	def get_linked_journal_entries(self):
		journal_entries = set()

		if frappe.db.has_column("Journal Entry", "custom_payroll_entry"):
			journal_entries.update(
				frappe.get_all(
					"Journal Entry",
					{"custom_payroll_entry": self.name, "docstatus": 1},
					pluck="name",
				)
			)

		journal_entries.update(
			frappe.get_all(
				"Journal Entry Account",
				{"reference_type": self.doctype, "reference_name": self.name, "docstatus": 1},
				pluck="parent",
				distinct=True,
			)
		)

		return list(journal_entries)

	@frappe.whitelist()
	def has_bank_entries(self) -> dict[str, bool]:
		if frappe.db.has_column("Journal Entry", "custom_payroll_entry"):
			bank_entries = frappe.get_all(
				"Journal Entry",
				{
					"custom_payroll_entry": self.name,
					"voucher_type": ["in", ["Bank Entry", "Cash Entry"]],
					"docstatus": ["!=", 2],
				},
				pluck="name",
			)
		else:
			bank_entries = []

		if not bank_entries:
			bank_entries = frappe.get_all(
				"Journal Entry Account",
				{
					"reference_type": self.doctype,
					"reference_name": self.name,
					"parenttype": "Journal Entry",
					"docstatus": ["!=", 2],
				},
				pluck="parent",
				distinct=True,
			)

		return {
			"has_bank_entries": bool(bank_entries),
			"has_bank_entries_for_withheld_salaries": not any(
				employee.is_salary_withheld for employee in self.employees
			),
		}


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_payroll_entries_for_jv(doctype, txt, searchfield, start, page_len, filters):
	if frappe.db.has_column("Journal Entry", "custom_payroll_entry"):
		return frappe.db.sql(
			f"""
			select name from `tabPayroll Entry`
			where `{searchfield}` LIKE %(txt)s
			and name not in (
				select custom_payroll_entry from `tabJournal Entry`
				where ifnull(custom_payroll_entry, "") != ""
			)
			and name not in (
				select reference_name from `tabJournal Entry Account`
				where reference_type = "Payroll Entry"
			)
			order by name limit %(start)s, %(page_len)s
			""",
			{"txt": "%%%s%%" % txt, "start": start, "page_len": page_len},
		)

	return frappe.db.sql(
		f"""
		select name from `tabPayroll Entry`
		where `{searchfield}` LIKE %(txt)s
		and name not in (
			select reference_name from `tabJournal Entry Account`
			where reference_type = "Payroll Entry"
		)
		order by name limit %(start)s, %(page_len)s
		""",
		{"txt": "%%%s%%" % txt, "start": start, "page_len": page_len},
	)
