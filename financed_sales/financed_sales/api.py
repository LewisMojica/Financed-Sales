import json
import frappe
from frappe import _

@frappe.whitelist()
def create_pos_quotation(customer, items):
	"""
	Create a Sales Quotation from a POS cart.
	`customer`: string, Customer name or ID
	`items`: list of dicts [{ item_code, qty, rate }, …]
	Returns: { name: <new Quotation name> }
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
	application = frappe.get_doc({
		'doctype': 'Finance Application',
		'customer': customer,
		'quotation': quotation.name,
		'total_amount_to_finance': quotation.grand_total,
	}).insert()
		
	return {"name": application.name}

