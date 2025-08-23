// Copyright (c) 2025, Lewis Mojica and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Payment Plan", {
//	refresh(frm) {

//	},
// });
frappe.ui.form.on('Payment Plan', {
	 gen_installment_payment: function(frm) {
			d = get_dialog().show(); 
			d.hide();
	 }
});

function get_dialog(){
return new frappe.ui.Dialog({
	title: 'Payment details',
	fields: [
			{
				label: 'Amount to pay',
				fieldname: 'amount',
				fieldtype: 'Currency',
			},
			{
				label: 'Payment method',
				fiendname: 'payment_method',
				fieldtype: 'Link',
				options: 'Mode of Payment',
			},
	 ],
	 size: 'small', // small, large, extra-large 
	 primary_action_label: 'Submit payment',
	 primary_action(values) {
			console.log(values);
	 }
});

}
