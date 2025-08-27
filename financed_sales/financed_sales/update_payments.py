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
		print(f' ~~~~~~ init old inst state ~~~~~\n {convert_fa_installments_to_alloc_format(doc.installments)}\n  ~~~~~~ end old inst state ~~~~~~ ')
		new_installments_state = auto_alloc_payments(doc.down_payment_amount, doc.installments, doc.payment_refs)
		apply_installments_state(doc, new_installments_state)
		print(f' ~~~~~~ init new inst state ~~~~~\n {new_installments_state}\n~~~~~~~~~~~~~~~ end new inst state~~~~~~~')
		
	
	
	if save:	
		doc.save()

def to_cents(amount):
		return int(round(amount*100))

def auto_alloc_payments(down_payment, installments, payments):
	
	installments = [{'amount': to_cents(installment.amount), 'payment_refs': []} for installment in installments]
	installments.insert(0, {'amount': to_cents(down_payment), 'payment_refs': []})
	payments = [{'payment_entry': payment.payment_entry, 'amount': to_cents(payment.amount), 'allocated': 0} for payment in payments] 

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

def get_current_installments_state(installments):
	pass

def installments_refs_empty(installments, down_payment):
	return True

def get_payment_refs(inst):
	if not inst.payment_ref:
		return []
	if inst.payment_doctype == 'Payment Entry':
		return [{'payment_entry': inst.payment_ref, 'amount': inst.paid_amount}]
	if inst.payment_doctype == 'Payment Entry List':
		pay_list = frappe.get_doc('Payment Entry List', inst.payment_ref)
		if len(pay_list.refs) == 0:
			return []
		refs = []
		for ref in pay_list.refs:
			refs.append({'payment_entry': ref.payment_entry, 'amount': ref.paid_amount})
		return refs
	raise ValueError(f'Unknown payment_doctype: {inst.payment_doctype}')

def convert_fa_installments_to_alloc_format(installments_table):
	output = [{'amount': to_cents(installment.amount), 'payment_refs': []} for installment in installments_table]
	for output_inst,inst in zip(output, installments_table):
		output_inst['payment_refs'] = get_payment_refs(inst)
	return output	
def apply_installments_state(pp, new_installments_state):
	new_installments_state.pop(0) #remove down payment	
	if installments_refs_empty(pp.installments, pp.down_payment_amount):
		for new_inst, actual_inst in zip(new_installments_state, pp.installments):
			no_refs = len(new_inst['payment_refs']) 
			print(f'actual inst is <{actual_inst.payment_ref}>')
			if no_refs == 0:
				break
			elif no_refs == 1:
				actual_inst.payment_doctype = 'Payment Entry'
				actual_inst.payment_ref = new_inst['payment_refs'][0]['payment_entry']
			else:
				actual_inst.payment_doctype = 'Payment Entry List'
				pel = frappe.new_doc('Payment Entry List')
				for pay_ref in new_inst['payment_refs']:
					pel.append('refs', {
						'payment_entry': pay_ref['payment_entry'],
						'paid_amount': pay_ref['amount'],
						
					})
				pel.save()
				actual_inst.payment_ref = pel.name

			
		


