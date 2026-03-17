# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class CartadeSaldo(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from financed_sales.financed_sales.doctype.carta_de_saldo_installment.carta_de_saldo_installment import CartadeSaldoInstallment
		from financed_sales.financed_sales.doctype.carta_de_saldo_payment.carta_de_saldo_payment import CartadeSaldoPayment

		amended_from: DF.Link | None
		credit_invoice: DF.Link | None
		customer: DF.Link | None
		customer_name: DF.Data | None
		finance_application: DF.Link | None
		installments: DF.Table[CartadeSaldoInstallment]
		issue_date: DF.Date
		payment_history: DF.Table[CartadeSaldoPayment]
		payment_plan: DF.Link
		total_financed_amount: DF.Currency
		total_paid: DF.Currency
	# end: auto-generated types

	def validate(self):
		self.validate_payment_plan_completed()

	def before_insert(self):
		self.snapshot_from_payment_plan()

	def validate_payment_plan_completed(self):
		"""Only allow Carta de Saldo for fully completed Payment Plans."""
		if not self.payment_plan:
			return

		status = frappe.db.get_value("Payment Plan", self.payment_plan, "status")
		if status != "Completed":
			frappe.throw(
				_("No se puede crear una Carta de Saldo para Plan de Pago {0}. El estado del Plan
	  es '{1}', pero debe ser 'Completado'.").format(
					self.payment_plan, status
				),
				title=_("Plan No Completado")
			)

	def snapshot_from_payment_plan(self):
		"""
		Snapshot installments and payment history from the linked Payment Plan.
		This makes the Carta de Saldo an immutable record of what was paid
		at the moment the letter was issued.
		"""
		if not self.payment_plan:
			return

		plan = frappe.get_doc("Payment Plan", self.payment_plan)

		# Clear any existing rows
		self.installments = []
		self.payment_history = []

		# Snapshot installments
		for row in plan.installments:
			self.append("installments", {
				"due_date": row.due_date,
				"amount": row.amount,
				"paid_amount": row.paid_amount,
				"pending_amount": row.pending_amount,
				"payment_ref": row.payment_ref,
				"penalty_amount": row.penalty_amount or 0,
			})

		# Snapshot payment references (actual Payment Entries)
		for row in plan.payment_refs:
			self.append("payment_history", {
				"payment_entry": row.payment_entry,
				"amount": row.amount,
				"date": row.date,
			})

		# total_paid = sum of every actual payment made (includes down payment)
		self.total_paid = sum(row.amount or 0 for row in plan.payment_refs)

		# total_financed_amount = the original financed amount from the Finance Application
		if plan.finance_application:
			fin_app_amount = frappe.db.get_value(
				"Finance Application", plan.finance_application, "total_amount_to_finance"
			)
			self.total_financed_amount = fin_app_amount or 0
		else:
			# Fallback: sum of installment amounts if no finance application linked
			self.total_financed_amount = sum(row.amount or 0 for row in plan.installments)

		# Carry over linked documents if not already set via fetch_from
		if not self.customer:
			self.customer = plan.customer
		if not self.finance_application:
			self.finance_application = plan.finance_application
		if not self.credit_invoice:
			self.credit_invoice = plan.credit_invoice
