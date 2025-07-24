import frappe

def main(doc,method):
	if doc.workflow_state == 'Approved':
		plan = frappe.new_doc('Payment Plan')
		plan.finance_application = doc.name
		
		for installment in doc.installments:
			plan.append('installments',{
				'due_date': installment.due_date,
				'amount': installment.amount,
				'paid_amount': 0,
				'pending_amount': 0,
			})
		plan.insert()
		plan.submit()
