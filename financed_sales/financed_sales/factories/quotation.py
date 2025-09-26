import frappe
import uuid
from frappe.utils import today, add_days


def create_test_quotation_for_financing():
    """
    Create a submitted quotation ready for finance application creation.

    Replicates UI workflow: Customer creation → Quotation creation with items → Submit quotation

    Returns:
        dict: {
            'customer': Customer document name,
            'quotation': Quotation document name
        }
    """
    # Create unique customer to avoid conflicts
    unique_suffix = str(uuid.uuid4())[:8]
    customer_name = f"Test Customer {unique_suffix}"

    # Use existing test customer if available, otherwise create minimal customer
    if frappe.db.exists('Customer', '_Test Customer'):
        customer_name = '_Test Customer'
    else:
        customer = frappe.get_doc({
            'doctype': 'Customer',
            'customer_name': customer_name,
            'customer_type': 'Individual',
            'customer_group': 'All Customer Groups',
            'territory': 'All Territories'
        }).insert(ignore_permissions=True)
        customer_name = customer.name

    # Ensure test item exists
    test_item_code = 'Test Financed Item'
    if not frappe.db.exists('Item', test_item_code):
        frappe.get_doc({
            'doctype': 'Item',
            'item_code': test_item_code,
            'item_name': test_item_code,
            'item_group': 'All Item Groups',
            'stock_uom': 'Nos',
            'is_stock_item': 0  # Service item for simplicity
        }).insert(ignore_permissions=True)

    # Create quotation following UI workflow pattern (same as POS workflow in api.py)
    quotation = frappe.get_doc({
        'doctype': 'Quotation',
        'party_name': customer_name,
        'transaction_date': today(),
        'valid_till': add_days(today(), 30),
        'items': [{
            'doctype': 'Quotation Item',
            'item_code': test_item_code,
            'qty': 2,
            'rate': 15000  # Realistic amount for financing (30,000 total)
        }]
    }).insert(ignore_permissions=True)

    # Submit quotation (required for finance application creation)
    quotation.submit()

    return {
        'customer': customer_name,
        'quotation': quotation.name
    }

