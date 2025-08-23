import frappe
from frappe import _
from erpnext.selling.doctype.quotation.quotation import make_sales_order
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice 

def main(doc,method):
	if doc.workflow_state == 'Approved' and not doc.credit_invoice:
		on_approval(doc)
	elif doc.workflow_state == 'Pending' and not doc.sales_order:
		create_sales_order(doc)
	
	
	
def create_sales_order(doc):
	sales_order_dict = make_sales_order(doc.quotation)
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
	
	sales_order.insert()
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
	plan_name = create_payment_plan(doc)
	doc.payment_plan = plan_name
	frappe.db.set_value(doc.doctype,doc.name,'payment_plan',plan_name)
	
	#add references to credit inv and payment plan:
	frappe.db.set_value('Payment Plan',plan_name,'credit_invoice',inv_name)
	frappe.db.set_value('Sales Invoice',inv_name,'custom_payment_plan',plan_name)
	frappe.db.set_value('Sales Invoice',inv_name,'custom_finance_application',doc.name)
	
	
def create_credit_inv(doc, submit = True):
	settings = frappe.get_single('Financed Sales Settings')
	account = settings.interests_account #account for interest
	invoice = make_sales_invoice(doc.sales_order)
	quotation = frappe.get_doc('Quotation',doc.quotation)

	invoice.custom_is_credit_invoice = True
	invoice.due_date = doc.installments[-1].due_date
	invoice.allocate_advances_automatically = 1
	invoice.only_include_allocated_payments = 1

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
		
		

	plan.insert()
	if submit:
		plan.submit()
	return plan.name
