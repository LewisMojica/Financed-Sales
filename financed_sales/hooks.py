app_name = "financed_sales"
app_title = "Financed Sales"
app_publisher = "Lewis Mojica"
app_description = "Financed Sales enables customer financed sales workflows in ERPNext. Creates financing applications from quotations and POS transactions and manages payment plans."
app_email = "lewismojica3@gmail.com"
app_license = "gpl-3.0"
page_js = {
	"pos": "public/js/point_of_sale.js",
	"point-of-sale": "public/js/point_of_sale.js",
}
doctype_js = {
	"Quotation": "public/js/quotation.js",
	"Finance Application": "public/js/finance_application.js"
}
fixtures = [
	{"doctype": "Custom Field", "filters": [["fieldname", "like", "custom_%"], ["module", "=", "Financed Sales"]]},
	{
		"doctype": "Workflow",
		"filters": {"name": "Finance Application Approval"}
	},
	{
		"doctype": "Workflow State" 
	},
	{
		"doctype": "Print Format",
		"filters": { "name": 'Factura Proforma' }
	},
	{
		"doctype": "Role",
		"filters": {"name": ["in", ["Financed Sales Manager", "Financed Sales User"]]}
	},
]
doc_events = {
	"Finance Application": {
		"on_update": [ "financed_sales.financed_sales.create_docs_on_approval.main"],
		"on_update_after_submit": [ "financed_sales.financed_sales.create_docs_on_approval.main"],
	},
	"Payment Entry": {
		"on_submit": ["financed_sales.financed_sales.update_payments.main"],
	},
}
scheduler_events = {
	"daily": [
		"financed_sales.financed_sales.doctype.payment_plan.payment_plan.daily_overdue_check"
	],
}

