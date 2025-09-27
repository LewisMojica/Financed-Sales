# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from erpnext.accounts.party import get_party_account


def create_penalty_journal_entry(penalty_amount, customer, payment_plan_name):
	"""
	Create Journal Entry document for penalty amounts with proper accounting entries.

	Creates double-entry accounting for penalty:
	- Debit: Customer receivable account (increases customer debt)
	- Credit: Penalty income account (recognizes penalty revenue)

	Args:
	    penalty_amount (float): Amount of penalty to be recorded
	    customer (str): Customer name
	    payment_plan_name (str): Payment Plan name for reference

	Returns:
	    str: Journal Entry name for referencing in payment entry

	Raises:
	    frappe.ValidationError: If penalty account is not configured
	    frappe.ValidationError: If customer data is invalid
	"""

	# Validate penalty account configuration
	settings = frappe.get_single("Financed Sales Settings")
	if not settings.penalty_income_account:
		frappe.throw(
			"Penalty Income Account is not configured in Financed Sales Settings. Please configure it before processing penalty payments."
		)

	penalty_account = settings.penalty_income_account

	# Get payment plan and extract company information through Finance Application -> Quotation
	payment_plan = frappe.get_doc("Payment Plan", payment_plan_name)

	if not payment_plan.finance_application:
		frappe.throw(f"Payment Plan {payment_plan_name} must be linked to a Finance Application")

	finance_application = frappe.get_doc("Finance Application", payment_plan.finance_application)

	if not finance_application.quotation:
		frappe.throw(f"Finance Application {finance_application.name} must be linked to a Quotation")

	quotation = frappe.get_doc("Quotation", finance_application.quotation)
	company = quotation.company

	# Get customer's receivable account
	try:
		customer_account = get_party_account("Customer", customer, company)
	except Exception as e:
		frappe.throw(f"Failed to get customer receivable account for {customer}: {e!s}")

	if not customer_account:
		frappe.throw(f"No receivable account found for customer {customer} in company {company}")

	# Create Journal Entry
	je = frappe.new_doc("Journal Entry")
	je.voucher_type = "Journal Entry"
	je.posting_date = frappe.utils.today()
	je.company = company
	je.remark = f"Penalty entry for Payment Plan {payment_plan_name} - Customer: {customer}"

	# Add debit entry - Customer receivable (increases customer debt)
	je.append(
		"accounts",
		{
			"account": customer_account,
			"party_type": "Customer",
			"party": customer,
			"debit_in_account_currency": penalty_amount,
			"user_remark": f"Penalty for Payment Plan {payment_plan_name}",
		},
	)

	# Add credit entry - Penalty income account (recognizes penalty revenue)
	je.append(
		"accounts",
		{
			"account": penalty_account,
			"credit_in_account_currency": penalty_amount,
			"user_remark": f"Penalty for Payment Plan {payment_plan_name}",
		},
	)

	# Save and submit Journal Entry
	try:
		je.save()
		je.submit()
		return je.name
	except Exception as e:
		frappe.log_error(
			f"Failed to create penalty journal entry for Payment Plan {payment_plan_name}: {e!s}"
		)
		frappe.throw(f"Failed to create penalty journal entry: {e!s}")
