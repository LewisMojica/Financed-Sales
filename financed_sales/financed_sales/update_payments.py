import frappe
from copy import deepcopy 
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
	"""
	Update payment records. If Finance Aplication has a Payment Plan it 
	updates the Payment Plan doc, if not, it update the Finance Applicatio.

	"""
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
		print(get_payment_refs_from_downp(doc))
		current_payment_state = convert_fa_installments_to_alloc_format(doc)
		print(f' ~~~~~~ init old inst state ~~~~~\n {current_payment_state}\n  ~~~~~~ end old inst state ~~~~~~ ')
		new_payment_state = auto_alloc_payments(doc.down_payment_amount, doc.installments, doc.payment_refs)
		ok = validate_states_continuity(new_payment_state,current_payment_state) 
		print(f'Validation Result <{ok}>')
		apply_installments_state(doc, new_payment_state)
		print(f' ~~~~~~ init new inst state ~~~~~\n {new_payment_state}\n~~~~~~~~~~~~~~~ end new inst state~~~~~~~')
		
	
	
	if save:	
		doc.save()

def to_cents(amount):
	return int(round(amount*100))

def from_cents(amount_in_cents):
	return amount_in_cents / 100

def auto_alloc_payments(down_payment, installments_table, payments_table):
	
	installments = [{'amount': to_cents(installment.amount), 'payment_refs': []} for installment in installments_table]
	installments.insert(0, {'amount': to_cents(down_payment), 'payment_refs': []})
	payments = [{'payment_entry': payment.payment_entry, 'amount': to_cents(payment.amount), 'date': payment.date, 'allocated': 0} for payment in payments_table] 

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
				installment['payment_refs'].append({'payment_entry': payment['payment_entry'], 'amount': payment_to_allocate, 'date': payment['date']})	
				installment_allocated += payment_to_allocate
				payment['allocated'] = payment['amount']
				
			else:
				installment['payment_refs'].append({'payment_entry': payment['payment_entry'], 'amount': installment['amount'] - installment_allocated, 'date': payment['date']})	
				added_amount = installment['amount'] - installment_allocated
				installment_allocated += added_amount
				payment['allocated'] += added_amount

	return installments

def get_payment_refs_from_downp(pp):
	if not pp.down_payment_reference:
		return []
	if pp.down_payment_ref_type == 'Payment Entry':
		return [{'payment_entry': pp.down_payment_reference, 'amount': to_cents(pp.paid_down_payment_amount)}]
	if pp.down_payment_ref_type == 'Payment Entry List':
		pay_list = frappe.get_doc('Payment Entry List', pp.down_payment_reference)              	
		if len(pay_list.refs) == 0:
			return []
		refs = []
		for ref in pay_list.refs:
			refs.append({'payment_entry': ref.payment_entry, 'amount': ref.paid_amount})
		return refs
	raise ValueError(f'Unknown payment_doctype: {pp.down_payment_ref_type}')


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

def convert_fa_installments_to_alloc_format(pp):
	installments_table = pp.installments
	output = [{'amount': to_cents(installment.amount), 'payment_refs': []} for installment in installments_table]
	for output_inst,inst in zip(output, installments_table):
		output_inst['payment_refs'] = get_payment_refs(inst)
	return output	
def apply_installments_state(pp, _new_installments_state):
	new_payment_state = deepcopy(_new_installments_state)
	downp_state = new_payment_state.pop(0) #remove down payment	
	downp_refs_no = len(downp_state['payment_refs'])
	print(downp_refs_no)
	if downp_refs_no == 1:
		pp.down_payment_ref_type = 'Payment Entry'
		pp.down_payment_reference = downp_state['payment_refs'][0]['payment_entry']
		print(f'{pp.down_payment_ref_type}---{pp.down_payment_reference}')
	elif downp_refs_no > 1:
		#if there is a payment entry list don't create a new one, just add the refs to the pel
		if pp.down_payment_ref_type == 'Payment Entry List' and pp.down_payment_reference:
			pel = frappe.get_doc('Payment Entry List', pp.down_payment_reference)
			pel.refs.clear()
			for ref in downp_state['payment_refs']:     		
				pel.append('refs',{
					'payment_entry': ref['payment_entry'],
					'paid_amount': from_cents(ref['amount']),
					'date': ref.get('date'),
				})
			pel.save()
		else:
			pp.down_payment_ref_type = 'Payment Entry List'
			pel = frappe.new_doc('Payment Entry List')
			for ref in downp_state['payment_refs']:
				pel.append('refs',{
					'payment_entry': ref['payment_entry'],
					'paid_amount': from_cents(ref['amount']),
					'date': ref.get('date'),
				})
			pel.save()
			pp.down_payment_reference = pel.name
		
	for new_inst, actual_inst in zip(new_payment_state, pp.installments):
		no_refs = len(new_inst['payment_refs']) 
		if no_refs == 0:
			# No payments for this installment
			actual_inst.paid_amount = 0
			actual_inst.pending_amount = actual_inst.amount
			break
		elif no_refs == 1:
			actual_inst.payment_doctype = 'Payment Entry'
			actual_inst.payment_ref = new_inst['payment_refs'][0]['payment_entry']
			# Calculate paid amount from single payment
			actual_inst.paid_amount = from_cents(new_inst['payment_refs'][0]['amount'])
			actual_inst.pending_amount = actual_inst.amount - actual_inst.paid_amount
		else:
			if actual_inst.payment_doctype == 'Payment Entry List' and actual_inst.payment_ref:
				pel = frappe.get_doc('Payment Entry List', actual_inst.payment_ref)
				pel.refs.clear()
				for ref in new_inst['payment_refs']:
					pel.append('refs',{
						'payment_entry': ref['payment_entry'],
						'paid_amount': from_cents(ref['amount']),
						'date': ref.get('date'),
					})
				pel.save()
			else:
				actual_inst.payment_doctype = 'Payment Entry List'
				pel = frappe.new_doc('Payment Entry List')
				for pay_ref in new_inst['payment_refs']:
					pel.append('refs', {
						'payment_entry': pay_ref['payment_entry'],
						'paid_amount': from_cents(pay_ref['amount']),
						'date': pay_ref.get('date'),
					})
				pel.save()
				actual_inst.payment_ref = pel.name
			
			# Calculate total paid amount from multiple payments
			total_paid = sum(ref['amount'] for ref in new_inst['payment_refs'])
			actual_inst.paid_amount = from_cents(total_paid)
			actual_inst.pending_amount = actual_inst.amount - actual_inst.paid_amount

			
		

def validate_states_continuity(_long_state,_short_state):
	def trim_state(state):
		print(state)
		trimmed_state = []
		found_empty_refs = False
		for inst in state:
			if len(inst['payment_refs']) != 0 and not found_empty_refs:
				trimmed_state.append(inst)
			elif not found_empty_refs:
				found_empty_refs = True
			elif len(inst['payment_refs']) != 0:
				frappe.throw('Found non empty refs after an empty refs, this means that an installment was paid befored paying the previus one')	
		return trimmed_state

	#trim states (remove installments that have empty payment_refs
	long_state = deepcopy(_long_state)
	short_state = deepcopy(_short_state)
	long_state = trim_state(long_state)
	short_state = trim_state(short_state)
	print(f'trimmed states: \n {long_state} \n \n {short_state}')	
	if short_state == long_state:
		return 1
	if short_state == []:
		return 0

	min_index = len(short_state) -1
	print(f'min in = {min_index} \n {short_state}')
	if min_index > len(long_state):
		return -1
	
	if short_state[0:min_index -1] != long_state[0:min_index -1]:
		print(f'{short_state[0:min_index -1]} != {long_state[0:min_index -1]}')
		return -2
	
	refs_min_index = len(short_state[min_index]['payment_refs'])-1	
	if refs_min_index > len(long_state[min_index]['payment_refs'])-1:
		return -3

	if short_state[min_index]['payment_refs'][0:refs_min_index] != long_state[min_index]['payment_refs'][0:refs_min_index]:
		return -4

	if short_state[min_index] != long_state[min_index]:
		return min_index
	else:
		return min_index + 1
