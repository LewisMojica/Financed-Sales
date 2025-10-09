# Copyright (c) 2024, Lewis Mojica and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_overdue_data(company):
	"""Get overdue payment plan data for the specified company."""
	if not company:
		frappe.throw(_("Please select a company"))

	# Get Payment Plan installments that are overdue
	from frappe.utils import today, date_diff

	overdue_installments = frappe.db.sql("""
		SELECT ppi.parent, ppi.due_date, ppi.pending_amount
		FROM `tabPayment Plan Installment` ppi
		INNER JOIN `tabPayment Plan` pp ON pp.name = ppi.parent
		WHERE ppi.due_date < %s
		AND ppi.pending_amount > 0
		AND pp.docstatus = 1
	""", (today(),), as_dict=True)

	# Group by Payment Plan and calculate overdue amounts
	overdue_plans = {}
	for installment in overdue_installments:
		plan_name = installment["parent"]
		if plan_name not in overdue_plans:
			overdue_plans[plan_name] = {
				"payment_plan": plan_name,
				"overdue_amount": 0,
				"oldest_due_date": installment["due_date"]
			}
		
		overdue_plans[plan_name]["overdue_amount"] += installment["pending_amount"]
		
		# Track oldest due date for days calculation
		if installment["due_date"] < overdue_plans[plan_name]["oldest_due_date"]:
			overdue_plans[plan_name]["oldest_due_date"] = installment["due_date"]

	# Get customer info and calculate days overdue
	result = []
	for plan_data in overdue_plans.values():
		payment_plan = frappe.get_doc("Payment Plan", plan_data["payment_plan"])

		plan_data["customer"] = payment_plan.customer
		plan_data["days_overdue"] = date_diff(today(), plan_data["oldest_due_date"])

		# Remove oldest_due_date from result
		del plan_data["oldest_due_date"]

		result.append(plan_data)

	# Sort by days overdue (most overdue first)
	result.sort(key=lambda x: x["days_overdue"], reverse=True)

	return result