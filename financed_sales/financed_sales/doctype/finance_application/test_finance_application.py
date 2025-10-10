# Copyright (c) 2025, Lewis Mojica and Contributors
# See license.txt

import unittest

import frappe

from financed_sales.financed_sales.api import create_payment_entry_from_finance_application
from financed_sales.financed_sales.factories.finance_application import create_finance_application


class TestFinanceApplication(unittest.TestCase):
	def test_create_payment_entry_from_finance_application(self):
		"""
		Test creating a payment entry from a submitted Finance Application.

		This reproduces the bug when a user clicks the 'Pay down payment' button
		on a Finance Application.
		"""
		# Step 1: Create a submitted Finance Application using factory
		test_data = create_finance_application()
		finance_app = frappe.get_doc('Finance Application', test_data['finance_application'])

		# Step 2: Verify Finance Application is submitted and has necessary fields
		self.assertEqual(finance_app.docstatus, 1, "Finance Application should be submitted")
		self.assertIsNotNone(finance_app.sales_order, "Finance Application should have a Sales Order")
		self.assertGreater(finance_app.down_payment_amount, 0, "Should have down payment amount")

		# Step 3: Create payment entry (simulates clicking 'Pay down payment' button)
		payment_entry_name = create_payment_entry_from_finance_application(
			finance_application_name=finance_app.name,
			paid_amount=finance_app.down_payment_amount,
			mode_of_payment='Cash',
			submit=True  # UI submits the payment entry automatically
		)

		# Step 4: Verify payment entry was created successfully
		self.assertIsNotNone(payment_entry_name, "Payment entry should be created")
		self.assertTrue(frappe.db.exists('Payment Entry', payment_entry_name),
			"Payment entry should exist in database")

		# Step 5: Verify payment entry details
		payment_entry = frappe.get_doc('Payment Entry', payment_entry_name)
		self.assertEqual(payment_entry.docstatus, 1,
			"Payment entry should be submitted")
		self.assertEqual(payment_entry.paid_amount, finance_app.down_payment_amount,
			"Payment amount should match down payment amount")
		self.assertEqual(payment_entry.party, finance_app.customer,
			"Payment should be for the correct customer")
		self.assertEqual(payment_entry.mode_of_payment, 'Cash',
			"Payment mode should be Cash")
