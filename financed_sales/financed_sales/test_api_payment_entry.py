import unittest

import frappe

from .api import create_payment_entry_from_payment_plan
from .factories.payment_plan_factory import create_test_payment_plan_for_payment_entry


class TestAPIPaymentEntry(unittest.TestCase):
	def test_create_payment_entry_single_reference_no_penalty(self):
		"""Test payment entry creation without penalty (single reference)"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_payment_entry()

		# Get payment plan to check installment amounts
		payment_plan = frappe.get_doc("Payment Plan", test_data["payment_plan"])

		# Test payment that covers only principal (no penalty expected)
		installment_amount = payment_plan.installments[0].amount  # First installment has no penalty
		penalty_amount = getattr(payment_plan.installments[0], "penalty_amount", 0) or 0

		self.assertEqual(penalty_amount, 0, "First installment should have no penalty for this test")

		# Create payment entry
		payment_entry_name = create_payment_entry_from_payment_plan(
			payment_plan_name=test_data["payment_plan"],
			paid_amount=installment_amount,
			mode_of_payment=test_data["mode_of_payment"],
			submit=False,
		)

		# Verify payment entry was created
		self.assertIsInstance(payment_entry_name, str)
		self.assertTrue(frappe.db.exists("Payment Entry", payment_entry_name))

		# Verify payment entry details
		payment_entry = frappe.get_doc("Payment Entry", payment_entry_name)
		self.assertEqual(payment_entry.paid_amount, installment_amount)
		self.assertEqual(payment_entry.mode_of_payment, test_data["mode_of_payment"])
		self.assertEqual(payment_entry.custom_is_finance_payment, 1)

		# Verify single reference (Sales Invoice only, no Journal Entry)
		self.assertEqual(len(payment_entry.references), 1)
		reference = payment_entry.references[0]
		self.assertEqual(reference.reference_doctype, "Sales Invoice")
		self.assertEqual(reference.reference_name, test_data["credit_invoice"])

	def test_create_payment_entry_dual_reference_with_penalty(self):
		"""Test payment entry creation with penalty (dual reference)"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_payment_entry()

		# Get payment plan to check installment amounts
		payment_plan = frappe.get_doc("Payment Plan", test_data["payment_plan"])

		# Find installment with penalty (installment 2 or 4 according to factory)
		installment_with_penalty = None
		for installment in payment_plan.installments:
			penalty_amount = getattr(installment, "penalty_amount", 0) or 0
			if penalty_amount > 0:
				installment_with_penalty = installment
				break

		self.assertIsNotNone(installment_with_penalty, "Test data should have installments with penalties")

		# Test payment that covers down payment + first installment + second installment (with penalty)
		# Need to cover down payment first, then first installment fully, then second installment with penalty
		down_payment_amount = payment_plan.down_payment_amount
		first_installment_amount = payment_plan.installments[0].amount
		installment_with_penalty_total = (
			installment_with_penalty.amount + installment_with_penalty.penalty_amount
		)
		total_payment = down_payment_amount + first_installment_amount + installment_with_penalty_total

		# Create payment entry
		payment_entry_name = create_payment_entry_from_payment_plan(
			payment_plan_name=test_data["payment_plan"],
			paid_amount=total_payment,
			mode_of_payment=test_data["mode_of_payment"],
			submit=False,
		)

		# Verify payment entry was created
		self.assertIsInstance(payment_entry_name, str)
		self.assertTrue(frappe.db.exists("Payment Entry", payment_entry_name))

		# Verify payment entry details
		payment_entry = frappe.get_doc("Payment Entry", payment_entry_name)
		self.assertEqual(payment_entry.paid_amount, total_payment)
		self.assertEqual(payment_entry.mode_of_payment, test_data["mode_of_payment"])
		self.assertEqual(payment_entry.custom_is_finance_payment, 1)

		# Verify dual references (Sales Invoice + Journal Entry)
		self.assertEqual(len(payment_entry.references), 2)

		# Find Sales Invoice and Journal Entry references
		sales_invoice_ref = None
		journal_entry_ref = None
		for ref in payment_entry.references:
			if ref.reference_doctype == "Sales Invoice":
				sales_invoice_ref = ref
			elif ref.reference_doctype == "Journal Entry":
				journal_entry_ref = ref

		# Verify Sales Invoice reference
		self.assertIsNotNone(sales_invoice_ref, "Should have Sales Invoice reference")
		self.assertEqual(sales_invoice_ref.reference_name, test_data["credit_invoice"])

		# Verify Journal Entry reference
		self.assertIsNotNone(journal_entry_ref, "Should have Journal Entry reference")
		self.assertTrue(frappe.db.exists("Journal Entry", journal_entry_ref.reference_name))

		# Verify Journal Entry was created with correct penalty amount
		journal_entry = frappe.get_doc("Journal Entry", journal_entry_ref.reference_name)
		total_debit = sum(entry.debit_in_account_currency for entry in journal_entry.accounts)
		self.assertEqual(total_debit, installment_with_penalty.penalty_amount)

	def test_create_payment_entry_partial_penalty_payment(self):
		"""Test payment entry creation with partial penalty payment"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_payment_entry()

		# Get payment plan to check installment amounts
		payment_plan = frappe.get_doc("Payment Plan", test_data["payment_plan"])

		# Find installment with penalty
		installment_with_penalty = None
		for installment in payment_plan.installments:
			penalty_amount = getattr(installment, "penalty_amount", 0) or 0
			if penalty_amount > 0:
				installment_with_penalty = installment
				break

		# Test payment that covers down payment + first installment + partial penalty
		# Need to cover down payment first, then first installment fully, then partial penalty
		down_payment_amount = payment_plan.down_payment_amount
		first_installment_amount = payment_plan.installments[0].amount
		partial_penalty = installment_with_penalty.penalty_amount / 2
		installment_with_partial_penalty = installment_with_penalty.amount + partial_penalty
		total_payment = down_payment_amount + first_installment_amount + installment_with_partial_penalty

		# Create payment entry
		payment_entry_name = create_payment_entry_from_payment_plan(
			payment_plan_name=test_data["payment_plan"],
			paid_amount=total_payment,
			mode_of_payment=test_data["mode_of_payment"],
			submit=False,
		)

		# Verify payment entry was created with dual references
		payment_entry = frappe.get_doc("Payment Entry", payment_entry_name)
		self.assertEqual(len(payment_entry.references), 2)

		# Verify Journal Entry has correct partial penalty amount
		journal_entry_ref = None
		for ref in payment_entry.references:
			if ref.reference_doctype == "Journal Entry":
				journal_entry_ref = ref
				break

		journal_entry = frappe.get_doc("Journal Entry", journal_entry_ref.reference_name)
		total_debit = sum(entry.debit_in_account_currency for entry in journal_entry.accounts)
		self.assertEqual(total_debit, partial_penalty)

	def test_create_payment_entry_error_handling_invalid_payment_plan(self):
		"""Test error handling with invalid payment plan"""
		with self.assertRaises(frappe.DoesNotExistError):
			create_payment_entry_from_payment_plan(
				payment_plan_name="Non-Existent Payment Plan",
				paid_amount=1000,
				mode_of_payment="Cash",
				submit=False,
			)

	def test_create_payment_entry_error_handling_missing_mode_of_payment(self):
		"""Test error handling with missing mode of payment"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_payment_entry()

		with self.assertRaises(frappe.ValidationError) as context:
			create_payment_entry_from_payment_plan(
				payment_plan_name=test_data["payment_plan"],
				paid_amount=1000,
				mode_of_payment=None,
				submit=False,
			)

		self.assertIn("Payment method is required", str(context.exception))

	def test_create_payment_entry_error_handling_missing_amount(self):
		"""Test error handling with missing payment amount"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_payment_entry()

		with self.assertRaises(frappe.ValidationError) as context:
			create_payment_entry_from_payment_plan(
				payment_plan_name=test_data["payment_plan"],
				paid_amount=None,
				mode_of_payment=test_data["mode_of_payment"],
				submit=False,
			)

		self.assertIn("Payment amount is required", str(context.exception))

	def test_create_payment_entry_workflow_integration(self):
		"""Test that payment entry integrates properly with existing workflow"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_payment_entry()

		# Get payment plan
		payment_plan = frappe.get_doc("Payment Plan", test_data["payment_plan"])

		# Create payment entry for first installment
		installment_amount = payment_plan.installments[0].amount
		payment_entry_name = create_payment_entry_from_payment_plan(
			payment_plan_name=test_data["payment_plan"],
			paid_amount=installment_amount,
			mode_of_payment=test_data["mode_of_payment"],
			submit=True,  # Test submission
		)

		# Verify payment entry was submitted successfully
		payment_entry = frappe.get_doc("Payment Entry", payment_entry_name)
		self.assertEqual(payment_entry.docstatus, 1)  # Submitted

		# Verify payment entry integration with finance payment workflow
		self.assertEqual(payment_entry.custom_is_finance_payment, 1)

		# Verify proper accounting setup
		self.assertGreater(payment_entry.paid_amount, 0)
		self.assertIsNotNone(payment_entry.paid_to)
		self.assertEqual(payment_entry.party_type, "Customer")
		self.assertEqual(payment_entry.party, test_data["customer"])
