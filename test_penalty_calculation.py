#!/usr/bin/env python3
"""
Test script for penalty calculation logic
Formula: penalty_amount = pending_amount * 0.05 * floor(months_overdue)
"""

from datetime import date
from dateutil.relativedelta import relativedelta
import sys
import os

# Add the app path to sys.path to import our modules
sys.path.insert(0, '/home/slart/frappe-env/dev-env/apps/financed_sales')

def calculate_months_overdue(due_date, today=None):
    """Calculate months overdue using the same logic as Payment Plan"""
    if today is None:
        today = date.today()
    
    months_diff = relativedelta(today, due_date)
    months_overdue = months_diff.years * 12 + months_diff.months
    return months_overdue

def calculate_penalty(pending_amount, due_date, today=None):
    """Calculate penalty using the same formula as Payment Plan"""
    if today is None:
        today = date.today()
    
    if due_date >= today or pending_amount <= 0:
        return 0
    
    months_overdue = calculate_months_overdue(due_date, today)
    penalty_amount = pending_amount * 0.05 * months_overdue
    return penalty_amount

def test_penalty_calculations():
    """Test various penalty calculation scenarios"""
    print("=== Penalty Calculation Test Cases ===\n")
    
    today = date(2025, 9, 10)  # Fixed test date
    
    test_cases = [
        {
            "name": "3.7 months overdue",
            "pending_amount": 1000,
            "due_date": date(2025, 5, 20),  # ~3.7 months ago
            "expected_months": 3,
            "expected_penalty": 150.0  # 1000 * 0.05 * 3
        },
        {
            "name": "Exactly 2 months overdue",
            "pending_amount": 500,
            "due_date": date(2025, 7, 10),  # exactly 2 months ago
            "expected_months": 2,
            "expected_penalty": 50.0  # 500 * 0.05 * 2
        },
        {
            "name": "Less than 1 month overdue",
            "pending_amount": 800,
            "due_date": date(2025, 8, 20),  # ~20 days ago
            "expected_months": 0,
            "expected_penalty": 0.0  # 800 * 0.05 * 0
        },
        {
            "name": "Future due date (no penalty)",
            "pending_amount": 1000,
            "due_date": date(2025, 10, 15),  # future date
            "expected_months": 0,  # No overdue months for future dates
            "expected_penalty": 0.0
        },
        {
            "name": "Fully paid (no penalty)",
            "pending_amount": 0,
            "due_date": date(2025, 5, 10),  # overdue but fully paid
            "expected_months": 4,
            "expected_penalty": 0.0  # No penalty if fully paid
        },
        {
            "name": "6 months overdue",
            "pending_amount": 2000,
            "due_date": date(2025, 3, 10),  # 6 months ago
            "expected_months": 6,
            "expected_penalty": 600.0  # 2000 * 0.05 * 6
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test {i}: {case['name']}")
        print(f"  Pending Amount: ${case['pending_amount']}")
        print(f"  Due Date: {case['due_date']}")
        print(f"  Test Date: {today}")
        
        months_overdue = calculate_months_overdue(case['due_date'], today)
        penalty = calculate_penalty(case['pending_amount'], case['due_date'], today)
        
        print(f"  Months Overdue: {months_overdue} (expected: {case['expected_months']})")
        print(f"  Penalty Amount: ${penalty:.2f} (expected: ${case['expected_penalty']:.2f})")
        
        months_ok = months_overdue == case['expected_months']
        penalty_ok = abs(penalty - case['expected_penalty']) < 0.01  # Allow for floating point precision
        
        if months_ok and penalty_ok:
            print("  ✅ PASS")
        else:
            print("  ❌ FAIL")
            if not months_ok:
                print(f"    Months mismatch: got {months_overdue}, expected {case['expected_months']}")
            if not penalty_ok:
                print(f"    Penalty mismatch: got ${penalty:.2f}, expected ${case['expected_penalty']:.2f}")
            all_passed = False
        
        print()
    
    print("=== Test Summary ===")
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return all_passed

if __name__ == "__main__":
    test_penalty_calculations()