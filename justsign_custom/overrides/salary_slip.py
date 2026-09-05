import frappe
from frappe.utils import flt

from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip


class CustomSalarySlip(SalarySlip):
	absent_deduction_component = "Absent Deduction"

	def set_net_pay(self):
		self.set_absent_deduction()
		return super().set_net_pay()

	def set_absent_deduction(self):
		if self.custom_set_comp_value_manually != 1:
			self.deductions = [
				d for d in self.deductions if d.salary_component != self.absent_deduction_component
			]

			if not self.total_working_days or not self.absent_days:
				return

			amount = flt(
				flt(self.gross_pay) / flt(self.total_working_days) * flt(self.absent_days),
				self.precision("amount", "deductions"),
			)

			if not amount:
				return

			self.append(
				"deductions",
				{
					"salary_component": self.absent_deduction_component,
					"abbr": frappe.get_cached_value(
						"Salary Component", self.absent_deduction_component, "salary_component_abbr"
					),
					"amount": amount,
					"default_amount": amount,
					"additional_amount": 0,
					"depends_on_payment_days": 0,
				},
			)

	def update_component_row(
		self,
		component_data,
		amount,
		component_type,
		additional_salary=None,
		is_recurring=0,
		data=None,
		default_amount=None,
		remove_if_zero_valued=None,
	):
		if self.get("custom_set_comp_value_manually") and not additional_salary:
			component_row = self.get_manual_component_row(component_data, component_type)
			if component_row:
				component_row.amount = flt(component_row.amount, component_row.precision("amount"))
				component_row.default_amount = 0
				component_row.additional_amount = 0

				if data:
					data[component_row.abbr] = component_row.amount

				return

		return super().update_component_row(
			component_data,
			amount,
			component_type,
			additional_salary=additional_salary,
			is_recurring=is_recurring,
			data=data,
			default_amount=default_amount,
			remove_if_zero_valued=remove_if_zero_valued,
		)

	def get_manual_component_row(self, component_data, component_type):
		for row in self.get(component_type):
			if row.salary_component == component_data.salary_component and not row.additional_salary:
				return row
