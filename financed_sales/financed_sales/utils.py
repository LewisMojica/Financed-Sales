"""Utility functions for financed sales interest calculations and item distribution."""

import frappe
from decimal import Decimal, ROUND_HALF_EVEN


def distribute_interest_to_items(original_items, total_interest):
	"""Distribute interest proportionally across items using banker's rounding.
	
	Args:
		original_items: List of item objects with amount, rate, qty, item_code, etc.
		total_interest (float): Total interest amount to distribute across items.
	
	Returns:
		list: List of dicts compatible with Quotation Item structure containing
			financed rates and amounts with interest included.
	
	Raises:
		frappe.ValidationError: If no items provided or total base amount is zero.
	"""
	if not original_items:
		frappe.throw("No items found to distribute interest")
	
	if total_interest <= 0:
		return []
	
	total_base_amount = sum(Decimal(str(item.amount)) for item in original_items)
	
	if total_base_amount <= 0:
		frappe.throw("Total base amount must be greater than zero")
	
	financed_items = []
	total_interest_decimal = Decimal(str(total_interest))
	distributed_interest = Decimal('0')
	
	for i, item in enumerate(original_items):
		item_amount = Decimal(str(item.amount))
		
		if i == len(original_items) - 1:
			interest_portion = total_interest_decimal - distributed_interest
		else:
			interest_portion = (item_amount / total_base_amount) * total_interest_decimal
			interest_portion = interest_portion.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
			distributed_interest += interest_portion
		
		interest_per_unit = interest_portion / Decimal(str(item.qty))
		financed_rate = Decimal(str(item.rate)) + interest_per_unit
		financed_amount = financed_rate * Decimal(str(item.qty))
		
		financed_items.append({
			'item_code': item.item_code,
			'item_name': item.item_name,
			'qty': item.qty,
			'uom': item.uom,
			'rate': float(financed_rate),
			'amount': float(financed_amount),
			'base_rate': float(financed_rate),
			'base_amount': float(financed_amount)
		})
	
	return financed_items
