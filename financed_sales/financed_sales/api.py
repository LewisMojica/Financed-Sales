import json
import frappe
from frappe import _

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
	application = frappe.get_doc({
		'doctype': 'Finance Application',
		'customer': quotation.party_name,
		'quotation': quotation.name,
		'total_amount_to_finance': quotation.grand_total,
		'down_payment': (settings.down_payment_percent or 0)*quotation.grand_total/100,
		'interest_rate': settings.interest_rate,
		'application_fee': settings.application_fee,
		'rate_period': settings.rate_period or 'Monthly',
	}).insert()
		
	print(f'creating application {application.name}')
	return {"name": application.name}

