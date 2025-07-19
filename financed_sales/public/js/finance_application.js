const genFacturaProforma = (frm) => {
	frappe.call({
		method: 'frappe.client.insert',
		args: {
			doc: {
				doctype: 'Factura Proforma',
				finance_application: frm.doc.name,
				customer: frm.doc.customer
			}
		},
		callback: (response) => {
			if (response.message) {
				frappe.show_alert({
					message: __('Factura Proforma created successfully'),
					indicator: 'green'
				});
				
				// Navigate to the newly created Finance Approval
				frappe.set_route('Form', 'Factura Proforma', response.message.name);
			}
		},
		error: (error) => {
			frappe.show_alert({
				message: __('Error creating Factura Proforma'),
				indicator: 'red'
			});
			console.error('Factura Proforma creation error:', error);
		}
	});	

}

frappe.ui.form.on('Finance Application', {
	refresh: (frm) => {
		// Only show button if doc is submitted
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__('Generar Factura Proforma'), () => {
			   genFacturaProforma(frm);
			}, __('Create'));
		}
	}
});

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
		let owed_amount = frm.doc.total_amount_to_finance - frm.doc.down_payment;
		let monthly_pays = frm.doc.repayment_term;
		let monthly_rate = frm.doc.interest_rate/1200;
		frm.set_df_property('installment', 'read_only', 0);
		frm.doc.installment = owed_amount/monthly_pays + owed_amount*monthly_rate;
		frm.set_df_property('installment', 'read_only', 1);
		let monthly_payments = frm.doc.repayment_term;
		for (let i = 0; i < monthly_payments; i++){
			let row = frm.add_child('installments');
			row.amount = frm.doc.installment;
			row.due_date = frm.doc.first_installment;
		}
	} 
	frm.refresh_field('installment');
	frm.refresh_field('installments');
}


	



