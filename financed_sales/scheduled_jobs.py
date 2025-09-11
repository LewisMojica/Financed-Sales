# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

"""Scheduled jobs for Financed Sales app."""

import frappe
from financed_sales.financed_sales.page.overdue_financed_sales.overdue_financed_sales import get_overdue_data


def daily_penalty_calculation():
	"""Daily scheduled task to calculate penalties for all overdue payment plans.
	
	Uses the existing get_overdue_data function to identify payment plans with overdue
	installments and applies penalties to them.
	
	Returns:
		dict: Summary of penalty calculations with counts and totals.
	"""
	# Get the first company (assuming single company setup)
	company = frappe.get_all("Company", limit=1)
	if not company:
		frappe.log_error("No company found for penalty calculation", "Daily Penalty Calculation")
		return {"overdue_plans_processed": 0, "penalties_applied": 0}
	
	company_name = company[0]["name"]
	total_plans = 0
	total_penalties_applied = 0
	
	try:
		# Use existing overdue function to get overdue payment plans
		overdue_plans = get_overdue_data(company_name)
		
		# Process each overdue payment plan
		for plan_data in overdue_plans:
			try:
				payment_plan = frappe.get_doc("Payment Plan", plan_data["payment_plan"])
				penalties_applied = payment_plan.calculate_overdue_penalties()
				
				if penalties_applied > 0:
					payment_plan.save()
					total_penalties_applied += penalties_applied
				
				total_plans += 1
				
			except Exception as e:
				frappe.log_error(
					f"Failed to calculate penalties for Payment Plan {plan_data['payment_plan']}: {str(e)}",
					"Daily Penalty Calculation"
				)
	
	except Exception as e:
		frappe.log_error(
			f"Failed to get overdue data for company {company_name}: {str(e)}",
			"Daily Penalty Calculation"
		)
	
	# Log summary
	frappe.logger().info(
		f"Daily penalty calculation completed: {total_plans} overdue plans processed, "
		f"{total_penalties_applied} penalties applied"
	)
	
	return {
		"overdue_plans_processed": total_plans,
		"penalties_applied": total_penalties_applied
	}