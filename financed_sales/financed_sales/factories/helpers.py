"""Helper functions for Payment Plan factories."""
import frappe
import uuid


def _ensure_financed_sales_settings():
    """Configure Financed Sales Settings with penalty income account."""
    settings = frappe.get_single("Financed Sales Settings")
    company = _get_or_create_test_company()

    penalty_account = _get_or_create_penalty_income_account(company)
    interests_account = _get_or_create_interests_income_account(company)

    settings.penalty_income_account = penalty_account
    settings.interests_account = interests_account

    if not settings.interest_rate:
        settings.interest_rate = 5.0
    if not settings.down_payment_percent:
        settings.down_payment_percent = 40.0
    if not settings.rate_period:
        settings.rate_period = 'Monthly'
    if not settings.application_fee:
        settings.application_fee = 1000

    settings.save()


def _get_or_create_test_customer():
    """Get existing test customer or create new one with unique name."""
    unique_suffix = str(uuid.uuid4())[:8]
    customer_name = f"Test Customer {unique_suffix}"

    customer = frappe.get_doc({
        'doctype': 'Customer',
        'customer_name': customer_name,
        'customer_type': 'Individual'
    }).insert(ignore_permissions=True)

    return customer.name


def _get_or_create_test_company():
    """Get the default company that has existing accounts and warehouses."""
    company_with_stores = frappe.db.get_value('Warehouse', 'Stores - S-C', 'company')
    if company_with_stores:
        return company_with_stores

    existing_companies = frappe.db.get_list('Company', fields=['name'], limit=1)
    if existing_companies:
        return existing_companies[0]['name']

    frappe.throw("No company found in system. Please create a company first.")


def _get_or_create_test_item():
    """Get existing test item that belongs to the default company."""
    company = _get_or_create_test_company()

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

    any_service_item = frappe.db.get_value('Item', {
        'is_sales_item': 1,
        'is_stock_item': 0
    }, 'item_code')

    if any_service_item:
        return any_service_item

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
    """Get or create penalty income account for the company."""
    existing_account = frappe.db.get_value('Account', {'account_name': 'Penalty Income', 'company': company})
    if existing_account:
        return existing_account

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
    """Get the parent income account for the company."""
    income_account = frappe.db.get_value('Account', {
        'company': company,
        'account_type': 'Income Account',
        'is_group': 1
    }, 'name')

    if income_account:
        return income_account

    root_income = frappe.db.get_value('Account', {
        'company': company,
        'root_type': 'Income',
        'is_group': 1
    }, 'name')

    if root_income:
        return root_income

    root_account = frappe.db.get_value('Account', {
        'company': company,
        'parent_account': '',
        'root_type': 'Income'
    }, 'name')

    if not root_account:
        root_account = frappe.get_doc({
            'doctype': 'Account',
            'account_name': 'Application of Funds (Income)',
            'is_group': 1,
            'root_type': 'Income',
            'report_type': 'Profit and Loss',
            'company': company
        }).insert(ignore_permissions=True).name

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
    """Get or create interests income account for the company."""
    existing_account = frappe.db.get_value('Account', {'account_name': 'Interests', 'company': company})
    if existing_account:
        return existing_account

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
