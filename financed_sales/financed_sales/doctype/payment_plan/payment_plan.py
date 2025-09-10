# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from financed_sales.financed_sales.update_payments import auto_alloc_payments, apply_installments_state
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import math


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
		print('~~~~~~~~~~~~~~~~~~~lsubmitted!~~~~~~~~~~~~~~~~~~\n\n~~~~~~~~~~~~~~~~~~~~~~~~~')
		state = auto_alloc_payments(self.down_payment_amount, self.installments, self.payment_refs)
		apply_installments_state(self, state)
		self.update_payment_plan_state()
		print(state)
	
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
	
	@staticmethod
	def daily_overdue_check():
		"""Scheduled task handler for daily overdue check"""
		return PaymentPlan.check_overdue_payment_plans()
	
	def calculate_penalty_amounts(self):
		"""Calculate penalty amounts for overdue installments"""
		today = date.today()
		
		for installment in self.installments:
			if installment.due_date and installment.due_date < today and installment.pending_amount > 0:
				# Calculate months overdue (integer only)
				months_diff = relativedelta(today, installment.due_date)
				months_overdue = months_diff.years * 12 + months_diff.months
				
				# Ensure months_overdue is not negative (safety check)
				months_overdue = max(0, months_overdue)
				
				# Apply penalty formula: pending_amount * 0.05 * months_overdue
				penalty_amount = installment.pending_amount * 0.05 * months_overdue
				installment.penalty_amount = penalty_amount
			else:
				# No penalty if not overdue or fully paid
				installment.penalty_amount = 0
	
	@staticmethod
	def update_penalty_amounts_bulk():
		"""Update penalty amounts for all active payment plans with overdue installments"""
		today = date.today()
		
		# Find Payment Plans with overdue installments
		overdue_plans = frappe.db.sql("""
			SELECT DISTINCT pp.name
			FROM `tabPayment Plan` pp
			INNER JOIN `tabPayment Plan Installment` ppi ON pp.name = ppi.parent
			WHERE pp.status IN ('Active', 'Overdue')
			AND ppi.due_date < %s
			AND ppi.pending_amount > 0
			AND pp.docstatus = 1
		""", (today,), as_dict=True)
		
		updated_count = 0
		for plan_data in overdue_plans:
			try:
				# Load Payment Plan and calculate penalties
				plan = frappe.get_doc("Payment Plan", plan_data.name)
				plan.calculate_penalty_amounts()
				
				# Update penalty amounts in database
				for installment in plan.installments:
					if installment.penalty_amount:
						frappe.db.set_value(
							"Payment Plan Installment", 
							installment.name, 
							"penalty_amount", 
							installment.penalty_amount
						)
				
				updated_count += 1
			except Exception as e:
				frappe.log_error(f"Failed to update penalties for Payment Plan {plan_data.name}: {str(e)}")
		
		if updated_count > 0:
			frappe.db.commit()
		
		return updated_count
	
	@staticmethod
	def daily_penalty_update():
		"""Scheduled task handler for daily penalty updates"""
		return PaymentPlan.update_penalty_amounts_bulk()
