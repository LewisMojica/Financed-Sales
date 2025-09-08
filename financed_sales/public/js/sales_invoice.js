frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
		calculate_financed_total(frm);
	},
	
	custom_financed_items: {
		items_add: function(frm, cdt, cdn) {
			calculate_financed_total(frm);
		},
		items_remove: function(frm, cdt, cdn) {
			calculate_financed_total(frm);
		},
		amount: function(frm, cdt, cdn) {
			calculate_financed_total(frm);
		}
	}
});

function calculate_financed_total(frm) {
	if (frm.doc.custom_financed_items && frm.doc.custom_financed_items.length > 0) {
		let total = 0;
		frm.doc.custom_financed_items.forEach(function(item) {
			if (item.amount) {
				total += flt(item.amount);
			}
		});
		frm.set_value('custom_financed_total', total);
	} else {
		frm.set_value('custom_financed_total', 0);
	}
}
