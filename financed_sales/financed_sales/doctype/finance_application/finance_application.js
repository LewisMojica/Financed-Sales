// Copyright (c) 2025, Lewis Mojica and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Finance Application", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Finance Application', {
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
                        },
                        {
                                label: 'Payment method',
                                fieldname: 'mode_of_payment',
                                fieldtype: 'Link',
                                options: 'Mode of Payment',
                                onchange: function() {
                                     const mode_of_payment = this.get_value();
                                     const dialog = window.cur_dialog;
                                    
                                     if (mode_of_payment === 'Wire Transfer' || mode_of_payment === 'Credit Card') {
                                         dialog.set_df_property('reference_number', 'hidden', false);
                                         dialog.set_df_property('reference_date', 'hidden', false);
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
                const args = {
					finance_application_name: fa_name,
					paid_amount: values.paid_amount,
					mode_of_payment: values.mode_of_payment,
					submit: true
				};
				
				if (values.mode_of_payment === 'Wire Transfer' || values.mode_of_payment === 'Credit Card') {
					args.reference_number = values.reference_number;
					args.reference_date = values.reference_date;
				}
				
                frappe.call({
                        method: "financed_sales.financed_sales.api.create_payment_entry_from_finance_application",
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
                        }
                });
         }
});

}
