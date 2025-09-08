# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from financed_sales.financed_sales.update_payments import auto_alloc_payments, apply_installments_state


class PaymentPlan(Document):
	def validate(self):
		self.validate_installments()
	
	def validate_installments(self):
		"""Validate that installments table is not empty"""
		if not self.installments:
			frappe.throw("Installments table cannot be empty. Please add at least one installment.")
	
	def before_submit(self):
		print('~~~~~~~~~~~~~~~~~~~lsubmitted!~~~~~~~~~~~~~~~~~~\n\n~~~~~~~~~~~~~~~~~~~~~~~~~')
		state = auto_alloc_payments(self.down_payment_amount, self.installments, self.payment_refs)
		apply_installments_state(self, state)
		print(state)
