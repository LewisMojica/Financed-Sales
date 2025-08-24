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

	#update installments payments
	if doc.doctype == 'Payment Plan':
		print(auto_alloc_payments(doc.down_payment_amount, doc.installments, doc.payment_refs))
	
	
	if save:	
		doc.save()

def auto_alloc_payments(down_payment, installments, payments):
	def to_cents(amount):
		return int(round(amount*100,2))

	installments = [{'amount': to_cents(installment.amount), 'payment_refs': []} for installment in installments]
	installments.insert(0, {'amount': to_cents(down_payment), 'payment_refs': []})
	payments = [{'payment_entry': payment.payment_entry, 'amount': to_cents(payment.amount), 'allocated': 0} for payment in payments] 

	print(down_payment)
	print(payments)
	print(installments)
	
	for installment in installments:
		installment_allocated = 0
		for payment in payments:
			if payment['allocated'] == payment['amount']:
				continue	
			elif payment['allocated'] > payment['amount']:
				raise ValueError(f'allocated > amount: {payment}')
			payment_to_allocate = payment['amount'] - payment['allocated']
			if installment_allocated >= installment['amount']:
				break
			elif payment_to_allocate <= installment['amount'] - installment_allocated:
				installment['payment_refs'].append({'payment_entry': payment['payment_entry'], 'amount': payment_to_allocate})	
				installment_allocated += payment_to_allocate
				payment['allocated'] = payment['amount']
				
			else:
				installment['payment_refs'].append({'payment_entry': payment['payment_entry'], 'amount': installment['amount'] - installment_allocated})	
				added_amount = installment['amount'] - installment_allocated
				installment_allocated += added_amount
				payment['allocated'] += added_amount

	return installments
