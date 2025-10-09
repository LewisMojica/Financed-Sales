"""Factory for creating Finance Applications."""
import frappe
from ..api import create_finance_application as api_create_finance_application
from .quotation import create_quotation
from .helpers import _ensure_financed_sales_settings


def create_finance_application():
    """
    Create a submitted and approved Finance Application with Payment Plan.

    Returns:
        dict: {
            'customer': Customer document name,
            'quotation': Quotation document name,
            'finance_application': Finance Application document name,
            'company': Company name
        }
    """
    _ensure_financed_sales_settings()

    # Create quotation
    quotation_result = create_quotation()

    # Create Finance Application via API
    fin_app_result = api_create_finance_application(quotation_result['quotation'])
    finance_application = frappe.get_doc('Finance Application', fin_app_result['name'])

    # Set up payment terms
    finance_application.repayment_term = 12
    finance_application.first_installment = frappe.utils.add_days(frappe.utils.today(), 30)

    # Calculate and add installments
    amount_to_finance = finance_application.total_amount_to_finance - finance_application.down_payment_amount
    monthly_installment = amount_to_finance / finance_application.repayment_term

    for i in range(finance_application.repayment_term):
        installment_date = frappe.utils.add_months(finance_application.first_installment, i)
        finance_application.append('installments', {
            'doctype': 'Financed Sale Installment',
            'installment_date': installment_date,
            'due_date': installment_date,
            'amount': monthly_installment
        })

    # Submit Finance Application
    finance_application.workflow_state = 'Pending'
    finance_application.save()
    finance_application.reload()
    finance_application.submit()

    # Create Sales Order if needed
    if not finance_application.sales_order:
        from ..create_docs_on_approval import create_sales_order
        create_sales_order(finance_application)

    return {
        'customer': quotation_result['customer'],
        'quotation': quotation_result['quotation'],
        'finance_application': finance_application.name,
        'company': quotation_result['company']
    }
