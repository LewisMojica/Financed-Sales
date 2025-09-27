# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

from copy import deepcopy

import frappe

from financed_sales.financed_sales.update_payments import auto_alloc_payments, from_cents, to_cents


def analyze_payment_allocation(payment_plan_doc, total_payment_amount):
	"""
	Analyze payment allocation to determine penalty vs principal breakdown.

	Uses existing auto_alloc_payments logic to simulate payment allocation without modifying it.
	Analyzes allocation results to determine how much goes to principal vs penalty for each installment.

	Args:
	    payment_plan_doc: Payment Plan document
	    total_payment_amount (float): Total payment amount to allocate

	Returns:
	    dict: {
	        'principal_amount': float,  # Amount allocated to principal
	        'penalty_amount': float,    # Amount allocated to penalty
	        'breakdown': [              # Detailed breakdown per installment
	            {
	                'installment_index': int,
	                'principal_payment': float,
	                'penalty_payment': float,
	                'installment_amount': float,
	                'penalty_amount': float
	            }
	        ]
	    }
	"""

	# Create a simulated payment object for analysis
	class SimulatedPayment:
		def __init__(self, payment_entry, amount, date):
			self.payment_entry = payment_entry
			self.amount = amount
			self.date = date

	simulated_payment = SimulatedPayment("SIMULATION", total_payment_amount, frappe.utils.today())

	# Create a copy of existing payments and add the simulated payment
	existing_payments = list(payment_plan_doc.payment_refs) if payment_plan_doc.payment_refs else []
	simulated_payments_table = [*existing_payments, simulated_payment]

	# Run allocation simulation
	allocation_result = auto_alloc_payments(
		payment_plan_doc.down_payment_amount, payment_plan_doc.installments, simulated_payments_table
	)

	# Extract only the new payment allocation (simulation payment)
	total_principal_amount = 0
	total_penalty_amount = 0
	breakdown = []

	# Check all allocations including down payment
	for allocation_index, allocated_item in enumerate(allocation_result):
		# Find simulation payment allocation in this item
		simulation_allocation = 0
		for payment_ref in allocated_item["payment_refs"]:
			if payment_ref["payment_entry"] == "SIMULATION":
				simulation_allocation = from_cents(payment_ref["amount"])
				break

		if simulation_allocation > 0:
			if allocation_index == 0:
				# This is down payment allocation - we skip it for installment analysis
				continue
			else:
				# This is an installment allocation
				installment_index = allocation_index - 1  # Adjust for down payment
				installment = payment_plan_doc.installments[installment_index]

				# Calculate principal vs penalty split
				installment_principal = installment.amount
				installment_penalty = getattr(installment, "penalty_amount", 0) or 0

				# Calculate cumulative principal already paid to this installment (excluding simulation)
				cumulative_principal_paid = 0
				for payment_ref in allocated_item["payment_refs"]:
					if payment_ref["payment_entry"] != "SIMULATION":
						# This is an existing payment - add its amount to cumulative principal
						existing_allocation = from_cents(payment_ref["amount"])
						cumulative_principal_paid += min(
							existing_allocation, installment_principal - cumulative_principal_paid
						)

				# Calculate remaining principal needed for this installment
				remaining_principal_needed = max(0, installment_principal - cumulative_principal_paid)

				# Allocate simulation payment: principal first, then penalty
				principal_payment = min(simulation_allocation, remaining_principal_needed)
				penalty_payment = max(0, simulation_allocation - principal_payment)

				# Ensure penalty payment doesn't exceed available penalty
				penalty_payment = min(penalty_payment, installment_penalty)

				total_principal_amount += principal_payment
				total_penalty_amount += penalty_payment

				breakdown.append(
					{
						"installment_index": installment_index,
						"principal_payment": principal_payment,
						"penalty_payment": penalty_payment,
						"installment_amount": installment_principal,
						"penalty_amount": installment_penalty,
					}
				)

	return {
		"principal_amount": total_principal_amount,
		"penalty_amount": total_penalty_amount,
		"breakdown": breakdown,
	}
