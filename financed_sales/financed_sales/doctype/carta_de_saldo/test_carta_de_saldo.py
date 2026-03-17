# Copyright (c) 2025, Lewis Mojica and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today


class TestCartaDeSaldo(FrappeTestCase):
	def _create_completed_payment_plan(self):
		"""
		Create a submitted Payment Plan whose installments are all fully paid
		so that its status is 'Completed', suitable for issuing a Carta de Saldo.
		"""
		from financed_sales.financed_sales.factories.payment_plan_factory import (
			_get_or_create_test_customer,
			_get_or_create_test_item,
			_create_test_credit_invoice,
		)
		from financed_sales.financed_sales.api import create_finance_application

		customer = _get_or_create_test_customer()
		item = _get_or_create_test_item()

		quotation = frappe.get_doc({
			"doctype": "Quotation",
			"party_name": customer,
			"transaction_date": today(),
			"valid_till": frappe.utils.add_days(today(), 30),
			"items": [{
				"doctype": "Quotation Item",
				"item_code": item,
				"qty": 1,
				"rate": 10000,
			}],
		}).insert(ignore_permissions=True)
		quotation.submit()

		finance_app_resp = create_finance_application(quotation.name)
		finance_app = frappe.get_doc("Finance Application", finance_app_resp["name"])
		finance_app.repayment_term = 3
		finance_app.interest_rate = 5.0
		finance_app.first_installment = frappe.utils.add_days(today(), 30)

		# Generate installments
		financed_amount = finance_app.total_amount_to_finance - (finance_app.down_payment_amount or 0)
		monthly = financed_amount / 3
		finance_app.installments = []
		for i in range(3):
			finance_app.append("installments", {
				"due_date": frappe.utils.add_months(finance_app.first_installment, i),
				"amount": monthly,
			})
		finance_app.save()

		credit_invoice = _create_test_credit_invoice(finance_app)

		# Build payment plan with all installments fully paid (pending = 0)
		plan = frappe.get_doc({
			"doctype": "Payment Plan",
			"finance_application": finance_app.name,
			"customer": finance_app.customer,
			"credit_invoice": credit_invoice.name,
			"down_payment_amount": 0,
			"paid_down_payment_amount": 0,
			"pending_down_payment_amount": 0,
		})
		for inst in finance_app.installments:
			plan.append("installments", {
				"due_date": frappe.utils.getdate(inst.due_date),
				"amount": inst.amount,
				"paid_amount": inst.amount,  # Fully paid
				"pending_amount": 0,
				"penalty_amount": 0,
			})

		plan.insert(ignore_permissions=True)
		plan.submit()

		# Force status to Completed
		frappe.db.set_value("Payment Plan", plan.name, "status", "Completed")

		return plan.name, finance_app.customer, len(finance_app.installments)

	def test_carta_de_saldo_snapshots_installments(self):
		"""
		Creating a Carta de Saldo for a Completed Payment Plan should copy
		all installment rows into the carta_de_saldo child table.
		"""
		plan_name, customer, installment_count = self._create_completed_payment_plan()

		carta = frappe.get_doc({
			"doctype": "Carta de Saldo",
			"payment_plan": plan_name,
			"issue_date": today(),
		})
		carta.insert(ignore_permissions=True)

		self.assertEqual(
			len(carta.installments),
			installment_count,
			"Carta de Saldo installments count should match Payment Plan installments count",
		)
		self.assertEqual(
			carta.customer, customer,
			"Customer should be carried over from Payment Plan",
		)
		self.assertGreater(
			carta.total_financed_amount, 0,
			"total_financed_amount should be populated",
		)

	def test_carta_de_saldo_totals(self):
		"""
		total_paid should equal the sum of paid_amount across all installments.
		"""
		plan_name, _, _ = self._create_completed_payment_plan()

		carta = frappe.get_doc({
			"doctype": "Carta de Saldo",
			"payment_plan": plan_name,
			"issue_date": today(),
		})
		carta.insert(ignore_permissions=True)

		expected_paid = sum(row.paid_amount for row in carta.installments)
		self.assertAlmostEqual(
			carta.total_paid, expected_paid, places=2,
			msg="total_paid should equal sum of paid_amount across installment rows",
		)

	def test_carta_de_saldo_rejects_non_completed_plan(self):
		"""
		Creating a Carta de Saldo for a non-Completed Payment Plan should raise a ValidationError.
		"""
		from financed_sales.financed_sales.factories.payment_plan.base import create_payment_plan

		result = create_payment_plan()
		plan = frappe.get_doc("Payment Plan", result["payment_plan"])

		# Ensure it is NOT Completed (Active is the default after submit)
		self.assertNotEqual(plan.status, "Completed")

		carta = frappe.get_doc({
			"doctype": "Carta de Saldo",
			"payment_plan": plan.name,
			"issue_date": today(),
		})

		with self.assertRaises(frappe.ValidationError):
			carta.insert(ignore_permissions=True)

	def test_carta_de_saldo_is_submittable(self):
		"""
		A Carta de Saldo should be submittable (docstatus 1) and once submitted
		the child tables remain intact.
		"""
		plan_name, _, installment_count = self._create_completed_payment_plan()

		carta = frappe.get_doc({
			"doctype": "Carta de Saldo",
			"payment_plan": plan_name,
			"issue_date": today(),
		})
		carta.insert(ignore_permissions=True)
		carta.submit()

		carta.reload()
		self.assertEqual(carta.docstatus, 1, "Carta de Saldo should be in submitted state")
		self.assertEqual(
			len(carta.installments), installment_count,
			"Installments should remain intact after submission",
		)
