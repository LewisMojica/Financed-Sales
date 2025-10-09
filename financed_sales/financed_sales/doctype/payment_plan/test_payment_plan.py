# Copyright (c) 2025, Lewis Mojica and Contributors
# See license.txt

import frappe
import json
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


def test_cancel_as_financed_sales_manager():
	"""
	Manual test function for running via bench execute.

	Usage:
	  bench --site dev.localhost execute "financed_sales.financed_sales.doctype.payment_plan.test_payment_plan.test_cancel_as_financed_sales_manager"
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

	# Test cancellation as the restricted user
	test_result = {
		'test_data': result,
		'test_user': test_user,
		'test_results': {}
	}

	# Save current user
	original_user = frappe.session.user

	try:
		# Switch to test user
		frappe.set_user(test_user)

		# Try to cancel Payment Plan
		payment_plan = frappe.get_doc("Payment Plan", result['payment_plan'])

		try:
			payment_plan.cancel()
			payment_plan.reload()
			factura = frappe.get_doc("Factura Proforma", result['factura_proforma'])

			test_result['test_results'] = {
				'status': 'SUCCESS',
				'message': 'Payment Plan cancelled successfully',
				'payment_plan_docstatus': payment_plan.docstatus,
				'factura_docstatus': factura.docstatus
			}
		except frappe.PermissionError as e:
			test_result['test_results'] = {
				'status': 'PERMISSION_ERROR',
				'message': str(e),
				'error_type': 'PermissionError',
				'bug_confirmed': True
			}
		except Exception as e:
			test_result['test_results'] = {
				'status': 'ERROR',
				'message': str(e),
				'error_type': type(e).__name__
			}
	finally:
		# Restore original user
		frappe.set_user(original_user)

	print(json.dumps(test_result, indent=2))
	return test_result
