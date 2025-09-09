// Copyright (c) 2024, Lewis Mojica and Contributors
// License: GNU General Public License v3. See license.txt

frappe.pages["overdue-financed-sales"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Overdue Financed Sales"),
		single_column: true,
	});

	wrapper.overdue_financed_sales = new financed_sales.OverdueFinancedSales(wrapper);

	frappe.breadcrumbs.add("Financed Sales");
};

financed_sales.OverdueFinancedSales = class OverdueFinancedSales {
	constructor(wrapper) {
		var me = this;
		// 0 setTimeout hack - this gives time for canvas to get width and height
		setTimeout(function () {
			me.setup(wrapper);
			me.get_data();
		}, 0);
	}

	setup(wrapper) {
		var me = this;

		// Company field
		this.company_field = wrapper.page.add_field({
			fieldtype: "Link",
			fieldname: "company",
			options: "Company",
			label: __("Company"),
			reqd: 1,
			default: frappe.defaults.get_user_default("company"),
			change: function () {
				me.company = this.value || frappe.defaults.get_user_default("company");
				me.get_data();
			},
		});

		// UI elements
		this.elements = {
			layout: $(wrapper).find(".layout-main"),
			refresh_btn: wrapper.page.set_primary_action(
				__("Refresh"),
				function () {
					me.get_data();
				},
				"fa fa-refresh"
			),
		};

		// No data message
		this.elements.no_data = $('<div class="alert alert-warning">' + __("No overdue payments found") + "</div>")
			.toggle(false)
			.appendTo(this.elements.layout);

		// Content wrapper
		this.elements.content_wrapper = $('<div class="overdue-content-wrapper"></div>').appendTo(
			this.elements.layout
		);

		this.company = frappe.defaults.get_user_default("company");

		// bind refresh
		this.elements.refresh_btn.on("click", function () {
			me.get_data(this);
		});
	}

	get_data(btn) {
		var me = this;
		if (!this.company) {
			frappe.throw(__("Please Select a Company."));
		}

		// TODO: Implement API call to get overdue data
		frappe.call({
			method: "financed_sales.financed_sales.page.overdue_financed_sales.overdue_financed_sales.get_overdue_data",
			args: {
				company: this.company,
			},
			btn: btn,
			callback: function (r) {
				if (!r.exc) {
					me.data = r.message;
					me.render();
				}
			},
		});
	}

	render() {
		let me = this;
		
		// Clear previous content
		me.elements.content_wrapper.empty();
		me.elements.no_data.toggle(false);

		// For now, just show a placeholder message
		if (!me.data || me.data.length === 0) {
			me.elements.no_data.toggle(true);
		} else {
			// TODO: Implement table rendering
			me.elements.content_wrapper.html('<div class="text-center"><h4>Overdue Payment Plans will be displayed here</h4><p>Data loaded: ' + me.data.length + ' records</p></div>');
		}
	}
};