# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class FinanceApplication(Document):
	@frappe.whitelist()
	def create_factura_proforma(self):
		sub_total = 0
		discount = 0
		delivery_fee = 0
		itbis = 0
		grand_total = 0
		credit_total = 0
		quotation = frappe.get_doc('Quotation', self.quotation)
		
		factura = frappe.new_doc('Factura Proforma')
		factura.finance_application = self.name
		factura.customer = self.customer


		for item in quotation.items:
			item_doc = frappe.get_doc("Item", item.item_code)
			sub_total += item.amount
			
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
		interest_item = frappe.get_doc('Item','INTEREST')
		factura.expiration_date = self.credit_expiration_date
		factura.sub_total = sub_total
		factura.total_credit = self.total_amount_to_finance+self.interests 
		factura.expiration_date = self.credit_expiration_date
		#factura.itbis = sub_total*0.18
		factura.insert()
		return factura.name
