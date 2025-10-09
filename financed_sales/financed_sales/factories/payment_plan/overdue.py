"""Factory for creating Payment Plans with overdue installments and penalties."""
import frappe
from .base import create_payment_plan


def create_overdue_payment_plan():
    """
    Create a Payment Plan with overdue installments and penalties.

    Leverages create_payment_plan() and adds:
    - Past due dates (60 days ago for first installment)
    - Penalty amounts on first 3 installments

    Returns:
        dict: Same as create_payment_plan()
    """
    result = create_payment_plan()

    # Modify the Payment Plan to add overdue dates and penalties
    payment_plan = frappe.get_doc('Payment Plan', result['payment_plan'])

    # Set first installment to 60 days ago
    overdue_start_date = frappe.utils.add_days(frappe.utils.today(), -60)
    penalty_amounts = [500.0, 750.0, 1000.0]

    for i, installment in enumerate(payment_plan.installments):
        new_due_date = frappe.utils.add_months(overdue_start_date, i)
        penalty = penalty_amounts[i] if i < len(penalty_amounts) else 0.0

        frappe.db.set_value('Payment Plan Installment', installment.name, {
            'due_date': new_due_date,
            'penalty_amount': penalty,
            'pending_amount': installment.amount + penalty
        })

    frappe.db.commit()

    return result
