// Copyright (c) 2025, Lewis Mojica and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Finance Application", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Finance Application', {
    create_application_form: function(frm) {
        if (!frm.doc.customer) {
            frappe.msgprint(__('Please select a customer first'));
            return;
        }

        frappe.call({
            method: 'create_application_form',
            doc: frm.doc,
            callback: function(response) {
                if (response.message) {
                    frappe.show_alert({
                        message: __('Finance Application Form created successfully'),
                        indicator: 'green'
                    });
                    frm.reload_doc();
                    frappe.set_route('Form', 'Finance Application Form', response.message);
                }
            },
            error: function(r) {
                frappe.msgprint({
                    title: __('Error'),
                    message: r.message || __('Failed to create Finance Application Form'),
                    indicator: 'red'
                });
            }
        });
    },

    gen_down_payment: function(frm) {
		dialog = get_payment_dialog(frm.doc.name)
		dialog.show()
		dialog.hide()
		
    }
});



frappe.ui.form.on('Payment Plan', {
         gen_installment_payment: function(frm) {
                        d = get_payment_dialog(frm.doc.name);
                        d.show();
                        d.hide();
         },
        gen_down_payment: function(frm){
                d = get_payment_dialog(frm.doc.name);
                d.show();
                d.hide();
        }
});

function get_payment_dialog(fa_name){
return new frappe.ui.Dialog({
        title: 'Payment details',
        fields: [
                        {
                                label: 'Amount to pay',
                                fieldname: 'paid_amount',
                                fieldtype: 'Currency',
                                reqd: 1,
                        },
                        {
                                label: 'Payment method',
                                fieldname: 'mode_of_payment',
                                fieldtype: 'Link',
                                options: 'Mode of Payment',
                                reqd: 1,
                                onchange: function() {
                                     const mode_of_payment = this.get_value();
                                     const dialog = window.cur_dialog;
                                    
                                     if (mode_of_payment) {
                                         frappe.db.get_value('Mode of Payment', mode_of_payment, 'type').then(r => {
                                             if (r.message && r.message.type === 'Bank') {
                                                 dialog.set_df_property('reference_number', 'hidden', false);
                                                 dialog.set_df_property('reference_date', 'hidden', false);
                                             } else {
                                                 dialog.set_df_property('reference_number', 'hidden', true);
                                                 dialog.set_df_property('reference_date', 'hidden', true);
                                             }
                                         });
                                     } else {
                                         dialog.set_df_property('reference_number', 'hidden', true);
                                         dialog.set_df_property('reference_date', 'hidden', true);
                                     }
                                }
                        },
                        {
                                label: 'Reference Number',
                                fieldname: 'reference_number',
                                fieldtype: 'Data',
                                hidden: 1,
                        },
                        {
                                label: 'Reference Date',
                                fieldname: 'reference_date',
                                fieldtype: 'Date',
                                default: frappe.datetime.get_today(),
                                hidden: 1,
                        },
        ],
        size: 'small', // small, large, extra-large
        primary_action_label: 'Submit payment',
        primary_action(values) {
                // Validate required fields
                if (!values.paid_amount) {
                        frappe.msgprint(__('Please enter the amount to pay'));
                        return;
                }
                if (!values.mode_of_payment) {
                        frappe.msgprint(__('Please select a payment method'));
                        return;
                }
                
                show_confirmation_dialog(values, fa_name, 'Finance Application');
         }
});

}

function show_confirmation_dialog(payment_values, source_name, source_type) {
	const confirmation_dialog = new frappe.ui.Dialog({
		title: 'Confirm Payment Submission',
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'payment_summary',
				options: `
				<div class="payment-summary">
					<h4>Payment Details:</h4>
					<p><strong>Amount to pay:</strong> ${format_currency(payment_values.paid_amount)}</p>
					<p><strong>Payment method:</strong> ${payment_values.mode_of_payment || 'Not selected'}</p>
						${payment_values.reference_number ? `<p><strong>Reference number:</strong> ${payment_values.reference_number}</p>` : ''}
						${payment_values.reference_date ? `<p><strong>Reference date:</strong> ${payment_values.reference_date}</p>` : ''}
						<p><strong>Source:</strong> ${source_type} - ${source_name}</p>
						<div class="alert alert-warning">
							<strong>Warning:</strong> This will create and submit a Payment Entry immediately.
						</div>
					</div>
				`
			}
		],
		size: 'small',
		primary_action_label: 'Confirm & Submit Payment',
		primary_action() {
			submit_payment(payment_values, source_name, source_type);
			confirmation_dialog.hide();
		},
		secondary_action_label: 'Cancel',
		secondary_action() {
			confirmation_dialog.hide();
		}
	});
	
	confirmation_dialog.show();
}

function submit_payment(payment_values, source_name, source_type) {
	const args = {
		paid_amount: payment_values.paid_amount,
		mode_of_payment: payment_values.mode_of_payment,
		submit: true
	};
	
	if (source_type === 'Finance Application') {
		args.finance_application_name = source_name;
	} else {
		args.payment_plan_name = source_name;
	}
	
	// Check payment method type to determine if reference fields are needed
	frappe.db.get_value('Mode of Payment', payment_values.mode_of_payment, 'type').then(r => {
		if (r.message && r.message.type === 'Bank') {
			args.reference_number = payment_values.reference_number;
			args.reference_date = payment_values.reference_date;
		}
		
		const method_name = source_type === 'Finance Application' 
			? "financed_sales.financed_sales.api.create_payment_entry_from_finance_application"
			: "financed_sales.financed_sales.api.create_payment_entry_from_payment_plan";
		
		frappe.call({
		method: method_name,
		args: args,
		callback: function(response) {
			if (response.message) {
				frappe.show_alert({
					message: __('Payment Entry created successfully'),
					indicator: 'green'
				});
				frappe.set_route('Form', 'Payment Entry', response.message);
			} else {
				frappe.msgprint("Error creating payment entry");
			}
		},
		error: function(r) {
			let error_msg = "Error creating payment entry";
			if (r.message) {
				error_msg = r.message;
			} else if (r.exc_type === 'TypeError' && r.exception && r.exception.includes('mode_of_payment')) {
				error_msg = "Payment method is required. Please select a payment method.";
			}
			frappe.msgprint({
				title: __('Payment Error'),
				message: error_msg,
				indicator: 'red'
			});
		}
		});
	});
}
