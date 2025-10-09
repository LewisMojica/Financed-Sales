# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from financed_sales.financed_sales.update_payments import auto_alloc_payments, apply_installments_state
from datetime import datetime, date


class PaymentPlan(Document):
	def validate(self):
		self.validate_credit_invoice()
		self.validate_installments()
	
	def validate_credit_invoice(self):
		"""Validate that credit invoice is provided"""
		if not self.credit_invoice:
			frappe.throw("Credit Invoice is mandatory. Please select a credit invoice.")
	
	def validate_installments(self):
		"""Validate that installments table is not empty"""
		if not self.installments:
			frappe.throw("Installments table cannot be empty. Please add at least one installment.")
	
	def before_submit(self):
		state = auto_alloc_payments(self.down_payment_amount, self.installments, self.payment_refs)
		apply_installments_state(self, state)
		self.update_payment_plan_state()
	
	def after_submit(self):
		"""Update Payment Plan state after successful submission"""
		try:
			self.save_payment_plan_state()
		except Exception as e:
			frappe.log_error(f"Failed to update Payment Plan {self.name} state after submit: {str(e)}")
	
	def calculate_payment_plan_state(self):
		"""Calculate Payment Plan state based on installment payment status and due dates"""
		if not self.installments:
			return "Draft"
		
		today = date.today()
		has_overdue = False
		all_paid = True
		
		for installment in self.installments:
			# Check if installment is overdue
			if installment.due_date and installment.due_date < today and installment.pending_amount > 0:
				has_overdue = True
			
			# Check if all installments are fully paid
			if installment.pending_amount > 0:
				all_paid = False
		
		# State priority: Completed > Overdue > Active
		if all_paid:
			return "Completed"
		elif has_overdue:
			return "Overdue"
		else:
			return "Active"
	
	def update_payment_plan_state(self):
		"""Update Payment Plan status based on current installment state"""
		new_state = self.calculate_payment_plan_state()
		if self.status != new_state:
			self.status = new_state
	
	def save_payment_plan_state(self):
		"""Save Payment Plan state to database in separate transaction"""
		try:
			frappe.db.set_value("Payment Plan", self.name, "status", self.status)
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Failed to update Payment Plan {self.name} status: {str(e)}")
			# Don't raise exception to avoid breaking payment processing
	
	def calculate_overdue_penalties(self):
		"""Calculate progressive penalties for overdue installments using 30-day periods.
		
		Penalty structure:
		- Days 1-5: Grace period (no penalty)
		- Days 6-35: 5% penalty (period 1)
		- Days 36-65: 10% penalty (period 2)  
		- Days 66-95: 15% penalty (period 3)
		- And so on...
		
		Uses fixed 30-day periods as requested by client.
		Formula: penalty_amount = installment_amount × periods_overdue × 5%
		
		Returns:
			int: Number of installments that had penalties updated.
		"""
		import math
		
		if not self.installments:
			return 0
		
		today = date.today()
		updated_count = 0
		
		for installment in self.installments:
			# Check if installment is overdue and has pending amount
			if (installment.due_date and 
				installment.due_date < today and 
				installment.pending_amount > 0):
				
				# Calculate days overdue
				days_overdue = (today - installment.due_date).days
				
				# Calculate penalty based on 30-day periods with grace period
				if days_overdue <= 5:
					# Grace period - no penalty
					new_penalty = 0
				else:
					# Calculate 30-day periods overdue after grace period
					days_after_grace = days_overdue - 5
					periods_overdue = math.ceil(days_after_grace / 30.0)
					penalty_rate = periods_overdue * 0.05  # 5% per 30-day period
					# Calculate penalty on unpaid installment amount (excluding previous penalties)
					unpaid_installment = installment.amount - installment.paid_amount
					new_penalty = round(unpaid_installment * penalty_rate, 2)
				
				# Calculate expected pending amount including penalty
				expected_pending_amount = (installment.amount - installment.paid_amount) + new_penalty

				# Update if penalty amount or pending amount needs correction
				if (installment.penalty_amount != new_penalty or
					abs(installment.pending_amount - expected_pending_amount) > 0.01):

					# Use direct database update for submitted documents
					frappe.db.set_value("Payment Plan Installment", installment.name, {
						"penalty_amount": new_penalty,
						"pending_amount": expected_pending_amount
					})
					updated_count += 1
		
		if updated_count > 0:
			frappe.db.commit()
		
		return updated_count
	
	@staticmethod
	def check_overdue_payment_plans():
		"""Check and update Payment Plans with overdue installments"""
		today = date.today()
		
		# Find Payment Plans with overdue installments
		overdue_plans = frappe.db.sql("""
			SELECT DISTINCT pp.name
			FROM `tabPayment Plan` pp
			INNER JOIN `tabPayment Plan Installment` ppi ON pp.name = ppi.parent
			WHERE pp.status IN ('Active', 'Draft')
			AND ppi.due_date < %s
			AND ppi.pending_amount > 0
			AND pp.docstatus = 1
		""", (today,), as_dict=True)
		
		# Update status to Overdue
		for plan in overdue_plans:
			frappe.db.set_value("Payment Plan", plan.name, "status", "Overdue")
		
		return len(overdue_plans)

	def before_cancel(self):
		"""Handle cleanup when cancelling Payment Plan"""
		# Cancel Sales Invoice if it exists
		if self.credit_invoice:
			sales_invoice = frappe.get_doc("Sales Invoice", self.credit_invoice)
			if sales_invoice.docstatus == 1:  # Only cancel if submitted
				sales_invoice.flags.ignore_links = True
				sales_invoice.cancel()

		# Cancel Sales Order from Finance Application if it exists
		if self.finance_application:
			finance_app = frappe.get_doc("Finance Application", self.finance_application)
			if finance_app.sales_order:
				sales_order = frappe.get_doc("Sales Order", finance_app.sales_order)
				if sales_order.docstatus == 1:  # Only cancel if submitted
					sales_order.flags.ignore_links = True
					sales_order.cancel()

		# Cancel Factura Proforma from Finance Application if it exists
		if self.finance_application:
			factura_list = frappe.get_all('Factura Proforma',
				filters={'finance_application': self.finance_application, 'docstatus': 1})
			for factura in factura_list:
				factura_doc = frappe.get_doc('Factura Proforma', factura.name)
				factura_doc.flags.ignore_links = True
				factura_doc.cancel()

		# Set flag to ignore links during cancellation
		self.flags.ignore_links = True

