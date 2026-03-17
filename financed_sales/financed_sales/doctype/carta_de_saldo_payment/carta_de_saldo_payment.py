# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CartadeSaldoPayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		date: DF.Date | None
		payment_entry: DF.Data | None
	# end: auto-generated types

	pass
