import unittest

import frappe

from .factories.penalty_journal_factory import create_test_payment_plan_for_penalty_journal
from .penalty_journal import create_penalty_journal_entry


class TestPenaltyJournal(unittest.TestCase):
	def test_create_penalty_journal_entry_success(self):
		"""Test successful penalty journal entry creation"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_penalty_journal()

		# Test penalty journal entry creation
		penalty_amount = 1000
		result = create_penalty_journal_entry(
			penalty_amount=penalty_amount,
			customer=test_data["customer"],
			payment_plan_name=test_data["payment_plan"],
		)

		# Verify result is a journal entry name
		self.assertIsInstance(result, str)
		self.assertTrue(frappe.db.exists("Journal Entry", result))

		# Verify journal entry details
		journal_entry = frappe.get_doc("Journal Entry", result)
		self.assertEqual(journal_entry.docstatus, 1)  # Submitted
		self.assertEqual(journal_entry.voucher_type, "Journal Entry")
		self.assertEqual(journal_entry.company, test_data["company"])

		# Verify proper accounting entries (should have exactly 2 entries: debit and credit)
		self.assertEqual(len(journal_entry.accounts), 2)

		# Find debit and credit entries
		debit_entry = None
		credit_entry = None
		for account_entry in journal_entry.accounts:
			if account_entry.debit_in_account_currency > 0:
				debit_entry = account_entry
			elif account_entry.credit_in_account_currency > 0:
				credit_entry = account_entry

		# Verify debit entry (customer receivable)
		self.assertIsNotNone(debit_entry, "Debit entry should exist")
		self.assertEqual(debit_entry.party_type, "Customer")
		self.assertEqual(debit_entry.party, test_data["customer"])
		self.assertEqual(debit_entry.debit_in_account_currency, penalty_amount)
		self.assertIn(test_data["payment_plan"], debit_entry.user_remark)

		# Verify credit entry (penalty income account)
		self.assertIsNotNone(credit_entry, "Credit entry should exist")
		self.assertEqual(credit_entry.credit_in_account_currency, penalty_amount)
		self.assertIn(test_data["payment_plan"], credit_entry.user_remark)

		# Verify accounting balance
		total_debit = sum(entry.debit_in_account_currency for entry in journal_entry.accounts)
		total_credit = sum(entry.credit_in_account_currency for entry in journal_entry.accounts)
		self.assertEqual(total_debit, total_credit)
		self.assertEqual(total_debit, penalty_amount)

	def test_create_penalty_journal_entry_missing_penalty_account(self):
		"""Test error handling when penalty account is not configured"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_penalty_journal()

		# Clear penalty account configuration
		settings = frappe.get_single("Financed Sales Settings")
		original_penalty_account = settings.penalty_income_account
		settings.penalty_income_account = ""
		settings.save()

		try:
			# Test should raise validation error
			with self.assertRaises(frappe.ValidationError) as context:
				create_penalty_journal_entry(
					penalty_amount=500,
					customer=test_data["customer"],
					payment_plan_name=test_data["payment_plan"],
				)

			self.assertIn("Penalty Income Account is not configured", str(context.exception))

		finally:
			# Restore original configuration
			settings.penalty_income_account = original_penalty_account
			settings.save()

	def test_create_penalty_journal_entry_invalid_customer(self):
		"""Test error handling with invalid customer"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_penalty_journal()

		# Test with non-existent customer should raise error
		with self.assertRaises(Exception):
			create_penalty_journal_entry(
				penalty_amount=500,
				customer="Non-Existent Customer",
				payment_plan_name=test_data["payment_plan"],
			)

	def test_create_penalty_journal_entry_invalid_payment_plan(self):
		"""Test error handling with invalid payment plan"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_penalty_journal()

		# Test with non-existent payment plan should raise error
		with self.assertRaises(frappe.DoesNotExistError):
			create_penalty_journal_entry(
				penalty_amount=500,
				customer=test_data["customer"],
				payment_plan_name="Non-Existent Payment Plan",
			)

	def test_create_penalty_journal_entry_multiple_amounts(self):
		"""Test penalty journal entry creation with different amounts"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_penalty_journal()

		# Test different penalty amounts
		test_amounts = [100, 500.50, 1250.75]

		for penalty_amount in test_amounts:
			result = create_penalty_journal_entry(
				penalty_amount=penalty_amount,
				customer=test_data["customer"],
				payment_plan_name=test_data["payment_plan"],
			)

			# Verify journal entry was created with correct amount
			journal_entry = frappe.get_doc("Journal Entry", result)
			total_debit = sum(entry.debit_in_account_currency for entry in journal_entry.accounts)
			self.assertEqual(total_debit, penalty_amount)

	def test_create_penalty_journal_entry_workflow_integration(self):
		"""Test that penalty journal entry integrates properly with workflow"""
		# Use provided factory to create test data
		test_data = create_test_payment_plan_for_penalty_journal()

		penalty_amount = 750
		journal_entry_name = create_penalty_journal_entry(
			penalty_amount=penalty_amount,
			customer=test_data["customer"],
			payment_plan_name=test_data["payment_plan"],
		)

		# Verify journal entry is available for payment allocation
		journal_entry = frappe.get_doc("Journal Entry", journal_entry_name)
		self.assertEqual(journal_entry.docstatus, 1)  # Must be submitted

		# Verify remark includes payment plan reference
		self.assertIn(test_data["payment_plan"], journal_entry.remark)
		self.assertIn(test_data["customer"], journal_entry.remark)

		# Verify all required fields are populated for payment referencing
		for account_entry in journal_entry.accounts:
			self.assertIn(test_data["payment_plan"], account_entry.user_remark)
