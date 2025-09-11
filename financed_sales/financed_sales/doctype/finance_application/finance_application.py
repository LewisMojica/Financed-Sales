# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from financed_sales.financed_sales.utils import distribute_interest_to_items


class FinanceApplication(Document):
	def validate(self):
		if len(self.installments) <= 0 and self.docstatus == 1:
			frappe.throw(_('Not enough data to compute installments'))
	
	def before_cancel(self):
		"""Handle cleanup when rejecting a pending Finance Application"""
		print(f"before_cancel called for {self.name}, state: {self.workflow_state}")
		
		# Handle rejections (workflow_state is already 'Rejected' when before_cancel is called)
		if self.workflow_state == 'Rejected' and self.sales_order:
			print(f"Attempting to cancel Sales Order: {self.sales_order}")
			try:
				sales_order = frappe.get_doc('Sales Order', self.sales_order)
				print(f"Sales Order status before cancel: {sales_order.docstatus}")
				
				if sales_order.docstatus == 1:  # Only cancel if submitted
					# First try to remove all link references
					frappe.db.set_value('Sales Order', self.sales_order, 'custom_finance_application', None)
					frappe.db.commit()
					
					# Cancel with ignore_links to bypass link checking
					sales_order.reload()
					sales_order.flags.ignore_links = True
					sales_order.cancel()
					print(f"Successfully cancelled Sales Order {self.sales_order}")
				else:
					print(f"Sales Order {self.sales_order} not submitted, status: {sales_order.docstatus}")
			except Exception as e:
				print(f"Error canceling Sales Order {self.sales_order}: {str(e)}")
				import traceback
				traceback.print_exc()
		
		# Also cancel any draft Factura Proforma documents linked to this Finance Application
		factura_list = frappe.get_all('Factura Proforma', 
			filters={'finance_application': self.name, 'docstatus': 0})
		for factura in factura_list:
			try:
				frappe.delete_doc('Factura Proforma', factura.name)
				print(f"Deleted draft Factura Proforma {factura.name}")
			except Exception as e:
				print(f"Error deleting Factura Proforma {factura.name}: {str(e)}")
	
	def on_cancel(self):
		"""Update workflow state when document is cancelled"""
		# Set workflow state to Rejected when cancelled from Pending state
		if self.workflow_state == 'Pending':
			frappe.db.set_value(self.doctype, self.name, 'workflow_state', 'Rejected')
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


		financed_items = distribute_interest_to_items(quotation.items, self.interests)
		
		for item in financed_items:
			item_doc = frappe.get_doc("Item", item['item_code'])
			sub_total += item['amount']
			
			factura.append('items', {
				'item_code': item['item_code'],
				'item_name': item['item_name'] or item_doc.item_name,
				'qty': item['qty'],
				'uom': item['uom'] or item_doc.stock_uom,
				'conversion_factor': 1,
				'rate': item['rate'],
				'amount': item['amount'],
				'base_rate': item['base_rate'],
				'base_amount': item['base_amount']
			})			
		factura.interests = self.interests
		factura.expiration_date = self.credit_expiration_date
		factura.sub_total = sub_total
		factura.total_credit = self.total_amount_to_finance+self.interests 
		factura.expiration_date = self.credit_expiration_date
		#factura.itbis = sub_total*0.18
		factura.insert()
		return factura.name
