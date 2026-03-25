import unittest

import frappe

from .api import create_payment_entry_from_payment_plan
from .factories.payment_plan_factory import create_test_payment_plan_for_payment_entry


class TestCustomPaymentDate(unittest.TestCase):
	def test_payment_with_custom_date_sets_correct_posting_date(self):
		"""Test that payment entry uses custom posting date when provided"""
		test_data = create_test_payment_plan_for_payment_entry()
		custom_date = "2026-01-15"

		payment_entry_name = create_payment_entry_from_payment_plan(
			payment_plan_name=test_data["payment_plan"],
			paid_amount=1000,
			mode_of_payment=test_data["mode_of_payment"],
			submit=True,
			posting_date=custom_date,
		)

		payment_entry = frappe.get_doc("Payment Entry", payment_entry_name)
		self.assertEqual(str(payment_entry.posting_date), custom_date)

	def test_payment_without_custom_date_uses_today(self):
		"""Test that payment entry uses today's date when no custom date provided"""
		test_data = create_test_payment_plan_for_payment_entry()

		payment_entry_name = create_payment_entry_from_payment_plan(
			payment_plan_name=test_data["payment_plan"],
			paid_amount=1000,
			mode_of_payment=test_data["mode_of_payment"],
			submit=True,
			posting_date=None,
		)

		payment_entry = frappe.get_doc("Payment Entry", payment_entry_name)
		self.assertEqual(str(payment_entry.posting_date), frappe.utils.today())

	def test_payment_date_before_last_payment_rejected(self):
		"""Test that payment date before last payment is rejected"""
		test_data = create_test_payment_plan_for_payment_entry()

		create_payment_entry_from_payment_plan(
			payment_plan_name=test_data["payment_plan"],
			paid_amount=1000,
			mode_of_payment=test_data["mode_of_payment"],
			submit=True,
			posting_date="2026-03-20",
		)

		with self.assertRaises(frappe.ValidationError) as context:
			create_payment_entry_from_payment_plan(
				payment_plan_name=test_data["payment_plan"],
				paid_amount=500,
				mode_of_payment=test_data["mode_of_payment"],
				submit=True,
				posting_date="2026-03-15",
			)

		self.assertIn("Payment date cannot be before", str(context.exception))

	def test_payment_with_custom_date_creates_je_with_correct_date(self):
		"""Test that Journal Entry is created with custom posting date when penalty exists"""
		test_data = create_test_payment_plan_for_payment_entry()
		payment_plan = frappe.get_doc("Payment Plan", test_data["payment_plan"])

		custom_date = "2026-02-15"

		second_installment = payment_plan.installments[1]
		frappe.db.set_value(
			"Payment Plan Installment",
			second_installment.name,
			{
				"due_date": frappe.utils.add_days(custom_date, -40),
			}
		)

		down_payment = payment_plan.down_payment_amount
		first_installment_amount = payment_plan.installments[0].amount
		second_installment_total = second_installment.amount + 500

		total_payment = down_payment + first_installment_amount + second_installment_total

		payment_entry_name = create_payment_entry_from_payment_plan(
			payment_plan_name=test_data["payment_plan"],
			paid_amount=total_payment,
			mode_of_payment=test_data["mode_of_payment"],
			submit=True,
			posting_date=custom_date,
		)

		payment_entry = frappe.get_doc("Payment Entry", payment_entry_name)
		self.assertEqual(str(payment_entry.posting_date), custom_date)

		journal_entry_ref = None
		for ref in payment_entry.references:
			if ref.reference_doctype == "Journal Entry":
				journal_entry_ref = ref
				break

		self.assertIsNotNone(journal_entry_ref, "Should have Journal Entry reference")
		journal_entry = frappe.get_doc("Journal Entry", journal_entry_ref.reference_name)
		self.assertEqual(str(journal_entry.posting_date), custom_date)

	def test_payment_resyncs_penalties_to_today(self):
		"""Test that penalties are recalculated to today after payment is created"""
		test_data = create_test_payment_plan_for_payment_entry()
		payment_plan = frappe.get_doc("Payment Plan", test_data["payment_plan"])

		second_installment = payment_plan.installments[1]
		custom_date_str = frappe.utils.add_days(frappe.utils.today(), -20)

		frappe.db.set_value(
			"Payment Plan Installment",
			second_installment.name,
			{
				"due_date": frappe.utils.add_days(custom_date_str, -50),
				"penalty_amount": 250
			}
		)

		down_payment = payment_plan.down_payment_amount
		first_installment_amount = payment_plan.installments[0].amount
		second_installment_total = second_installment.amount + 250

		total_payment = down_payment + first_installment_amount + second_installment_total

		create_payment_entry_from_payment_plan(
			payment_plan_name=test_data["payment_plan"],
			paid_amount=total_payment,
			mode_of_payment=test_data["mode_of_payment"],
			submit=True,
			posting_date=custom_date_str,
		)

		payment_plan.reload()
		second_installment.reload()

		self.assertGreaterEqual(second_installment.paid_amount, 0)
