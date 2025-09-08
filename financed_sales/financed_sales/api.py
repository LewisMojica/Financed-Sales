import json
import frappe
from frappe import _
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from types import SimpleNamespace


@frappe.whitelist()
def create_finance_app_from_pos_cart(customer, items):
	"""
	Create a Sales Quotation and Finance Appication 
	from a POS cart.
	`customer`: string, Customer name or ID
	`items`: list of dicts [{ item_code, qty, rate }, …]
	Returns: { name: <new Finance Application name> }
	"""
	items = json.loads(items)
	# 1. Validation
	if not customer:
		frappe.throw(_("No customer specified"))

	if not items:
		frappe.throw(_("Cart is empty"))

	# 2. Build Quotation items
	quotation_items = []
	for row in items:
		print('row',row)
		quotation_items.append({
			"doctype": "Quotation Item",
			"item_code": row["item_code"],
			"qty":	   row["qty"],
			"rate":    row["rate"]
		})

	# 3. Create and insert the Quotation
	quotation = frappe.get_doc({
		"doctype":		   "Quotation",
		"party_name":		   customer,
		"transaction_date": frappe.utils.today(),
		"valid_till":	   frappe.utils.add_days(frappe.utils.today(), 30),
		"items":		   quotation_items
	}).insert(ignore_permissions=True)
	quotation.submit()
	
	return create_finance_application(quotation.name) 


@frappe.whitelist()
def create_finance_application(quotation_name):
	"""
	Creates a Finance Application from a Quotation.
	`quotation_name`: Quotation name from which the Finance 
	Application will be created.	
	Returns: {'name': <new Finance Application name>'} 
	"""
	settings = frappe.get_single('Financed Sales Settings')
	quotation = frappe.get_doc('Quotation', quotation_name)	
	down_payment = (settings.down_payment_percent or 0)*quotation.grand_total/100
	application = frappe.get_doc({
		'doctype': 'Finance Application',
		'customer': quotation.party_name,
		'quotation': quotation.name,
		'total_amount_to_finance': quotation.grand_total,
		'down_payment_amount':down_payment, 
		'pending_down_payment_amount': down_payment,
		'interest_rate': settings.interest_rate,
		'application_fee': settings.application_fee,
		'rate_period': settings.rate_period or 'Monthly',
	}).insert()
		
	print(f'creating application {application.name}')
	return {"name": application.name}


@frappe.whitelist()
def create_down_payment_from_fin_app(fin_app_name):
	"""
	Creates a payment entry for the down payment amount specified
	in the `fin_app_name` param.
	The created payment entry is linked to the Sales Order or 
	(credit) Sales Invoice (if it already created) referenced in
	param `fin_app_name`.
	`fin_app_name`: Fiance Application from which the Sales Order or
	(credit) Sales invoice will be taken to link in the payment entry
	Returns: <new Payment Entry name>
	"""
	fin_app = frappe.get_doc('Finance Application', fin_app_name)
	pe = get_payment_entry("Sales Order", fin_app.sales_order, party_amount=fin_app.down_payment)	
	pe.custom_is_finance_down_payment = 1
	return pe



@frappe.whitelist()
def create_payment_entry_from_payment_plan(payment_plan_name, paid_amount, mode_of_payment, submit = False, reference_number = None, reference_date = None):
	paid_amount = float(paid_amount)
	si_name = frappe.db.get_value('Payment Plan', payment_plan_name, 'credit_invoice')
	si = SimpleNamespace(doctype='Sales Invoice', name=si_name)
	return create_payment_entry(si, paid_amount, mode_of_payment, submit, reference_number, reference_date)	

@frappe.whitelist()
def create_payment_entry_from_finance_application(finance_application_name, paid_amount, mode_of_payment, submit = False, reference_number = None, reference_date = None):
	paid_amount = float(paid_amount)
	so_name = frappe.db.get_value('Finance Application', finance_application_name, 'sales_order')
	so = SimpleNamespace(doctype='Sales Order', name=so_name)
	return create_payment_entry(so, paid_amount, mode_of_payment, submit, reference_number, reference_date)	


def create_payment_entry(doc, paid_amount, mode_of_payment, submit = False, reference_number = None, reference_date = None):
	pe = get_payment_entry(doc.doctype, doc.name, party_amount = paid_amount)
	pe.mode_of_payment = mode_of_payment
	
	mode_of_payment_doc = frappe.get_doc('Mode of Payment', mode_of_payment)
	if not mode_of_payment_doc.accounts:
		frappe.throw(f"No accounts configured for Mode of Payment '{mode_of_payment}'. Please configure at least one account.")
	
	account = mode_of_payment_doc.accounts[0].default_account
	if not account:
		frappe.throw(f"Default account not set for Mode of Payment '{mode_of_payment}'. Please configure the default account.")
	
	pe.paid_to = account
	pe.custom_is_finance_payment = 1
	
	# Set reference number and date for Wire Transfer and Credit Card
	if mode_of_payment in ["Wire Transfer", "Credit Card"] and reference_number:
		pe.reference_no = reference_number
	if mode_of_payment in ["Wire Transfer", "Credit Card"] and reference_date:
		pe.reference_date = reference_date
	
	pe.save()
	if submit:
		pe.submit()
	return pe.name

