import unittest

import frappe

from financed_sales.financed_sales.page.overdue_financed_sales.overdue_financed_sales import get_overdue_data
from financed_sales.financed_sales.factories.payment_plan.cancelled import create_cancelled_overdue_payment_plan


class TestOverdueFinancedSales(unittest.TestCase):
	def test_cancelled_payment_plans_not_shown(self):
		"""Cancelled Payment Plans should not appear in overdue data"""
		# Create a cancelled overdue payment plan
		result = create_cancelled_overdue_payment_plan()

		# Get overdue data
		overdue_data = get_overdue_data(result['company'])

		# Cancelled plan should NOT appear in results
		payment_plan_names = [item['payment_plan'] for item in overdue_data]
		self.assertNotIn(result['payment_plan'], payment_plan_names)
