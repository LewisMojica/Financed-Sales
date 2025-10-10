"""Factory for creating Quotations."""
import frappe
from .helpers import _get_or_create_test_customer, _get_default_company, _get_or_create_test_item


def create_quotation():
    """
    Create a submitted Quotation.

    Returns:
        dict: {
            'customer': Customer document name,
            'quotation': Quotation document name,
            'company': Company name
        }
    """
    customer = _get_or_create_test_customer()
    company = _get_default_company()
    item = _get_or_create_test_item()

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
            'rate': 50000
        }]
    }).insert(ignore_permissions=True)

    quotation.submit()

    return {
        'customer': customer,
        'quotation': quotation.name,
        'company': company
    }
