# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Frappe/ERPNext app called "Financed Sales" that enables customer financed sales workflows. It allows creating financing applications from quotations and POS transactions with structured payment plans, including down payments, installments, and interest calculations.

## Essential Commands

### Environment Setup
```bash
# Always activate the virtual environment first
source ~/frappe-env/bin/activate

# Import custom fields after making changes
bench --site [site-name] import-doc apps/financed_sales/financed_sales/fixtures/custom_field.json
bench --site [site-name] clear-cache
```

### Frontend Development
```bash
# MANDATORY after EVERY JavaScript change - build the frontend
source ~/frappe-env/bin/activate && bench --site [site-name] build --app financed_sales
```

### Code Quality
```bash
# Pre-commit hooks (configured in .pre-commit-config.yaml)
pre-commit install
pre-commit run --all-files

# Ruff linting and formatting (configured in pyproject.toml)
ruff check
ruff format
```

## Architecture Overview

### Core Workflow
The financed sales process follows this workflow:
```
Quotation → Finance Application [Submission] → Sales Order → Finance Application [Approval] → Credit Invoice + Payment Plan [status = active] → Receive Payments
```

### Key DocTypes
- **Finance Application**: Main financing document with approval workflow
- **Payment Plan**: Manages installment schedules and payment tracking  
- **Factura Proforma**: Custom invoice format for financed sales
- **Financed Sales Settings**: Global configuration for interest rates, down payments

### Event Hooks (hooks.py)
- **Finance Application**: `on_update` and `on_update_after_submit` trigger document creation on approval
- **Payment Entry**: `on_submit` triggers payment allocation to installments

### JavaScript Integration
- **Point of Sale**: `public/js/point_of_sale.js` 
- **Quotation**: `public/js/quotation.js`
- **Finance Application**: `public/js/finance_application.js`

## Development Conventions

### Custom Fields
- Always set `"module": "Financed Sales"` in custom field JSON
- Use `custom_financed_items` for financed items tables
- Set `"modified"` to current timestamp for UI identification

### Version Management
- Update version in `financed_sales/__init__.py` for production tracking
- Bug fixes: bump patch version (0.21.0 → 0.21.1)
- New features: bump minor version (0.21.0 → 0.22.0)
- **Always bump version immediately after implementing new features**

### Commit Messages
- **Must use conventional commit format**: `type(scope): description`
- Examples: `feat: add custom fields`, `fix: payment allocation bug`, `docs: update notes`
- **Don't create commit summary messages after commits** - the git output shows what was committed
- **Don't use Claude Code attribution** - just use the conventional commit format without additional attribution text

### Data Handling
- Preserve original field values when transforming data
- Use proportional allocation with banker's rounding for interest distribution
- Pre-fill fields with likely values to improve user experience

### Frappe/ERPNext Specifics
- Table column visibility: Use `"in_list_view": 1` on child doctype fields, NOT `default_columns` on parent
- Check source code in `/home/slart/frappe-env/dev-env/apps/frappe/` and `/home/slart/frappe-env/dev-env/apps/erpnext/` for unclear documentation
- Frontend changes require building with `bench build --app financed_sales`

### Core vs External DocTypes
**Core DocTypes (owned by this app)**: Finance Application, Payment Plan, Factura Proforma, Financed Sales Settings, etc.
- Edit directly in JSON files: `financed_sales/financed_sales/doctype/[doctype_name]/[doctype_name].json`
- Modify any property (permissions, fields, options, etc.) directly in the JSON
- Changes applied via: `bench --site [site-name] migrate`

**External DocTypes (from Frappe/ERPNext)**: Quotation, Sales Order, Sales Invoice, etc.
- Use Property Setter documents to modify any doctype property
- Create via debug scripts for permissions, field properties, etc.
- Add Property Setter to fixtures if needed for deployment
- Cannot edit their JSON files as they belong to other apps

### Debugging with bench execute
For faster debugging than console copy-paste, create debug scripts in the `financed_sales/debug/` directory:

```python
# Create file: financed_sales/debug/debug_[feature].py
def debug_function():
    import frappe
    # Your debug code here
    print("Debug output")
```

Execute with:
```bash
bench --site [site-name] execute "financed_sales.debug.debug_[feature].debug_function"
```

**Debug Directory Structure:**
```
financed_sales/
├── debug/                    # Ignored by git
│   ├── README.md            # Debug patterns and examples
│   ├── debug_penalty.py     # Penalty calculation debugging
│   └── debug_[feature].py   # Feature-specific debugging
```

**Benefits:**
- Immediate execution and output
- No interactive session management needed  
- Can include complex multi-step debugging logic
- Full access to Frappe context and database
- Organized and reusable debug scripts
- Debug files ignored by git for clean repository

### Fixtures Management
Fixtures are used to bring document instances (roles, custom fields, workflows, etc.) to environments where the app is installed. They ensure required documents are created automatically when the app is installed.

**Creating fixtures workflow:**
1. Create the document in database using debug scripts (for roles, custom fields, etc.)
2. Add fixture definition to `hooks.py` fixtures array
3. Export fixtures to JSON files: `bench --site [site-name] export-fixtures --app financed_sales`

**Re-export fixtures when needed:**
```bash
# Only needed after updating documents that are defined as fixtures in hooks.py AND you want the JSON to update
bench --site [site-name] export-fixtures --app financed_sales
```

**Fixture types in this app:**
- **Custom Fields**: Auto-exported with module filter
- **Roles**: Custom roles for permission management (`Financed Sales Manager`, `Financed Sales User`)
- **Workflows**: Finance Application approval process
- **Print Formats**: Custom invoice formats
- **Workflow States**: Workflow state definitions

## Key Implementation Details

### Interest Implementation
- **Factura Proforma**: Modifies existing `items` table with financed rates
- **Sales Order/Invoice**: Adds `custom_items_with_interest` table, preserves original items + tax

### Payment Processing
- Sequential installment payment allocation
- Down payment must be completed before installments
- Automatic Payment Entry creation with proper account allocation
- Reference number validation for Wire Transfer/Credit Card payments

### Workflow States
- **Finance Application**: Draft → Pending → Approved/Rejected
- Automatic document creation triggered by state transitions