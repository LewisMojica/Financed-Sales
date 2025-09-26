import frappe
import uuid
from datetime import datetime, timedelta
from financed_sales.financed_sales.api import create_finance_application


def create_test_payment_plan_with_penalties():
    """
    Create a realistic Payment Plan with multiple installments including penalty amounts.

    This creates a Payment Plan directly using the same pattern as the automatic workflow,
    but without triggering complex workflow dependencies.

    Returns:
        dict: {
            'customer': Customer document name,
            'quotation': Quotation document name,
            'finance_application': Finance Application document name,
            'payment_plan': Payment Plan document name,
            'credit_invoice': Credit Invoice document name
        }
    """

    # Step 1: Handle dependencies - create customer if needed
    customer = _get_or_create_test_customer()

    # Step 2: Handle dependencies - create test item if needed
    item = _get_or_create_test_item()

    # Step 3: Create Quotation with realistic financing amounts
    quotation = frappe.get_doc({
        'doctype': 'Quotation',
        'party_name': customer,
        'transaction_date': frappe.utils.today(),
        'valid_till': frappe.utils.add_days(frappe.utils.today(), 30),
        'items': [{
            'doctype': 'Quotation Item',
            'item_code': item,
            'qty': 1,
            'rate': 50000  # $50,000 - realistic amount for financing with significant installments
        }]
    }).insert(ignore_permissions=True)

    # Step 4: Submit quotation (required for finance applications)
    quotation.submit()

    # Step 5: Create Finance Application from quotation (replicates UI workflow)
    finance_app_response = create_finance_application(quotation.name)
    finance_app = frappe.get_doc('Finance Application', finance_app_response['name'])

    # Step 6: Configure realistic financing terms
    finance_app.repayment_term = 12  # 12 months
    finance_app.interest_rate = 8.0  # 8% monthly interest
    finance_app.first_installment = frappe.utils.add_days(frappe.utils.today(), 30)

    # Step 6.1: Generate installments (required for submission)
    _generate_installments(finance_app)
    finance_app.save()

    # Step 7: Create a Credit Invoice manually (similar to create_docs_on_approval.py pattern)
    credit_invoice = _create_test_credit_invoice(finance_app)

    # Step 8: Create Payment Plan manually (replicates create_payment_plan from create_docs_on_approval.py)
    payment_plan = _create_test_payment_plan(finance_app, credit_invoice.name)

    # Step 9: Add realistic penalty amounts to installments (simulates overdue scenarios)
    penalty_installments = [0, 2, 4]  # Add penalties to installments 1, 3, and 5 (0-indexed)
    penalty_amounts = [500, 750, 1200]  # Escalating penalty amounts

    for i, penalty_amount in zip(penalty_installments, penalty_amounts):
        if i < len(payment_plan.installments):
            payment_plan.installments[i].penalty_amount = penalty_amount

    # Step 10: Save the Payment Plan with penalty amounts
    payment_plan.save()

    return {
        'customer': customer,
        'quotation': quotation.name,
        'finance_application': finance_app.name,
        'payment_plan': payment_plan.name,
        'credit_invoice': credit_invoice.name
    }


def _get_or_create_test_customer():
    """Get existing test customer or create new one with unique name"""
    unique_suffix = str(uuid.uuid4())[:8]
    customer_name = f"Test Customer {unique_suffix}"

    customer = frappe.get_doc({
        'doctype': 'Customer',
        'customer_name': customer_name,
        'customer_type': 'Individual'
    }).insert(ignore_permissions=True)

    return customer.name


def _get_or_create_test_item():
    """Get existing test item or create new one"""
    # Check for existing test item first
    existing_item = frappe.db.get_value('Item', {'is_sales_item': 1}, 'item_code')
    if existing_item:
        return existing_item

    # Create test item if none exists
    unique_suffix = str(uuid.uuid4())[:8]
    item = frappe.get_doc({
        'doctype': 'Item',
        'item_code': f'TEST-ITEM-{unique_suffix}',
        'item_name': f'Test Item {unique_suffix}',
        'item_group': 'Products',
        'stock_uom': 'Nos',
        'is_sales_item': 1
    }).insert(ignore_permissions=True)

    return item.item_code


def create_test_payment_plan_simple():
    """
    Create a simple Payment Plan without penalties for basic testing scenarios.

    Returns:
        dict: {
            'customer': Customer document name,
            'payment_plan': Payment Plan document name
        }
    """

    # Create test data using the main factory function but return minimal structure
    test_data = create_test_payment_plan_with_penalties()

    # Get the payment plan and remove penalties for simple testing
    payment_plan = frappe.get_doc('Payment Plan', test_data['payment_plan'])

    # Clear penalty amounts for simple scenario
    for installment in payment_plan.installments:
        installment.penalty_amount = 0

    payment_plan.save()

    return {
        'customer': test_data['customer'],
        'payment_plan': payment_plan.name
    }


def _generate_installments(finance_app):
    """Generate installments for Finance Application"""
    if not finance_app.repayment_term or not finance_app.first_installment:
        return

    # Calculate installment amount (simple calculation for factory)
    financed_amount = finance_app.total_amount_to_finance - finance_app.down_payment_amount
    monthly_installment = financed_amount / finance_app.repayment_term

    # Clear existing installments
    finance_app.installments = []

    # Generate installments
    for i in range(finance_app.repayment_term):
        due_date = frappe.utils.add_months(finance_app.first_installment, i)
        finance_app.append('installments', {
            'due_date': due_date,
            'amount': monthly_installment
        })


def _create_test_credit_invoice(finance_app):
    """Create a test credit invoice for the finance application"""
    credit_invoice = frappe.get_doc({
        'doctype': 'Sales Invoice',
        'customer': finance_app.customer,
        'posting_date': frappe.utils.today(),
        'due_date': frappe.utils.add_days(frappe.utils.today(), 30),
        'custom_is_credit_invoice': True,
        'custom_finance_application': finance_app.name,
        'items': [{
            'doctype': 'Sales Invoice Item',
            'item_code': 'Test Credit Item',
            'item_name': 'Test Credit Item',
            'qty': 1,
            'rate': finance_app.total_amount_to_finance,
            'amount': finance_app.total_amount_to_finance
        }]
    })

    # Create test item if it doesn't exist
    if not frappe.db.exists('Item', 'Test Credit Item'):
        frappe.get_doc({
            'doctype': 'Item',
            'item_code': 'Test Credit Item',
            'item_name': 'Test Credit Item',
            'item_group': 'Products',
            'stock_uom': 'Nos',
            'is_sales_item': 1
        }).insert(ignore_permissions=True)

    credit_invoice.insert(ignore_permissions=True)
    credit_invoice.submit()
    return credit_invoice


def _create_test_payment_plan(finance_app, credit_invoice_name):
    """Create a test payment plan from finance application (replicates create_payment_plan pattern)"""
    plan = frappe.get_doc({
        'doctype': 'Payment Plan',
        'finance_application': finance_app.name,
        'customer': finance_app.customer,
        'credit_invoice': credit_invoice_name,
        'down_payment_amount': finance_app.down_payment_amount,
        'paid_down_payment_amount': 0,
        'pending_down_payment_amount': finance_app.down_payment_amount
    })

    # Add installments from finance application
    for installment in finance_app.installments:
        plan.append('installments', {
            'due_date': frappe.utils.getdate(installment.due_date),  # Ensure proper date conversion
            'amount': installment.amount,
            'paid_amount': 0,
            'pending_amount': installment.amount,
            'penalty_amount': 0  # Will be set later by the main function
        })

    plan.insert(ignore_permissions=True)
    plan.submit()
    return plan
