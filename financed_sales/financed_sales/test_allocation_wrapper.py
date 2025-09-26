import unittest

import frappe

from .allocation_wrapper import analyze_payment_allocation


class TestAllocationWrapper(unittest.TestCase):
	def _create_mock_payment_plan(self, installments_data=None):
		"""Create a mock payment plan for testing"""

		class MockInstallment:
			def __init__(self, amount, penalty_amount=0):
				self.amount = amount
				self.penalty_amount = penalty_amount

		class MockPaymentPlan:
			def __init__(self, down_payment_amount, installments_data, payment_refs=None):
				self.down_payment_amount = down_payment_amount
				self.installments = [
					MockInstallment(inst["amount"], inst.get("penalty_amount", 0))
					for inst in installments_data
				]
				self.payment_refs = payment_refs or []

		if installments_data is None:
			installments_data = [{"amount": 1000}, {"amount": 1000}, {"amount": 1000}]

		return MockPaymentPlan(2000, installments_data)

	def test_analyze_payment_allocation_principal_only(self):
		"""Test payment allocation when payment covers only principal amount"""
		# Create mock payment plan with zero down payment for easier testing
		payment_plan = self._create_mock_payment_plan([{"amount": 1000}, {"amount": 1000}])
		payment_plan.down_payment_amount = 0  # Set down payment to 0 for simplicity

		# Test payment that covers only one installment's principal (no penalty)
		result = analyze_payment_allocation(payment_plan, 1000)

		# Verify result structure
		self.assertIsInstance(result, dict)
		self.assertIn("principal_amount", result)
		self.assertIn("penalty_amount", result)
		self.assertIn("breakdown", result)

		# Verify principal amount allocation
		self.assertEqual(result["principal_amount"], 1000)
		self.assertEqual(result["penalty_amount"], 0)

		# Verify breakdown
		self.assertEqual(len(result["breakdown"]), 1)
		breakdown_item = result["breakdown"][0]
		self.assertEqual(breakdown_item["installment_index"], 0)
		self.assertEqual(breakdown_item["principal_payment"], 1000)
		self.assertEqual(breakdown_item["penalty_payment"], 0)

	def test_analyze_payment_allocation_with_penalties(self):
		"""Test payment allocation when payment covers principal plus penalty"""
		# Create mock payment plan with penalties
		payment_plan = self._create_mock_payment_plan(
			[{"amount": 1000, "penalty_amount": 200}, {"amount": 1000}]
		)
		payment_plan.down_payment_amount = 0  # Set down payment to 0 for simplicity

		# Test payment that covers principal + penalty
		total_payment = 1200  # 1000 principal + 200 penalty
		result = analyze_payment_allocation(payment_plan, total_payment)

		# Verify penalty allocation
		self.assertGreater(result["penalty_amount"], 0)
		self.assertEqual(result["principal_amount"], 1000)
		self.assertEqual(result["penalty_amount"], 200)

		# Verify breakdown includes penalty payment
		breakdown_item = result["breakdown"][0]
		self.assertEqual(breakdown_item["principal_payment"], 1000)
		self.assertEqual(breakdown_item["penalty_payment"], 200)

	def test_analyze_payment_allocation_multi_installment(self):
		"""Test payment allocation across multiple installments"""
		# Create mock payment plan with multiple installments
		payment_plan = self._create_mock_payment_plan(
			[{"amount": 1000, "penalty_amount": 100}, {"amount": 1000, "penalty_amount": 50}]
		)
		payment_plan.down_payment_amount = 0  # Set down payment to 0 for simplicity

		# Calculate payment that covers multiple installments
		multi_payment = 2150  # 1000+100 + 1000+50

		result = analyze_payment_allocation(payment_plan, multi_payment)

		# Verify payment spans multiple installments
		self.assertGreaterEqual(len(result["breakdown"]), 2)

		# Verify total amounts
		total_principal = sum(item["principal_payment"] for item in result["breakdown"])
		total_penalty = sum(item["penalty_payment"] for item in result["breakdown"])

		self.assertEqual(result["principal_amount"], total_principal)
		self.assertEqual(result["penalty_amount"], total_penalty)

	def test_analyze_payment_allocation_partial_penalty(self):
		"""Test payment allocation when payment partially covers penalty"""
		# Create mock payment plan with penalties
		payment_plan = self._create_mock_payment_plan([{"amount": 1000, "penalty_amount": 200}])
		payment_plan.down_payment_amount = 0  # Set down payment to 0 for simplicity

		# Test payment that covers principal + partial penalty
		partial_penalty = 100  # Half of the 200 penalty
		total_payment = 1100  # 1000 principal + 100 partial penalty
		result = analyze_payment_allocation(payment_plan, total_payment)

		# Verify partial penalty allocation
		self.assertEqual(result["principal_amount"], 1000)
		self.assertEqual(result["penalty_amount"], partial_penalty)

		# Verify breakdown
		breakdown_item = result["breakdown"][0]
		self.assertEqual(breakdown_item["principal_payment"], 1000)
		self.assertEqual(breakdown_item["penalty_payment"], partial_penalty)

	def test_analyze_payment_allocation_no_payment(self):
		"""Test payment allocation with zero payment amount"""
		# Create mock payment plan
		payment_plan = self._create_mock_payment_plan([{"amount": 1000}])
		payment_plan.down_payment_amount = 0  # Set down payment to 0 for simplicity

		result = analyze_payment_allocation(payment_plan, 0)

		# Verify zero allocation
		self.assertEqual(result["principal_amount"], 0)
		self.assertEqual(result["penalty_amount"], 0)
		self.assertEqual(len(result["breakdown"]), 0)

	def test_analyze_payment_allocation_excessive_payment(self):
		"""Test payment allocation when payment exceeds available penalty limits"""
		# Create mock payment plan with penalties
		payment_plan = self._create_mock_payment_plan([{"amount": 1000, "penalty_amount": 200}])
		payment_plan.down_payment_amount = 0  # Set down payment to 0 for simplicity

		# Test payment that exceeds principal + penalty
		excessive_payment = 2000  # 1000 principal + 200 penalty + 800 excess
		result = analyze_payment_allocation(payment_plan, excessive_payment)

		# Verify penalty is capped at available penalty amount
		breakdown_item = result["breakdown"][0]
		self.assertLessEqual(breakdown_item["penalty_payment"], 200)
