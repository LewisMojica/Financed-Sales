// Copyright (c) 2025, Lewis Mojica and contributors
// For license information, please see license.txt

frappe.ui.form.on("Carta de Saldo", {
	payment_plan: function (frm) {
		if (!frm.doc.payment_plan) return;

		// Fetch linked fields from the Payment Plan
		frappe.db.get_value(
			"Payment Plan",
			frm.doc.payment_plan,
			["customer", "finance_application", "credit_invoice", "status"],
			(values) => {
				if (!values) return;

				frm.set_value("customer", values.customer);
				frm.set_value("finance_application", values.finance_application);
				frm.set_value("credit_invoice", values.credit_invoice);

				if (values.status !== "Completed") {
					frappe.msgprint({
						title: __("Plan Not Completed"),
						indicator: "orange",
						message: __(
							"The selected Payment Plan has status <b>{0}</b>. " +
							"A Carta de Saldo should only be issued for <b>Completed</b> plans.",
							[values.status]
						),
					});
				}
			}
		);
	},

	refresh: function (frm) {
		if (frm.doc.docstatus === 1) {
			// Submitted — add a shortcut to print
			frm.add_custom_button(__("Print Carta de Saldo"), () => {
				const w = window.open(
					frappe.urllib.get_full_url(
						`/printview?doctype=Carta%20de%20Saldo&name=${frm.doc.name}&format=Standard`
					)
				);
				if (!w) {
					frappe.msgprint(__("Please allow pop-ups to print this document."));
				}
			});
		}
	},
});
