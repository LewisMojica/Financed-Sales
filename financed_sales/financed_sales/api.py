import json
import math
from datetime import date
from types import SimpleNamespace

import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe import _

from .allocation_wrapper import analyze_payment_allocation
from .penalty_journal import create_penalty_journal_entry


def calculate_penalty_for_date(due_date, installment_amount, paid_amount, reference_date):
	"""
	Calculate penalty for an installment based on a specific date.
	
	Args:
		due_date: The due date of the installment
		installment_amount: The original installment amount
		paid_amount: Amount already paid toward the installment
		reference_date: The date to calculate penalty for (typically payment date)
	
	Returns:
		float: Calculated penalty amount (0 if not overdue or in grace period)
	"""
	if not due_date:
		return 0
	
	ref_date = reference_date if isinstance(reference_date, date) else frappe.utils.getdate(reference_date)
	due = due_date if isinstance(due_date, date) else frappe.utils.getdate(due_date)
	
	if due >= ref_date:
		return 0  # Not overdue
	
	days_overdue = (ref_date - due).days
	
	if days_overdue <= 5:
		return 0  # Grace period
	
	# Calculate 30-day periods overdue after grace period
	days_after_grace = days_overdue - 5
	periods_overdue = math.ceil(days_after_grace / 30.0)
	penalty_rate = periods_overdue * 0.05  # 5% per 30-day period
	
	# Calculate penalty on unpaid installment amount
	unpaid_installment = installment_amount - paid_amount
	return round(unpaid_installment * penalty_rate, 2)


def recalculate_installment_penalties_for_date(payment_plan_doc, reference_date):
	"""
	Recalculate penalty amounts for overdue installments in a payment plan based on a specific date.
	Only updates installments that ARE overdue on the reference date.
	For installments not yet due, preserves existing penalty amounts.
	
	Args:
		payment_plan_doc: Payment Plan document
		reference_date: The date to calculate penalties for
	
	Returns:
		list: Names of installments that were updated
	"""
	from datetime import date as date_type
	
	updated_installments = []
	ref_date = reference_date if isinstance(reference_date, (date, str)) else frappe.utils.getdate(reference_date)
	if isinstance(ref_date, str):
		ref_date = frappe.utils.getdate(ref_date)
	
	for installment in payment_plan_doc.installments:
		# Skip fully paid installments
		if installment.paid_amount >= installment.amount:
			continue
		
		# Only recalculate for installments that ARE overdue on the reference date
		due_date = installment.due_date
		if isinstance(due_date, str):
			due_date = frappe.utils.getdate(due_date)
		
		# If not overdue on reference date, preserve existing penalty
		if not due_date or due_date >= ref_date:
			continue
		
		new_penalty = calculate_penalty_for_date(
			installment.due_date,
			installment.amount,
			installment.paid_amount,
			reference_date
		)
		
		if installment.penalty_amount != new_penalty:
			# Update the penalty amount in the database
			frappe.db.set_value(
				"Payment Plan Installment",
				installment.name,
				"penalty_amount",
				new_penalty
			)
			updated_installments.append(installment.name)
	
	if updated_installments:
		frappe.db.commit()
	
	return updated_installments


def validate_payment_date(payment_plan_name, posting_date):
	if not posting_date:
		return
	result = frappe.db.sql(
		"SELECT MAX(date) as max_date FROM `tabFinanced Payment Ref` WHERE parent = %s",
		payment_plan_name,
	)
	last_date = result[0][0] if result and result[0] else None
	if last_date:
		if isinstance(posting_date, str):
			posting_date = frappe.utils.getdate(posting_date)
		if posting_date < last_date:
			frappe.throw(
				_(f"Payment date cannot be before {frappe.format(last_date, 'Date')}. "
				  "Payments must be recorded in chronological order.")
			)


@frappe.whitelist()
def create_finance_app_from_pos_cart(customer, items):
	"""
	Create a Sales Quotation and Finance Appication
	from a POS cart.
	`customer`: string, Customer name or ID
	`items`: list of dicts [{ item_code, qty, rate }, …]
	Returns: { name: <new Finance Application name> }
	"""
	items = json.loads(items)
	# 1. Validation
	if not customer:
		frappe.throw(_("No customer specified"))

	if not items:
		frappe.throw(_("Cart is empty"))

	# 2. Build Quotation items
	quotation_items = []
	for row in items:
		print("row", row)
		quotation_items.append(
			{
				"doctype": "Quotation Item",
				"item_code": row["item_code"],
				"qty": row["qty"],
				"rate": row["rate"],
			}
		)

	# 3. Create and insert the Quotation
	quotation = frappe.get_doc(
		{
			"doctype": "Quotation",
			"party_name": customer,
			"transaction_date": frappe.utils.today(),
			"valid_till": frappe.utils.add_days(frappe.utils.today(), 30),
			"items": quotation_items,
		}
	).insert(ignore_permissions=True)
	quotation.submit()

	return create_finance_application(quotation.name)


@frappe.whitelist()
def create_finance_application(quotation_name):
	"""
	Creates a Finance Application from a Quotation.
	`quotation_name`: Quotation name from which the Finance
	Application will be created.
	Returns: {'name': <new Finance Application name>'}
	"""
	settings = frappe.get_single("Financed Sales Settings")
	quotation = frappe.get_doc("Quotation", quotation_name)
	down_payment = (settings.down_payment_percent or 0) * quotation.grand_total / 100
	application = frappe.get_doc(
		{
			"doctype": "Finance Application",
			"customer": quotation.party_name,
			"quotation": quotation.name,
			"total_amount_to_finance": quotation.grand_total,
			"down_payment_amount": down_payment,
			"pending_down_payment_amount": down_payment,
			"interest_rate": settings.interest_rate,
			"application_fee": settings.application_fee,
			"rate_period": settings.rate_period or "Monthly",
		}
	).insert()

	return {"name": application.name}


@frappe.whitelist()
def create_down_payment_from_fin_app(fin_app_name):
	"""
	Creates a payment entry for the down payment amount specified
	in the `fin_app_name` param.
	The created payment entry is linked to the Sales Order or
	(credit) Sales Invoice (if it already created) referenced in
	param `fin_app_name`.
	`fin_app_name`: Fiance Application from which the Sales Order or
	(credit) Sales invoice will be taken to link in the payment entry
	Returns: <new Payment Entry name>
	"""
	fin_app = frappe.get_doc("Finance Application", fin_app_name)
	pe = get_payment_entry("Sales Order", fin_app.sales_order, party_amount=fin_app.down_payment)
	pe.custom_is_finance_down_payment = 1
	return pe


@frappe.whitelist()
def create_payment_entry_from_payment_plan(
	payment_plan_name, paid_amount, mode_of_payment, submit=False, reference_number=None, reference_date=None, posting_date=None
):
	# Validate required parameters
	if not mode_of_payment:
		frappe.throw(_("Payment method is required. Please select a payment method."))
	if not paid_amount:
		frappe.throw(_("Payment amount is required. Please enter the amount to pay."))

	paid_amount = float(paid_amount)

	# Validate payment date is not before last payment
	if posting_date:
		validate_payment_date(payment_plan_name, posting_date)

	# Get payment plan document for allocation analysis
	payment_plan = frappe.get_doc("Payment Plan", payment_plan_name)

	# Recalculate penalties based on payment date (not today)
	# This ensures penalty reflects the date being recorded
	reference_date = posting_date if posting_date else frappe.utils.today()
	recalculate_installment_penalties_for_date(payment_plan, reference_date)
	
	# Reload payment plan to get updated penalty amounts
	payment_plan.reload()

	# Use allocation analysis to determine if penalty payment is needed
	allocation_result = analyze_payment_allocation(payment_plan, paid_amount)

	journal_entry_name = None

	# If penalty amount exists, create journal entry first
	if allocation_result["penalty_amount"] > 0:
		journal_entry_name = create_penalty_journal_entry(
			penalty_amount=allocation_result["penalty_amount"],
			customer=payment_plan.customer,
			payment_plan_name=payment_plan_name,
			posting_date=posting_date,
		)

	# Create payment entry with appropriate references
	si_name = frappe.db.get_value("Payment Plan", payment_plan_name, "credit_invoice")
	si = SimpleNamespace(doctype="Sales Invoice", name=si_name)

	return create_payment_entry(
		si,
		paid_amount,
		mode_of_payment,
		submit,
		reference_number,
		reference_date,
		journal_entry_name,
		allocation_result["penalty_amount"],
		posting_date,
	)


@frappe.whitelist()
def create_payment_entry_from_finance_application(
	finance_application_name,
	paid_amount,
	mode_of_payment,
	submit=False,
	reference_number=None,
	reference_date=None,
):
	# Validate required parameters
	if not mode_of_payment:
		frappe.throw(_("Payment method is required. Please select a payment method."))
	if not paid_amount:
		frappe.throw(_("Payment amount is required. Please enter the amount to pay."))

	paid_amount = float(paid_amount)
	so_name = frappe.db.get_value("Finance Application", finance_application_name, "sales_order")
	so = SimpleNamespace(doctype="Sales Order", name=so_name)
	return create_payment_entry(so, paid_amount, mode_of_payment, submit, reference_number, reference_date)


def create_payment_entry(
	doc,
	paid_amount,
	mode_of_payment,
	submit=False,
	reference_number=None,
	reference_date=None,
	journal_entry_reference=None,
	penalty_amount=0,
	posting_date=None,
):
	pe = get_payment_entry(doc.doctype, doc.name, party_amount=paid_amount)
	pe.mode_of_payment = mode_of_payment

	mode_of_payment_doc = frappe.get_doc("Mode of Payment", mode_of_payment)
	if not mode_of_payment_doc.accounts:
		frappe.throw(
			f"No accounts configured for Mode of Payment '{mode_of_payment}'. Please configure at least one account."
		)

	account = mode_of_payment_doc.accounts[0].default_account
	if not account:
		frappe.throw(
			f"Default account not set for Mode of Payment '{mode_of_payment}'. Please configure the default account."
		)

	pe.paid_to = account
	pe.custom_is_finance_payment = 1

	if posting_date:
		pe.posting_date = posting_date

	# Set reference number and date for Bank type payments
	mode_of_payment_type = frappe.db.get_value("Mode of Payment", mode_of_payment, "type")
	if mode_of_payment_type == "Bank" and reference_number:
		pe.reference_no = reference_number
	if mode_of_payment_type == "Bank" and reference_date:
		pe.reference_date = reference_date

	# Add dual reference support - add journal entry reference if provided
	if journal_entry_reference:
		# Adjust Sales Invoice allocation to principal amount only (exclude penalty)
		principal_amount = paid_amount - penalty_amount
		for ref in pe.references:
			if ref.reference_doctype == "Sales Invoice":
				ref.allocated_amount = principal_amount
				break

		# Payment entry should now have dual references: Sales Invoice + Journal Entry
		pe.append(
			"references",
			{
				"reference_doctype": "Journal Entry",
				"reference_name": journal_entry_reference,
				"allocated_amount": penalty_amount,  # Allocate the penalty amount
			},
		)

	pe.save()
	if submit:
		pe.submit()
	return pe.name


@frappe.whitelist()
def get_or_create_carta_de_saldo(payment_plan_name):
	"""
	Check for an existing Carta de Saldo for this payment plan.
	Priority: Submitted > Draft > Create New.
	"""
	# 1. Check for submitted
	submitted = frappe.db.get_value(
		"Carta de Saldo", {"payment_plan": payment_plan_name, "docstatus": 1}, "name"
	)
	if submitted:
		return submitted

	# 2. Check for draft
	draft = frappe.db.get_value(
		"Carta de Saldo", {"payment_plan": payment_plan_name, "docstatus": 0}, "name"
	)
	if draft:
		return draft

	# 3. Create new
	status = frappe.db.get_value("Payment Plan", payment_plan_name, "status")
	if status != "Completed":
		frappe.throw(_("La Carta de Saldo solo puede ser creada para Planes de Pago completados."))

	doc = frappe.new_doc("Carta de Saldo")
	doc.payment_plan = payment_plan_name
	doc.insert()
	return doc.name
