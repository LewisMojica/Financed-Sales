"""Factory for creating cancelled Payment Plans with overdue installments."""
import frappe
from .overdue import create_overdue_payment_plan


def create_cancelled_overdue_payment_plan():
    """
    Create a cancelled Payment Plan with overdue installments and penalties.

    Leverages create_overdue_payment_plan() and cancels the Payment Plan.
    Reproduces the bug where cancelled plans appear in Overdue Financed Sales page.

    Returns:
        dict: Same as create_overdue_payment_plan(), but Payment Plan has docstatus=2
    """
    result = create_overdue_payment_plan()

    # Cancel the Payment Plan
    payment_plan = frappe.get_doc('Payment Plan', result['payment_plan'])
    payment_plan.cancel()

    return result
