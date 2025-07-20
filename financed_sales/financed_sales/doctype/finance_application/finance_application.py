# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FinanceApplication(Document):
	@frappe.whitelist()
	def create_factura_proforma(self):
		quotation = frappe.get_doc('Quotation', self.quotation)
		
		factura = frappe.new_doc('Factura Proforma')
		factura.finance_application = self.name
		factura.customer = self.customer


		for item in quotation.items:
			item_doc = frappe.get_doc("Item", item.item_code)
			
			factura.append('items', {
				'item_code': item.item_code,
				'item_name': item.item_name or item_doc.item_name,
				'qty': item.qty,
				'uom': item.uom or item_doc.stock_uom,
				'conversion_factor': item.conversion_factor or 1,
				'rate': item.rate,
				'amount': item.amount,
				'base_rate': item.base_rate,
				'base_amount': item.base_amount
			})			

		factura.insert()
		return factura.name
