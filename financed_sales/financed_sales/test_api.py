import json
import unittest

import frappe

from .api import create_finance_app_from_pos_cart, create_finance_application
from .factories import create_test_quotation_for_financing


class TestAPI(unittest.TestCase):

    def test_create_finance_app_from_pos_cart_validation_no_customer(self):
        """Test that function throws error when no customer is provided"""

        items = json.dumps([{"item_code": "Test Item", "qty": 1, "rate": 100}])

        with self.assertRaises(frappe.ValidationError):
            create_finance_app_from_pos_cart(customer=None, items=items)

    def test_create_finance_app_from_pos_cart_validation_empty_customer(self):
        """Test that function throws error when empty customer is provided"""

        items = json.dumps([{"item_code": "Test Item", "qty": 1, "rate": 100}])

        with self.assertRaises(frappe.ValidationError):
            create_finance_app_from_pos_cart(customer="", items=items)

    def test_create_finance_app_from_pos_cart_validation_no_items(self):
        """Test that function throws error when no items provided"""

        with self.assertRaises((frappe.ValidationError, TypeError)):
            create_finance_app_from_pos_cart(customer="Test Customer", items=None)

    def test_create_finance_app_from_pos_cart_validation_empty_items(self):
        """Test that function throws error when empty items list provided"""

        items = json.dumps([])

        with self.assertRaises(frappe.ValidationError):
            create_finance_app_from_pos_cart(customer="Test Customer", items=items)

    def test_create_finance_application_success(self):
        """Test that create_finance_application successfully creates finance application from quotation"""

        # Use data factory to create test quotation
        test_data = create_test_quotation_for_financing()
        quotation_name = test_data['quotation']

        # Execute function under test
        result = create_finance_application(quotation_name)

        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('name', result)
        self.assertIsNotNone(result['name'])

        # Verify finance application was actually created
        finance_app_name = result['name']
        self.assertTrue(frappe.db.exists('Finance Application', finance_app_name))

        # Verify finance application has correct data
        finance_app = frappe.get_doc('Finance Application', finance_app_name)
        self.assertEqual(finance_app.quotation, quotation_name)
        self.assertEqual(finance_app.customer, test_data['customer'])
        self.assertGreater(finance_app.total_amount_to_finance, 0)


