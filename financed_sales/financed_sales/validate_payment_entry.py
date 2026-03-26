import frappe
from frappe import _


def validate_payment_entry_references(doc, method):
    """
    Prevent direct payment entries against financed Sales Invoices.
    All payments for financed sales must go through the Finance Application workflow
    to maintain payment plan integrity.
    """
    if doc.doctype != "Payment Entry":
        return

    for ref in doc.get("references", []):
        if ref.reference_doctype == "Sales Invoice":
            finance_app = frappe.db.get_value(
                "Sales Invoice",
                ref.reference_name,
                "custom_finance_application"
            )

            if finance_app:
                if not doc.custom_is_finance_payment:
                    frappe.throw(
                        _(
                            "Cannot create Payment Entry directly against financed Sales Invoice {0}. "
                            "This invoice is linked to Finance Application {1}.<br><br>"
                            "Please follow the proper workflow:<br>"
                            "1. Go to the Finance Application {1}<br>"
                            "2. Create payment from there or use the payment plan workflow"
                        ).format(
                            frappe.bold(ref.reference_name),
                            frappe.bold(finance_app)
                        ),
                        title=_("Financed Sales Invoice - Direct Payment Not Allowed")
                    )

                fa_name = frappe.get_value(
                    "Sales Invoice", ref.reference_name, "custom_finance_application"
                )
                if not fa_name:
                    frappe.throw(
                        _(
                            "Payment Entry with 'Finance Payment' enabled must reference "
                            "a financed Sales Invoice with a valid Finance Application link."
                        ),
                        title=_("Invalid Finance Payment Configuration")
                    )
