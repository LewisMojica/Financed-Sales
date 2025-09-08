// Copyright (c) 2025, Lewis Mojica and contributors
// For license information, please see license.txt

frappe.listview_settings["Payment Plan"] = {
	get_indicator: function (doc) {
		const status_colors = {
			Draft: "red",
			Active: "blue",
			Completed: "green",
			Overdue: "red",
			Renegotiated: "orange",
			Cancelled: "gray",
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	},
};
