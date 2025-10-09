"""Factory for creating Payment Plan with Factura Proforma."""
import frappe
import json
from .base import create_payment_plan


def create_payment_plan_with_factura():
    """
    Create a Payment Plan with a submitted Factura Proforma.

    Leverages create_payment_plan() and adds Factura Proforma creation.

    Returns:
        dict: {
            'customer': Customer document name,
            'quotation': Quotation document name,
            'finance_application': Finance Application document name,
            'factura_proforma': Factura Proforma document name,
            'payment_plan': Payment Plan document name,
            'company': Company name
        }
    """
    # Create Payment Plan using base factory
    result = create_payment_plan()

    # Get Finance Application
    finance_application = frappe.get_doc('Finance Application', result['finance_application'])

    # Create Factura Proforma
    factura_name = finance_application.create_factura_proforma()
    factura = frappe.get_doc('Factura Proforma', factura_name)

    # Submit Factura Proforma
    factura.submit()

    # Add factura to result
    result['factura_proforma'] = factura.name

    return result


def test_factory():
    """Test the factory and verify Payment Plan can be cancelled."""
    result = create_payment_plan_with_factura()

    # Verify cancellation works
    payment_plan = frappe.get_doc("Payment Plan", result['payment_plan'])
    factura = frappe.get_doc("Factura Proforma", result['factura_proforma'])

    test_result = {
        **result,
        'verification': {
            'payment_plan_docstatus': payment_plan.docstatus,
            'factura_docstatus': factura.docstatus,
            'finance_app_has_factura': bool(frappe.get_all(
                'Factura Proforma',
                filters={'finance_application': result['finance_application'], 'docstatus': 1},
                limit=1
            ))
        }
    }

    print(json.dumps(test_result, indent=2))
    return test_result
