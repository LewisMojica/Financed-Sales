import frappe
def main(pe, method):
	if not pe.custom_is_finance_payment:
		return	
	
	# Validation: Block submission if number of references is not exactly 1
	if len(pe.references) != 1:
		frappe.throw('Number of refereces must be equal to 1')
	if pe.unallocated_amount != 0.00:
		frappe.throw(f'Unallocated amount must be 0.00 and is {pe.unallocated_amount}')

	ref = pe.references[0]	
	fa_name = frappe.get_value(ref.reference_doctype, ref.reference_name, 'custom_finance_application') 
	if not fa_name:
		frappe.throw('Finance Application reference not found')	

	fa = frappe.get_doc('Finance Application', fa_name)
	
	valid_state_and_ref_combinations = (
		('Approved', 'Sales Invoice'),
		('Pending', 'Sales Order'),
	)
	if (fa.workflow_state, ref.reference_doctype) not in valid_state_and_ref_combinations:
		frappe.throw(f'Wrong ref doctype for {fa.workflow_state} Finance Application')
	update_payments(fa, pe, save=True)
	

def update_payments(fa, pe, save=False):
	"""Update payment records. If fa has payment_plan, updates Payment Plan doc instead."""

	doc = frappe.get_doc('Payment Plan', fa.payment_plan) if fa.payment_plan else fa
	# Add payment to table
	doc.append('payment_refs',{
		'payment_entry': pe.name,
		'amount': pe.paid_amount,
		'date': pe.posting_date,
	})
	#update down payment fields
	paid_down_payment = 0
	for payment in doc.payment_refs:
		paid_down_payment += payment.amount
	
	doc.paid_down_payment_amount = paid_down_payment if paid_down_payment < doc.down_payment_amount else doc.down_payment_amount
	doc.pending_down_payment_amount = max(0,doc.down_payment_amount - paid_down_payment)
	if doc.down_payment_amount and doc.pending_down_payment_amount:
		doc.paid_down_payment_percent = 100*paid_down_payment/doc.down_payment_amount 
	else:
		doc.paid_down_payment_percent = 100	
	if save:	
		doc.save()
