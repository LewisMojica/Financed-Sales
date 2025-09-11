import frappe
from frappe import _
from erpnext.selling.doctype.quotation.quotation import make_sales_order
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from financed_sales.financed_sales.utils import distribute_interest_to_items 

def main(doc,method):
	if doc.workflow_state == 'Approved' and not doc.credit_invoice:
		on_approval(doc)
	elif doc.workflow_state == 'Pending' and not doc.sales_order:
		create_sales_order(doc)
	
	
	
def create_sales_order(doc):
	sales_order_dict = make_sales_order(doc.quotation, ignore_permissions=True)
	settings = frappe.get_single('Financed Sales Settings')

	# The method returns a dictionary, convert to doc and save
	sales_order = frappe.get_doc(sales_order_dict)
	sales_order.delivery_date = doc.first_installment
	sales_order.custom_finance_application = doc.name
	sales_order.payment_schedule[0].due_date = doc.installments[-1].due_date
	sales_order.append('taxes', {
	'charge_type': 'Actual',
	'account_head': settings.interests_account,
	'description': 'Intereses',
	'tax_amount': doc.interests,
	})
	
	quotation = frappe.get_doc('Quotation', doc.quotation)
	financed_items = distribute_interest_to_items(quotation.items, doc.interests)
	
	for item in financed_items:
		sales_order.append('custom_financed_items', {
			'item_code': item['item_code'],
			'item_name': item['item_name'],
			'qty': item['qty'],
			'uom': item['uom'],
			'conversion_factor': item['conversion_factor'],
			'rate': item['rate'],
			'amount': item['amount']
		})
	
	sales_order.insert(ignore_permissions=True)
	sales_order.submit()
	doc.sales_order = sales_order.name
	frappe.db.set_value(doc.doctype, doc.name, 'sales_order', sales_order.name)

def on_approval(doc):
	"""Creates corresponding (credit) Sales Invoice and Payment Plan"""
	inv_name = create_credit_inv(doc)				#Create the credit inv and put the link in the application                              	
	doc.credit_invoice = inv_name						#Note: this does not add the link to the database as the application is already submited)	
																#In the next line the value is acctually inserted in the DB                             	
	frappe.db.set_value(doc.doctype,doc.name,'credit_invoice',inv_name)
	#same pattern:
	plan_name = create_payment_plan(doc, inv_name)
	doc.payment_plan = plan_name
	frappe.db.set_value(doc.doctype,doc.name,'payment_plan',plan_name)
	
	#add references to credit inv and payment plan:
	frappe.db.set_value('Sales Invoice',inv_name,'custom_payment_plan',plan_name)
	frappe.db.set_value('Sales Invoice',inv_name,'custom_finance_application',doc.name)
	
	
def create_credit_inv(doc, submit = True):
	settings = frappe.get_single('Financed Sales Settings')
	account = settings.interests_account #account for interest
	invoice = make_sales_invoice(doc.sales_order, ignore_permissions=True)
	quotation = frappe.get_doc('Quotation', doc.quotation)

	invoice.custom_is_credit_invoice = True
	invoice.custom_factura_de_valor_fiscal = False
	invoice.due_date = doc.installments[-1].due_date
	invoice.allocate_advances_automatically = 1
	invoice.only_include_allocated_payments = 1

	# Calculate financed total from existing financed items
	financed_total = 0
	if invoice.custom_financed_items:
		for item in invoice.custom_financed_items:
			if item.amount:
				financed_total += item.amount
	
	# Set the financed total
	invoice.custom_financed_total = financed_total

	invoice.insert(ignore_permissions=True)
	if submit:
		invoice.submit()
	return invoice.name

def create_payment_plan(doc, credit_invoice_name, submit = True):
	plan = frappe.new_doc('Payment Plan')
	plan.finance_application = doc.name
	plan.customer = doc.customer
	plan.credit_invoice = credit_invoice_name
	plan.down_payment_amount = doc.down_payment_amount
	plan.paid_down_payment_amount = doc.paid_down_payment_amount
	plan.pending_down_payment_amount = doc.pending_down_payment_amount
	
	for installment in doc.installments:
		plan.append('installments',{
			'due_date': installment.due_date,
			'amount': installment.amount,
			'paid_amount': 0,
			'pending_amount': installment.amount,
		})

	#copy payments made against Finance Application:
	for payment in doc.payment_refs:
		plan.append('payment_refs',payment.as_dict())
		
		

	plan.insert(ignore_permissions=True)
	if submit:
		plan.submit()
	return plan.name
