import frappe
from frappe import _

def main(doc,method):
	if doc.workflow_state == 'Approved':
		settings = frappe.get_single('Financed Sales Settings')
		invoice = frappe.new_doc('Sales Invoice')
		quotation = frappe.get_doc('Quotation',doc.quotation)

		for item in quotation.items:
			invoice.append('items',{
				'item_code': item.item_code,
				'qty': item.qty,
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
		account = settings.interests_account #account for interest
		for tax in quotation.taxes:
			invoice.append('taxes',tax)
		invoice.append('taxes', {
			'charge_type': 'Actual',
			'account_head': account,
			'description': 'Intereses',
			'tax_amount': doc.interests,
		})
		

	invoice.insert()
