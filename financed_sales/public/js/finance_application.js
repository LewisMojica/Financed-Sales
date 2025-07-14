frappe.ui.form.on('Finance Application', {
	repayment_term: function(frm) {
		if (frm.doc.repayment_term) {
			console.log('term changed');
			generate_installments(frm);
		}
	},
	
	down_payment: function(frm) {
		if (frm.doc.down_payment) {
			console.log('down payment changed');
			generate_installments(frm);
		}
	},
	
	first_installment: function(frm) {
		if (frm.doc.first_installment) {
			generate_installments(frm);
			console.log('date changed');
		}
	},
		
	application_fee: function(frm) {
		if (frm.doc.application_fee) {
			console.log('fee changed');
			generate_installments(frm);
		}
	},

	interest_rate: function(frm) {
		if (frm.doc.interest_rate) {
			console.log('interest_rate changed');
			generate_installments(frm);
		}
	}

});

function generate_installments(frm){
	frm.clear_table('installments');
	if (frm.doc.total_amount_to_finance && frm.doc.interest_rate && frm.doc.repayment_term && frm.doc.application_fee && frm.doc.first_installment && frm.doc.down_payment){
		console.log('generating installments');
		frm.doc.installment = (frm.doc.total_amount_to_finance - frm.doc.down_payment)/frm.doc.repayment_term;
		console.log(frm.doc);
		let monthly_payments = frm.doc.repayment_term;
		for (let i = 0; i < monthly_payments; i++){
			let row = frm.add_child('installments');
			row.amount = frm.doc.installment;
			row.due_date = frm.doc.first_installment;
		}
	} else {
		console.log('missing parameters');
	}
	frm.refresh_field('installments');
}
