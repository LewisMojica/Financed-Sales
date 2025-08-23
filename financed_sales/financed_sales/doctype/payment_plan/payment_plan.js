// Copyright (c) 2025, Lewis Mojica and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Payment Plan", {
//	refresh(frm) {

//	},
// });
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

function get_payment_dialog(pp_name){
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
			},
	],
	size: 'small', // small, large, extra-large 
	primary_action_label: 'Submit payment',
	primary_action(values) {
		frappe.call({
			method: "financed_sales.financed_sales.api.create_payment_entry_from_payment_plan",
			args: { payment_plan_name:pp_name, paid_amount: values.paid_amount, mode_of_payment: values.mode_of_payment, submit: true},
			callback: function(response) {
				if (response.message) {
				// Open the payment entry form
					var doclist = frappe.model.sync(response.message);
					frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
				} else {
					frappe.msgprint("Error creating payment entry");
				}
			}
		});
		console.log(values);
	 }
});

}

