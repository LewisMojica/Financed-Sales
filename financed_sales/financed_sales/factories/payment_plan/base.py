"""Base factory for creating Payment Plans."""
import frappe
from ..finance_application import create_finance_application


def create_payment_plan():
    """
    Create a basic Payment Plan following the standard workflow.

    Leverages create_finance_application() and approves it to create Payment Plan.

    Returns:
        dict: {
            'customer': Customer document name,
            'quotation': Quotation document name,
            'finance_application': Finance Application document name,
            'payment_plan': Payment Plan document name,
            'company': Company name
        }
    """
    # Create Finance Application (submitted)
    fin_app_result = create_finance_application()

    # Approve Finance Application to create Payment Plan
    finance_application = frappe.get_doc('Finance Application', fin_app_result['finance_application'])
    finance_application.reload()
    finance_application.db_set('workflow_state', 'Approved')

    if not finance_application.payment_plan:
        from ...create_docs_on_approval import on_approval
        on_approval(finance_application)

    payment_plan_name = finance_application.payment_plan
    if not payment_plan_name:
        frappe.throw("Payment Plan was not created automatically after approval")

    return {
        'customer': fin_app_result['customer'],
        'quotation': fin_app_result['quotation'],
        'finance_application': fin_app_result['finance_application'],
        'payment_plan': payment_plan_name,
        'company': fin_app_result['company']
    }
