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


def create_test_payment_plan_for_payment_entry():
    """
    Create a Payment Plan with installments that have penalties, configured Mode of Payment,
    and complete financed sales workflow for testing payment entry creation scenarios.

    Supports both single reference (principal only) and dual reference (principal + penalty) testing.

    Returns:
        dict: {
            'customer': Customer document name,
            'quotation': Quotation document name,
            'finance_application': Finance Application document name,
            'payment_plan': Payment Plan document name,
            'credit_invoice': Sales Invoice document name,
            'mode_of_payment': Mode of Payment document name,
            'company': Company name
        }
    """

    # Step 1: Get the existing company (use the working company logic from penalty_journal_factory)
    company = _get_existing_company()

    # Step 2: Ensure we have a configured Mode of Payment
    mode_of_payment = _get_or_create_test_mode_of_payment(company)

    # Step 3: Handle dependencies - create customer and item using existing company
    customer = _get_or_create_test_customer_fixed(company)
    item = _get_or_create_test_item_fixed(company)

    # Step 4: Create Quotation with realistic financing amounts
    company_currency = frappe.db.get_value('Company', company, 'default_currency')
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
            'rate': 50000  # $50,000 - realistic amount for financing with significant installments
        }]
    }).insert(ignore_permissions=True)

    # Step 5: Submit quotation (required for finance applications)
    quotation.submit()

    # Step 6: Create Finance Application from quotation (replicates UI workflow)
    finance_app_response = create_finance_application(quotation.name)
    finance_app = frappe.get_doc('Finance Application', finance_app_response['name'])

    # Step 7: Configure realistic financing terms
    finance_app.repayment_term = 6  # 6 months for easier testing
    finance_app.interest_rate = 8.0  # 8% monthly interest
    finance_app.first_installment = frappe.utils.add_days(frappe.utils.today(), 30)

    # Step 8: Generate installments (required for submission)
    _generate_installments_fixed(finance_app)
    finance_app.save()

    # Step 9: Submit Finance Application using workflow API (creates Sales Order automatically)
    from frappe.model.workflow import apply_workflow
    apply_workflow(finance_app, 'Submit')

    # Step 10: Approve Finance Application using workflow API (creates Payment Plan + Credit Invoice automatically)
    finance_app.reload()
    apply_workflow(finance_app, 'Approve')

    # Get the automatically created Payment Plan and Credit Invoice
    finance_app.reload()
    payment_plan = frappe.get_doc('Payment Plan', finance_app.payment_plan)
    credit_invoice = frappe.get_doc('Sales Invoice', finance_app.credit_invoice)

    # Step 11: Add realistic penalty amounts to some installments (simulates overdue scenarios)
    penalty_installments = [1, 3]  # Add penalties to installments 2 and 4 (0-indexed)
    penalty_amounts = [750, 1200]  # Realistic penalty amounts

    for i, penalty_amount in zip(penalty_installments, penalty_amounts):
        if i < len(payment_plan.installments):
            payment_plan.installments[i].penalty_amount = penalty_amount

    # Step 12: Save the Payment Plan with penalty amounts
    payment_plan.save()

    return {
        'customer': customer,
        'quotation': quotation.name,
        'finance_application': finance_app.name,
        'payment_plan': payment_plan.name,
        'credit_invoice': credit_invoice.name,
        'mode_of_payment': mode_of_payment,
        'company': company
    }


def _get_existing_company():
    """Get the default company that has existing accounts and warehouses (from penalty_journal_factory logic)"""
    # Look for the company that owns the "Stores - S-C" warehouse
    company_with_stores = frappe.db.get_value('Warehouse', 'Stores - S-C', 'company')
    if company_with_stores:
        return company_with_stores

    # Fallback to any existing company
    existing_companies = frappe.db.get_list('Company', fields=['name'], limit=1)
    if existing_companies:
        return existing_companies[0]['name']

    # If no company exists at all, this is a setup issue
    frappe.throw("No company found in system. Please create a company first.")


def _get_or_create_test_mode_of_payment(company):
    """Get or create a test Mode of Payment configured for the company"""
    # Check for existing cash mode of payment
    existing_mode = frappe.db.get_value('Mode of Payment', {'mode_of_payment': 'Cash'})
    if existing_mode:
        return existing_mode

    # Create a simple cash mode of payment if none exists
    mode_of_payment = frappe.get_doc({
        'doctype': 'Mode of Payment',
        'mode_of_payment': 'Cash',
        'accounts': [{
            'doctype': 'Mode of Payment Account',
            'company': company,
            'default_account': _get_or_create_cash_account(company)
        }]
    }).insert(ignore_permissions=True)

    return mode_of_payment.mode_of_payment


def _get_or_create_cash_account(company):
    """Get or create a cash account for the company"""
    # Look for existing cash account
    cash_account = frappe.db.get_value('Account', {
        'company': company,
        'account_type': 'Cash',
        'is_group': 0
    })
    if cash_account:
        return cash_account

    # Look for any asset account as fallback
    asset_account = frappe.db.get_value('Account', {
        'company': company,
        'root_type': 'Asset',
        'is_group': 0
    })
    if asset_account:
        return asset_account

    frappe.throw(f"No suitable cash/asset account found for company {company}")


def _get_or_create_test_customer_fixed(company):
    """Get existing test customer or create new one with unique name (company-aware)"""
    unique_suffix = str(uuid.uuid4())[:8]
    customer_name = f"Test Customer {unique_suffix}"

    customer = frappe.get_doc({
        'doctype': 'Customer',
        'customer_name': customer_name,
        'customer_type': 'Individual'
    }).insert(ignore_permissions=True)

    return customer.name


def _get_or_create_test_item_fixed(company):
    """Get existing test item that belongs to the company (from penalty_journal_factory logic)"""
    # Try to find an existing service item that works with this company
    existing_items = frappe.db.sql("""
        SELECT i.item_code
        FROM `tabItem` i
        LEFT JOIN `tabItem Default` id ON i.name = id.parent
        WHERE i.is_sales_item = 1
        AND i.is_stock_item = 0
        AND (id.company = %s OR i.name NOT IN (
            SELECT DISTINCT parent FROM `tabItem Default` WHERE company != %s
        ))
        LIMIT 1
    """, (company, company))

    if existing_items:
        return existing_items[0][0]

    # If no suitable existing item, just get any service item and let the system handle defaults
    any_service_item = frappe.db.get_value('Item', {
        'is_sales_item': 1,
        'is_stock_item': 0
    }, 'item_code')

    if any_service_item:
        return any_service_item

    # As last resort, create a simple service item without specific company defaults
    unique_suffix = str(uuid.uuid4())[:8]
    item_code = f"TEST-SERVICE-{unique_suffix}"

    item = frappe.get_doc({
        'doctype': 'Item',
        'item_code': item_code,
        'item_name': f'Test Service {unique_suffix}',
        'item_group': 'Services',
        'stock_uom': 'Nos',
        'is_sales_item': 1,
        'is_stock_item': 0,
        'is_purchase_item': 0
    }).insert(ignore_permissions=True)

    return item.item_code


def _generate_installments_fixed(finance_app):
    """Generate installments for Finance Application (fixed version)"""
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


def _create_test_credit_invoice_fixed(finance_app, company):
    """Create a test credit invoice for the finance application (company-aware)"""
    credit_invoice = frappe.get_doc({
        'doctype': 'Sales Invoice',
        'customer': finance_app.customer,
        'company': company,
        'posting_date': frappe.utils.today(),
        'due_date': frappe.utils.add_days(frappe.utils.today(), 30),
        'custom_is_credit_invoice': False,
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
            'item_group': 'Services',
            'stock_uom': 'Nos',
            'is_sales_item': 1,
            'is_stock_item': 0
        }).insert(ignore_permissions=True)

    credit_invoice.insert(ignore_permissions=True)
    credit_invoice.submit()
    return credit_invoice


def _create_test_payment_plan_fixed(finance_app, credit_invoice_name):
    """Create a test payment plan from finance application (fixed version)"""
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
