# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CartadeSaldoInstallment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		due_date: DF.Date | None
		paid_amount: DF.Currency
		payment_ref: DF.Data | None
		penalty_amount: DF.Currency
		pending_amount: DF.Currency
	# end: auto-generated types

	pass
