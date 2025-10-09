import frappe
import uuid
import json
from ..api import create_finance_application

def create_test_payment_plan_for_penalty_journal():
    """
    Create a complete Payment Plan with valid company and customer data for testing penalty journal entry creation.

    Follows UI workflow: Quotation → Finance Application → Submit → Approve → Payment Plan creation

    Returns:
        dict: {
            'customer': Customer document name,
            'quotation': Quotation document name,
            'finance_application': Finance Application document name,
            'payment_plan': Payment Plan document name,
            'company': Company name (accessed via quotation)
        }
    """

    # Step 1: Configure Financed Sales Settings with penalty account
    _ensure_financed_sales_settings()

    # Step 2: Handle dependencies - create customer, company, and item
    customer = _get_or_create_test_customer()
    company = _get_or_create_test_company()
    item = _get_or_create_test_item()

    # Step 3: Get company currency to avoid exchange rate issues
    company_currency = frappe.db.get_value('Company', company, 'default_currency')

    # Step 4: Create Quotation with realistic financing amount (following UI workflow)
    quotation = frappe.get_doc({
        'doctype': 'Quotation',
        'party_name': customer,
        'company': company,
        'currency': company_currency,
        'conversion_rate': 1.0,  # Same currency, no conversion needed
        'transaction_date': frappe.utils.today(),
        'valid_till': frappe.utils.add_days(frappe.utils.today(), 30),
        'items': [{
            'doctype': 'Quotation Item',
            'item_code': item,
            'qty': 1,
            'rate': 50000  # Realistic amount for financing that requires penalties
        }]
    }).insert(ignore_permissions=True)

    # Step 5: Submit quotation (required for finance applications)
    quotation.submit()

    # Step 6: Create Finance Application using API (replicates UI workflow)
    fin_app_result = create_finance_application(quotation.name)
    finance_application = frappe.get_doc('Finance Application', fin_app_result['name'])

    # Step 7: Set up payment terms for realistic penalty scenario
    finance_application.repayment_term = 12  # 12 months
    finance_application.first_installment = frappe.utils.add_days(frappe.utils.today(), 30)

    # Calculate and add installments (required for submission)
    amount_to_finance = finance_application.total_amount_to_finance - finance_application.down_payment_amount
    monthly_installment = amount_to_finance / finance_application.repayment_term

    # Add installments to meet validation requirements
    for i in range(finance_application.repayment_term):
        installment_date = frappe.utils.add_months(finance_application.first_installment, i)
        finance_application.append('installments', {
            'doctype': 'Financed Sale Installment',
            'installment_date': installment_date,
            'due_date': installment_date,  # Required by workflow
            'amount': monthly_installment
        })

    # Set workflow state to Pending before saving to trigger correct workflow
    finance_application.workflow_state = 'Pending'
    finance_application.save()

    # Step 8: Submit Finance Application (this should create Sales Order due to Pending state)
    finance_application.reload()  # Refresh to avoid timestamp mismatch
    finance_application.submit()

    # Step 9: Manually create Sales Order if not created by workflow
    if not finance_application.sales_order:
        from ..create_docs_on_approval import create_sales_order
        create_sales_order(finance_application)

    # Step 10: Set workflow state to Approved (creates Payment Plan + Credit Invoice)
    finance_application.reload()
    finance_application.db_set('workflow_state', 'Approved')

    # Manually trigger the approval workflow to create Payment Plan + Credit Invoice
    if not finance_application.payment_plan:
        from ..create_docs_on_approval import on_approval
        on_approval(finance_application)

    # Get the automatically created Payment Plan
    payment_plan_name = finance_application.payment_plan
    if not payment_plan_name:
        frappe.throw("Payment Plan was not created automatically after approval")

    # Step 11: Modify Payment Plan installments to have overdue dates and penalties
    payment_plan = frappe.get_doc('Payment Plan', payment_plan_name)

    # Update installment due dates to past dates (creating overdue scenario)
    # First installment was due 60 days ago
    overdue_start_date = frappe.utils.add_days(frappe.utils.today(), -60)

    # Add penalties to the first 3 overdue installments
    penalty_amounts = [500.0, 750.0, 1000.0]

    for i, installment in enumerate(payment_plan.installments):
        # Update due date to past date
        new_due_date = frappe.utils.add_months(overdue_start_date, i)

        # Set penalty for first 3 installments
        penalty = penalty_amounts[i] if i < len(penalty_amounts) else 0.0

        # Update via direct database update (since Payment Plan is submitted)
        frappe.db.set_value('Payment Plan Installment', installment.name, {
            'due_date': new_due_date,
            'penalty_amount': penalty,
            'pending_amount': installment.amount + penalty
        })

    frappe.db.commit()

    # Step 12: Cancel the Payment Plan to reproduce the bug
    payment_plan.reload()  # Reload to get fresh data
    payment_plan.cancel()

    return {
        'customer': customer,
        'quotation': quotation.name,
        'finance_application': finance_application.name,
        'payment_plan': payment_plan_name,
        'company': company
    }


def _ensure_financed_sales_settings():
    """Configure Financed Sales Settings with penalty income account"""
    settings = frappe.get_single("Financed Sales Settings")

    # Get the existing company to ensure account compatibility
    company = _get_or_create_test_company()

    # Always update accounts to match the current company - don't check if they exist
    penalty_account = _get_or_create_penalty_income_account(company)
    interests_account = _get_or_create_interests_income_account(company)

    settings.penalty_income_account = penalty_account
    settings.interests_account = interests_account

    # Set default values for other fields
    if not settings.interest_rate:
        settings.interest_rate = 5.0  # 5% monthly
    if not settings.down_payment_percent:
        settings.down_payment_percent = 40.0  # 40% down payment
    if not settings.rate_period:
        settings.rate_period = 'Monthly'
    if not settings.application_fee:
        settings.application_fee = 1000

    settings.save()


def _get_or_create_test_customer():
    """Get existing test customer or create new one with unique name and proper receivable account setup"""
    unique_suffix = str(uuid.uuid4())[:8]
    customer_name = f"Test Customer {unique_suffix}"

    customer = frappe.get_doc({
        'doctype': 'Customer',
        'customer_name': customer_name,
        'customer_type': 'Individual'
    }).insert(ignore_permissions=True)

    return customer.name


def _get_or_create_test_company():
    """Get the default company that has existing accounts and warehouses"""
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


def _get_or_create_test_item():
    """Get existing test item that belongs to the default company"""
    company = _get_or_create_test_company()

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


def _get_or_create_penalty_income_account(company):
    """Get or create penalty income account for the company"""
    # Check for existing penalty income account
    account_name = f"Penalty Income - {company}"
    existing_account = frappe.db.get_value('Account', {'account_name': 'Penalty Income', 'company': company})
    if existing_account:
        return existing_account

    # Create penalty income account
    account = frappe.get_doc({
        'doctype': 'Account',
        'account_name': 'Penalty Income',
        'account_type': 'Income Account',
        'root_type': 'Income',
        'report_type': 'Profit and Loss',
        'company': company,
        'parent_account': _get_income_parent_account(company)
    }).insert(ignore_permissions=True)

    return account.name


def _get_income_parent_account(company):
    """Get the parent income account for the company"""
    # Look for standard income accounts
    income_account = frappe.db.get_value('Account', {
        'company': company,
        'account_type': 'Income Account',
        'is_group': 1
    }, 'name')

    if income_account:
        return income_account

    # Look for any root Income account
    root_income = frappe.db.get_value('Account', {
        'company': company,
        'root_type': 'Income',
        'is_group': 1
    }, 'name')

    if root_income:
        return root_income

    # If no income account group exists, create one with proper parent
    # Get root Application of Funds account as parent
    root_account = frappe.db.get_value('Account', {
        'company': company,
        'parent_account': '',
        'root_type': 'Income'
    }, 'name')

    if not root_account:
        # Create root Income account first
        root_account = frappe.get_doc({
            'doctype': 'Account',
            'account_name': 'Application of Funds (Income)',
            'is_group': 1,
            'root_type': 'Income',
            'report_type': 'Profit and Loss',
            'company': company
        }).insert(ignore_permissions=True).name

    # Create Income group under root
    income_group = frappe.get_doc({
        'doctype': 'Account',
        'account_name': 'Income',
        'is_group': 1,
        'root_type': 'Income',
        'report_type': 'Profit and Loss',
        'company': company,
        'parent_account': root_account
    }).insert(ignore_permissions=True)

    return income_group.name


def _get_or_create_interests_income_account(company):
    """Get or create interests income account for the company"""
    # Check for existing interests income account
    existing_account = frappe.db.get_value('Account', {'account_name': 'Interests', 'company': company})
    if existing_account:
        return existing_account

    # Create interests income account
    account = frappe.get_doc({
        'doctype': 'Account',
        'account_name': 'Interests',
        'account_type': 'Income Account',
        'root_type': 'Income',
        'report_type': 'Profit and Loss',
        'company': company,
        'parent_account': _get_income_parent_account(company)
    }).insert(ignore_permissions=True)

    return account.name


def _get_or_create_default_income_account(company):
    """Get or create a default income account for items"""
    # Check for existing sales account
    existing_account = frappe.db.get_value('Account', {
        'company': company,
        'account_type': 'Income Account',
        'account_name': 'Sales'
    })
    if existing_account:
        return existing_account

    # Look for any income account for the company
    any_income_account = frappe.db.get_value('Account', {
        'company': company,
        'account_type': 'Income Account',
        'is_group': 0
    })
    if any_income_account:
        return any_income_account

    # Create a Sales income account
    sales_account = frappe.get_doc({
        'doctype': 'Account',
        'account_name': 'Sales',
        'account_type': 'Income Account',
        'root_type': 'Income',
        'report_type': 'Profit and Loss',
        'company': company,
        'parent_account': _get_income_parent_account(company)
    }).insert(ignore_permissions=True)

    return sales_account.name


def test_factory():
    """Create a Payment Plan and display the result in pretty JSON format."""
    result = create_test_payment_plan_for_penalty_journal()
    print(json.dumps(result, indent=2))
