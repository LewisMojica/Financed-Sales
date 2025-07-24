import frappe
from frappe import _

def main(doc,method):
	if doc.workflow_state == 'Approved':
		invoice = frappe.new_doc('Sales Invoice')
		interest_item = frappe.get_doc('Item', 'INTEREST')
		
		quotation = frappe.get_doc('Quotation',doc.quotation)
		for item in quotation.items:
			invoice.append('items',{
				'item_code': item.item_code,
				'qty': item.qty,
			})
		invoice.append('items',{
					'item_code': 'INTEREST',
					'item_name': _('Interest'),
					'qty': 1,
					'rate': doc.interests, 
					'uom': interest_item.stock_uom,
					'conversion_factor': 1,
					
				})

		invoice.custom_is_credit_invoice = True
		invoice.due_date = doc.installments[-1].due_date
		invoice.customer = quotation.party_name
		invoice.company = quotation.company
		invoice.currency = quotation.currency
		invoice.conversion_rate = quotation.conversion_rate
		invoice.selling_price_list = quotation.selling_price_list
		invoice.price_list_currency = quotation.price_list_currency
		invoice.plc_conversion_rate = quotation.plc_conversion_rate
		

	invoice.insert()
