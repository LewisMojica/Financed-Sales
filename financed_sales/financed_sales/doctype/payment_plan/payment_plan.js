// Copyright (c) 2025, Lewis Mojica and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Payment Plan", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Payment Plan', {
    gen_installment_payment: function(frm) {
        frappe.call({
            method: "financed_sales.financed_sales.api.create_payment_from_pay_plan",
            args: { payment_plan_name: frm.doc.name, },
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
    }
});
