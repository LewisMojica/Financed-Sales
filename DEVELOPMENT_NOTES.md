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
- Use conventional commit messages: `type(scope): description` (e.g. `feat: add custom fields`, `docs: update notes`)
- Commit changes before starting unrelated work or when convenient to break into multiple commits
- Update version in `financed_sales/__init__.py` - Frappe uses this for production version tracking
- **Data Preservation**: When transforming data, preserve original field values instead of hardcoding defaults (avoid silent data corruption)

## Interest Implementation
- **Factura Proforma**: Modify existing `items` table with financed rates
- **Sales Order/Invoice**: Add `custom_items_with_interest` table, keep original items + tax
- **Distribution**: Proportional allocation with banker's rounding


## Guideline for Docstrings (Google Style): When to Write Docstrings

- **Public Functions/Methods**: All functions intended for use by other parts of the codebase.
- **Classes**: Every class definition.
- **Modules**: Add a docstring at the top of each file explaining its purpose.
- **Complex Private Functions**: Any non-trivial helper function where the purpose or logic is not immediately obvious.