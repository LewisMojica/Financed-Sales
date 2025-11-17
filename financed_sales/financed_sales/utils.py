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
			'conversion_factor': item.conversion_factor or 1,
			'rate': float(financed_rate),
			'amount': float(financed_amount),
			'base_rate': float(financed_rate),
			'base_amount': float(financed_amount)
		})
	
	return financed_items


def validate_financed_items_total(financed_items, original_total, interest_amount):
	"""Validate that financed items total equals original total plus interest.
	
	Args:
		financed_items (list): List of financed item dictionaries.
		original_total (float): Original items total before interest.
		interest_amount (float): Total interest amount distributed.
	
	Raises:
		frappe.ValidationError: If totals don't match within tolerance.
	"""
	if not financed_items:
		frappe.throw("Financed items table is empty")
	
	financed_total = sum(Decimal(str(item['amount'])) for item in financed_items)
	expected_total = Decimal(str(original_total)) + Decimal(str(interest_amount))
	tolerance = Decimal('0.01')
	
	if abs(financed_total - expected_total) > tolerance:
		frappe.throw(f"Financed items total ({financed_total}) does not match expected total ({expected_total})")


def validate_financed_sales_document(doc):
	"""Validate financed sales document has required financed items table.

	Args:
		doc: Document object (Sales Order or Sales Invoice) to validate.

	Raises:
		frappe.ValidationError: If financed items missing for financed sales.
	"""
	if hasattr(doc, 'custom_finance_application') and doc.custom_finance_application:
		if not hasattr(doc, 'custom_financed_items') or not doc.custom_financed_items:
			frappe.throw(f"Financed items table is required for financed sales document {doc.name}")
