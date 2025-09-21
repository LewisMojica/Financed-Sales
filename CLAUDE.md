# CLAUDE.md

@Context.md

## Project Overview

This is a Frappe/ERPNext app called "Financed Sales" that enables customer financed sales workflows. It allows creating financing applications from quotations and POS transactions with structured payment plans, including down payments, installments, and interest calculations.

## Documentation
For additional documentation, see docs/ directory. Use `ls docs/` to see available files, then choose the relevant one - this avoids bloating context with unnecessary files.

## Essential Commands

### Environment Setup
```bash
# Make sure the venv is active, as the bench command in the the venv.
source ~/frappe-env/bin/activate

# After editing a Doctype by its json file do this to update the database (UI won't show the changes if not done)
bench --site dev.localhost import-doc apps/financed_sales/financed_sales/fixtures/custom_field.json
```

### Frontend Development
```bash
# MANDATORY after EVERY JavaScript change - build the frontend
source ~/frappe-env/bin/activate && bench --site dev.localhost build --app financed_sales
```


## Development Conventions

### Custom Fields
- Always set `"module": "Financed Sales"` in custom field JSON
- Set `"modified"` to current timestamp for UI identification

### Version Management
- Update version in `financed_sales/__init__.py` for production tracking
- Bug fixes: bump patch version (0.21.0 → 0.21.1)
- New features: bump minor version (0.21.0 → 0.22.0)
- **Always bump version immediately after implementing new features**

### Commit Messages
- **Verify branch**: run `git branch` before `git add` if the branch name seems sus ask for confirmation.
- **Must use conventional commit format**: `type(scope): description`
- **Verify Changes**: Always check `git diff` before committing to ensure commit message accurately describes actual changes
- Don't pile many changes for a single commit. 
- Commit changes before starting unrelated work. 
- **Don't use Claude Code attribution** 
### Guideline for Docstrings (Google Style): When to Write Docstrings
- **Public Functions/Methods**: All functions intended for use by other parts of the codebase.
- **Classes**: Every class definition.
- **Modules**: Add a docstring at the top of each file explaining its purpose.
- **Complex Private Functions**: Any non-trivial helper function where the purpose or logic is not immediately obvious.

### Data Handling
- Pre-fill fields with likely values to improve user experience

### Frappe/ERPNext Specifics
- Table column visibility: Use `"in_list_view": 1` on child doctype fields, NOT `default_columns` on parent
- If documentation is missing/wrong the source code is the most reliable source of truth.
	Source code of the Frappe framework: `/home/slart/frappe-env/dev-env/apps/frappe/`
	Source code of ERPNext: `/home/slart/frappe-env/dev-env/apps/erpnext/`

### Core vs External DocTypes
**Core DocTypes (owned by this app)**: Finance Application, Payment Plan, Factura Proforma, Financed Sales Settings, etc.
- Edit directly in JSON files: `financed_sales/financed_sales/doctype/[doctype_name]/[doctype_name].json`
- Modify any property (permissions, fields, options, etc.) directly in the JSON
- Changes applied via: `bench --site dev.localhost import-doc [json file path]`

**External DocTypes (from Frappe/ERPNext)**: Quotation, Sales Order, Sales Invoice, etc.
- Use Property Setter documents to modify any doctype property
- Create via debug scripts for permissions, field properties, etc.
- Add Property Setter to fixtures if needed for deployment
- Cannot edit their JSON files as they belong to other apps


