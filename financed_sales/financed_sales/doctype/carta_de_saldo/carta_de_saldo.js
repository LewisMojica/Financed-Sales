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
							"El Plan de Pago seleccionado tiene estado <b>{0}</b>. " +
							"Una Carta de Saldo solo debe ser emitida para Plan es<b>Completados</b>.",
							[values.status]
						),
					});
				}
			}
		);
	},
});
