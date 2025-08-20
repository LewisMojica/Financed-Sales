// public/js/point_of_sale.js
frappe.provide("erpnext.pos");

(function() {
	// 1. When clicked, call our whitelisted API to build a Quotation
	function onMyButtonClick() {
		const pos = window.cur_pos;
		const customer = pos.customer_details?.customer;
		if (!customer) {
			frappe.msgprint(__("Please select a customer first"));
			return;
		}

		const items = (pos.frm?.doc?.items || []).map(i => ({
			item_code: i.item_code,
			qty:			 i.qty,
			rate:			 i.rate
		}));
		if (!items.length) {
			frappe.msgprint(__("Cart is empty"));
			return;
		}

		frappe.call({
			method: "financed_sales.financed_sales.api.create_finance_app_from_pos_cart",
			args: { customer, items },
			freeze: true,
			callback: r => {
				if (r.message?.name) {
					frappe.msgprint(__(`Quotation {0} created`, [r.message.name]));
					// Optionally navigate to it:
					frappe.set_route("Form", "Finance Application", r.message.name);
				}
			}
		});
	}

	// 2. Inject “Financiar” button into the cart area
	function addCustomButton() {
		if (document.getElementById("my-custom-btn")) return;

		const container = document.querySelector(".cart-container");
		if (!container) return;

		const btn = document.createElement("button");
		btn.id = "my-custom-btn";
		btn.innerText = __("Financiar");
		btn.className = "btn btn-primary btn-sm";
		btn.style.position			= "relative";
		btn.style.zIndex				= "9999";
		btn.style.pointerEvents = "auto";

		btn.onclick = onMyButtonClick;
		container.appendChild(btn);
	}

	// 3. Run immediately, on AJAX reloads, and on DOM mutations
	addCustomButton();
	frappe.after_ajax(addCustomButton);
	new MutationObserver(addCustomButton)
		.observe(document.body, { childList: true, subtree: true });
})();

