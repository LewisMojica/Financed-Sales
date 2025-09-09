# Copyright (c) 2024, Lewis Mojica and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_overdue_data(company):
	"""Get overdue payment plan data for the specified company."""
	if not company:
		frappe.throw(_("Please select a company"))

	# TODO: Implement actual overdue payment plan query
	# For now, return empty data to test the page structure
	return []