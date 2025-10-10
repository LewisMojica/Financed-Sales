# Copyright (c) 2025, Lewis Mojica and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPaymentPlan(FrappeTestCase):
	def test_cancel_with_factura_proforma_as_financed_sales_manager(self):
		"""
		Test if user with 'Financed Sales Manager' role can cancel Payment Plan with Factura.

		This reproduces the production bug where users get permission error.
		"""
		from financed_sales.financed_sales.factories.payment_plan.with_factura import (
			create_payment_plan_with_factura,
		)
		from financed_sales.financed_sales.factories.helpers import (
			_get_or_create_test_user_with_role
		)

		# Create test data
		result = create_payment_plan_with_factura()

		# Get or create test user with only Financed Sales Manager role
		test_user = _get_or_create_test_user_with_role("Financed Sales Manager")

		# Save current user
		original_user = frappe.session.user

		try:
			# Switch to test user
			frappe.set_user(test_user)

			# Try to cancel Payment Plan
			payment_plan = frappe.get_doc("Payment Plan", result['payment_plan'])

			# This should NOT raise PermissionError
			payment_plan.cancel()

			# Verify cancellation succeeded
			payment_plan.reload()
			self.assertEqual(payment_plan.docstatus, 2, "Payment Plan should be cancelled")

			# Verify Factura Proforma was also cancelled
			factura = frappe.get_doc("Factura Proforma", result['factura_proforma'])
			self.assertEqual(factura.docstatus, 2, "Factura Proforma should be cancelled")

		finally:
			# Restore original user
			frappe.set_user(original_user)

	def test_cancel_without_factura_proforma_as_financed_sales_manager(self):
		"""
		Test if user with 'Financed Sales Manager' role can cancel Payment Plan WITHOUT Factura.

		This tests if the issue is specific to Factura Proforma or affects all Payment Plans.
		"""
		from financed_sales.financed_sales.factories.payment_plan.base import (
			create_payment_plan,
		)
		from financed_sales.financed_sales.factories.helpers import (
			_get_or_create_test_user_with_role
		)

		# Create test data WITHOUT Factura Proforma
		result = create_payment_plan()

		# Get or create test user with only Financed Sales Manager role
		test_user = _get_or_create_test_user_with_role("Financed Sales Manager")

		# Save current user
		original_user = frappe.session.user

		try:
			# Switch to test user
			frappe.set_user(test_user)

			# Try to cancel Payment Plan
			payment_plan = frappe.get_doc("Payment Plan", result['payment_plan'])

			# This should show us if the issue is with Factura or with Sales Invoice/Order
			payment_plan.cancel()

			# Verify cancellation succeeded
			payment_plan.reload()
			self.assertEqual(payment_plan.docstatus, 2, "Payment Plan should be cancelled")

		finally:
			# Restore original user
			frappe.set_user(original_user)
