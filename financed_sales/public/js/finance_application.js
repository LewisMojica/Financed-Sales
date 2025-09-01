const genFacturaProforma = (frm) => {
	frm.call('create_factura_proforma').then(r => {
		if (r.message) {
			frappe.show_alert({
				message: __('Factura Proforma created successfully'),
				indicator: 'green'
			});
			frappe.set_route('Form', 'Factura Proforma', r.message);
		}
	}).catch(error => {
		frappe.show_alert({
			message: __('Error creating Factura Proforma'),
			indicator: 'red'
		});
		console.error('Error:', error);
	});
}

frappe.ui.form.on('Finance Application', {
	refresh: (frm) => {
		// Only show button if doc is submitted
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Generar Factura Proforma'), () => {
			   genFacturaProforma(frm);
			}, __('Create'));
		}
	}
});

frappe.ui.form.on('Finance Application', {
	repayment_term: function(frm) {
		if (frm.doc.repayment_term) {
			generate_installments(frm);
		}
	},
	
	down_payment_amount: function(frm) {
		if (frm.doc.down_payment_amount) {
			generate_installments(frm);
			frm.set_df_property('pending_down_payment_amount', 'read_only', 0);
			frm.doc.pending_down_payment_amount = frm.doc.down_payment_amount
			frm.set_df_property('pending_down_payment_amount', 'read_only', 1);
		}
	},
	
	first_installment: function(frm) {
		if (frm.doc.first_installment) {
			generate_installments(frm);
		}
	},
		
	application_fee: function(frm) {
		if (frm.doc.application_fee) {
			generate_installments(frm);
		}
	},

	interest_rate: function(frm) {
		if (frm.doc.interest_rate) {
			generate_installments(frm);
		}
	},
	rate_period: function(frm) {
		generate_installments(frm);
	}
});

function generate_installments(frm){
	frm.clear_table('installments');
	if (frm.doc.total_amount_to_finance && frm.doc.interest_rate && frm.doc.repayment_term && frm.doc.application_fee && frm.doc.first_installment && frm.doc.down_payment_amount){
		let owed_amount = frm.doc.total_amount_to_finance - frm.doc.down_payment_amount;
		let monthly_pays = frm.doc.repayment_term;
		let monthly_rate = frm.doc.interest_rate / (frm.doc.rate_period === "Monthly" ? 100 : 1200);
		frm.set_df_property('installment', 'read_only', 0);
		frm.doc.installment = owed_amount/monthly_pays + owed_amount*monthly_rate;
		frm.set_df_property('installment', 'read_only', 1);
		let monthly_payments = frm.doc.repayment_term;
		for (let i = 0; i < monthly_payments; i++){
			let row = frm.add_child('installments');
			row.amount = frm.doc.installment;
			row.due_date = frappe.datetime.add_months(frm.doc.first_installment, i);
		}
		frm.set_df_property('credit_expiration_date', 'read_only', 0);
		frm.set_df_property('total_credit', 'read_only', 0);
		frm.set_df_property('interests', 'read_only', 0);
		frm.set_value('credit_expiration_date', frappe.datetime.add_months(frm.doc.first_installment, monthly_payments-1));
		frm.set_value('total_credit', frm.doc.repayment_term*frm.doc.installment);
		frm.set_value('interests',frm.doc.repayment_term*frm.doc.installment-(frm.doc.total_amount_to_finance-frm.doc.down_payment_amount))
		frm.set_df_property('credit_expiration_date', 'read_only', 1);
		frm.set_df_property('total_credit', 'read_only', 1);
		frm.set_df_property('interests', 'read_only', 1);
		


	} 
	frm.refresh_field('installment');
	frm.refresh_field('installments');
}


	



