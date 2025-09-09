// Copyright (c) 2024, Lewis Mojica and Contributors
// License: GNU General Public License v3. See license.txt

frappe.pages["overdue-financed-sales"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Overdue Financed Sales"),
		single_column: true,
	});

	wrapper.overdue_financed_sales = new OverdueFinancedSales(wrapper);

	frappe.breadcrumbs.add("Financed Sales");
};

class OverdueFinancedSales {
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

		// Hardcoded demo data for testing - bypass API
		let demo_data = [
			{
				customer: "John Doe Enterprises",
				finance_application_id: "FINAPP-2024-001",
				overdue_amount: 1500.00,
				days_overdue: 5
			},
			{
				customer: "ABC Company Ltd", 
				finance_application_id: "FINAPP-2024-002",
				overdue_amount: 3200.50,
				days_overdue: 23
			},
			{
				customer: "Smith & Associates",
				finance_application_id: "FINAPP-2024-003", 
				overdue_amount: 750.25,
				days_overdue: 45
			}
		];

		me.render_hardcoded_table(demo_data);
	}

	render_hardcoded_table(data) {
		let me = this;
		
		let table_html = '<div class="overdue-summary"><h4>Overdue Financed Sales (' + data.length + ' records)</h4></div>';
		table_html += '<table class="table table-bordered overdue-table">';
		table_html += '<thead><tr>';
		table_html += '<th>Customer</th>';
		table_html += '<th>Finance Application</th>'; 
		table_html += '<th>Overdue Amount</th>';
		table_html += '<th>Days Overdue</th>';
		table_html += '</tr></thead><tbody>';

		data.forEach(function(row) {
			let days_class = row.days_overdue > 30 ? "text-danger" : "text-warning";
			table_html += '<tr>';
			table_html += '<td><strong>' + row.customer + '</strong></td>';
			table_html += '<td>' + row.finance_application_id + '</td>';
			table_html += '<td>$' + row.overdue_amount.toFixed(2) + '</td>';
			table_html += '<td class="' + days_class + '"><strong>' + row.days_overdue + ' days</strong></td>';
			table_html += '</tr>';
		});

		table_html += '</tbody></table>';
		me.elements.content_wrapper.html(table_html);
	}
};