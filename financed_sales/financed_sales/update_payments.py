def main(pe, method):
	if not pe.custom_is_finance_down_payment:
		return	
	
	# Validation: Block submission if number of references is not exactly 1
	if len(pe.references) != 1:
		frappe.throw('Number of refereces must be equal to 1')
	
	
	raise NotImplementedError("Function under construction")

