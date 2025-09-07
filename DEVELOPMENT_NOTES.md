# Development Notes - Financed Sales

## Custom Fields
```bash
# Import custom fields
source [frappe-env-path]/bin/activate
bench --site [site-name] import-doc apps/financed_sales/financed_sales/fixtures/custom_field.json
bench --site [site-name] clear-cache
```

**Requirements:**
- Always set `"module": "Financed Sales"` in custom field JSON
- Use `custom_items_with_interest` field name for financed items tables

## Interest Implementation
- **Factura Proforma**: Modify existing `items` table with financed rates
- **Sales Order/Invoice**: Add `custom_items_with_interest` table, keep original items + tax
- **Distribution**: Proportional allocation with banker's rounding
