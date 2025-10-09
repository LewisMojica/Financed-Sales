"""Base factory for creating Payment Plans."""
import frappe
import uuid
from ...api import create_finance_application


def create_payment_plan():
    """
    Create a basic Payment Plan following the standard workflow.

    Workflow: Quotation → Finance Application → Submit → Approve → Payment Plan

    Returns:
        dict: {
            'customer': Customer document name,
            'quotation': Quotation document name,
            'finance_application': Finance Application document name,
            'payment_plan': Payment Plan document name,
            'company': Company name
        }
    """
    from ..helpers import (
        _ensure_financed_sales_settings,
        _get_or_create_test_customer,
        _get_or_create_test_company,
        _get_or_create_test_item
    )

    # Step 1: Configure settings
    _ensure_financed_sales_settings()

    # Step 2: Create dependencies
    customer = _get_or_create_test_customer()
    company = _get_or_create_test_company()
    item = _get_or_create_test_item()

    # Step 3: Get company currency
    company_currency = frappe.db.get_value('Company', company, 'default_currency')

    # Step 4: Create Quotation
    quotation = frappe.get_doc({
        'doctype': 'Quotation',
        'party_name': customer,
        'company': company,
        'currency': company_currency,
        'conversion_rate': 1.0,
        'transaction_date': frappe.utils.today(),
        'valid_till': frappe.utils.add_days(frappe.utils.today(), 30),
        'items': [{
            'doctype': 'Quotation Item',
            'item_code': item,
            'qty': 1,
            'rate': 50000
        }]
    }).insert(ignore_permissions=True)

    # Step 5: Submit quotation
    quotation.submit()

    # Step 6: Create Finance Application
    fin_app_result = create_finance_application(quotation.name)
    finance_application = frappe.get_doc('Finance Application', fin_app_result['name'])

    # Step 7: Set up payment terms
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

    # Step 8: Submit Finance Application
    finance_application.workflow_state = 'Pending'
    finance_application.save()
    finance_application.reload()
    finance_application.submit()

    # Step 9: Create Sales Order if needed
    if not finance_application.sales_order:
        from ...create_docs_on_approval import create_sales_order
        create_sales_order(finance_application)

    # Step 10: Approve to create Payment Plan
    finance_application.reload()
    finance_application.db_set('workflow_state', 'Approved')

    if not finance_application.payment_plan:
        from ...create_docs_on_approval import on_approval
        on_approval(finance_application)

    payment_plan_name = finance_application.payment_plan
    if not payment_plan_name:
        frappe.throw("Payment Plan was not created automatically after approval")

    return {
        'customer': customer,
        'quotation': quotation.name,
        'finance_application': finance_application.name,
        'payment_plan': payment_plan_name,
        'company': company
    }
