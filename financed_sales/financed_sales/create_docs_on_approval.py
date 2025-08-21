import frappe
from frappe import _
from erpnext.selling.doctype.quotation.quotation import make_sales_order


def main(doc,method):
	if doc.workflow_state == 'Approved':
		on_approval(doc)
	elif doc.workflow_state == 'Pending':
		create_sales_invoice(doc)
	
	
	
def create_sales_invoice(doc):
	sales_order_dict = make_sales_order(doc.quotation)

	# The method returns a dictionary, convert to doc and save
	sales_order = frappe.get_doc(sales_order_dict)
	sales_order.delivery_date = doc.first_installment
	sales_order.custom_finance_application = doc.name
	sales_order.insert()
	sales_order.submit()  

def on_approval(doc):
	"""Creates corresponding (credit) Sales Invoice and Payment Plan"""
	inv_name = create_credit_inv(doc)				#Create the credit inv and put the link in the application                              	
	doc.credit_invoice = inv_name						#Note: this does not add the link to the database as the application is already submited)	
																#In the next line the value is acctually inserted in the DB                             	
	frappe.db.set_value(doc.doctype,doc.name,'credit_invoice',inv_name)
	#same pattern:
	plan_name = create_payment_plan(doc)
	doc.payment_plan = plan_name
	frappe.db.set_value(doc.doctype,doc.name,'payment_plan',plan_name)
	
	#add references to credit inv and payment plan:
	frappe.db.set_value('Payment Plan',plan_name,'credit_invoice',inv_name)
	frappe.db.set_value('Sales Invoice',inv_name,'custom_payment_plan',plan_name)
	frappe.db.set_value('Sales Invoice',inv_name,'custom_finance_application',doc.name)
	
	
def create_credit_inv(doc, submit = True):
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
	if submit:
		invoice.submit()
	return invoice.name
def create_payment_plan(doc, submit = True):
	plan = frappe.new_doc('Payment Plan')
	plan.finance_application = doc.name
	plan.customer = doc.customer
	
	for installment in doc.installments:
		plan.append('installments',{
			'due_date': installment.due_date,
			'amount': installment.amount,
			'paid_amount': 0,
			'pending_amount': installment.amount,
		})
	plan.insert()
	if submit:
		plan.submit()
	return plan.name
