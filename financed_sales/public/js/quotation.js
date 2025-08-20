frappe.ui.form.on('Quotation', {
	refresh: (frm) => {
		// Only show button if quotation is submitted
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Appply for Financing'), () => {
			   apply_for_credit(frm);
			}, __('Create'));
		}
	}
});

const apply_for_credit = (frm) => {
	// Validation checks
	if (!frm.doc.party_name) {
		frappe.msgprint(__('Customer is required'));
		return;
	}
	
	if (!frm.doc.grand_total || frm.doc.grand_total <= 0) {
		frappe.msgprint(__('Grand total must be greater than 0'));
		return;
	}

	frappe.call({
		method: 'financed_sales.financed_sales.api.create_finance_application',
		args: {
			quotation_name: frm.doc.name 
		},
		callback: (response) => {
			if (response.message) {
				frappe.show_alert({
					message: __('Finance Application created successfully'),
					indicator: 'green'
				});
				
				// Navigate to the newly created Finance Approval
				frappe.set_route('Form', 'Finance Application', response.message.name);
			}
		},
		error: (error) => {
			frappe.show_alert({
				message: __('Error creating Finance Application'),
				indicator: 'red'
			});
			console.error('Finance Application creation error:', error);
		}
	});	
}

const check_customer_credit_status = (frm) => {
	// Optional: Check if customer has existing credit applications
	frappe.call({
		method: 'financed_sales.api.get_customer_credit_status',
		args: {
			customer: frm.doc.customer
		},
		callback: (r) => {
			if (r.message && r.message.has_pending_applications) {
				frm.dashboard.add_comment(
					__('This customer has pending credit applications'), 
					'orange', 
					true
				);
			}
		}
	});
};

