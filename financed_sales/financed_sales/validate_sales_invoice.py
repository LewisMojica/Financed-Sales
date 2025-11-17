import frappe
from frappe import _

def validate_sales_invoice_from_financed_order(doc, method):
    """
    Prevent manual creation of Sales Invoice from Sales Orders that are linked to Finance Applications.
    This protects the integrity of the financed sales workflow.
    """
    # Skip validation if this is an automated creation from Finance Application workflow
    # Check if the invoice has custom_is_credit_invoice flag (set by our workflow)
    if hasattr(doc, 'custom_is_credit_invoice') and doc.custom_is_credit_invoice:
        return

    # Check each item to see if it references a Sales Order with Finance Application
    for item in doc.get("items", []):
        if item.sales_order:
            finance_application = frappe.db.get_value(
                "Sales Order",
                item.sales_order,
                "custom_finance_application"
            )

            if finance_application:
                frappe.throw(
                    _(
                        "Cannot create Sales Invoice manually from Sales Order {0} "
                        "because it is linked to Finance Application {1}.<br><br>"
                        "Please follow the proper workflow:<br>"
                        "1. Go to the Finance Application {1}<br>"
                        "2. Submit the Finance Application for approval<br>"
                        "3. The system will automatically create the credit invoice"
                    ).format(
                        frappe.bold(item.sales_order),
                        frappe.bold(finance_application)
                    ),
                    title=_("Financed Sales Order - Manual Invoice Not Allowed")
                )