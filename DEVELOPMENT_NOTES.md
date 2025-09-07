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
- Use `custom_financed_items` field name for financed items tables
- Set `"modified"` to current date/time for easy identification in UI (use: `date '+%Y-%m-%d %H:%M:%S.%6N'`)

## Interest Implementation
- **Factura Proforma**: Modify existing `items` table with financed rates
- **Sales Order/Invoice**: Add `custom_items_with_interest` table, keep original items + tax
- **Distribution**: Proportional allocation with banker's rounding
