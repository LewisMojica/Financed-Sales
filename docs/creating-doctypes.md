# Creating DocTypes Programmatically

## Overview

This guide covers how to create new DocTypes programmatically in a Frappe app using `bench import-doc`.

## Required Structure

To create a DocType using `bench import-doc`, you must create the complete module structure:

```
apps/app_name/module_name/doctype/doctype_name/
├── __init__.py
├── doctype_name.py
└── doctype_name.json
```

Example for financed_sales app:
```
apps/financed_sales/financed_sales/doctype/my_doctype/
├── __init__.py
├── my_doctype.py
└── my_doctype.json
```

## Step-by-Step Process

### 1. Create Directory Structure
```bash
mkdir -p financed_sales/financed_sales/doctype/my_doctype
```

### 2. Create `__init__.py`
```python
# Empty file - required for Python module
```

### 3. Create Python Class File (`my_doctype.py`)
```python
# Copyright (c) 2025, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MyDocType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		naming_series: DF.Select
		title: DF.Data
		description: DF.Text | None
	# end: auto-generated types

	pass
```

### 4. Create JSON Definition (`my_doctype.json`)
```json
{
 "actions": [],
 "allow_copy": 0,
 "allow_events_in_timeline": 0,
 "allow_guest_to_view": 0,
 "allow_import": 0,
 "allow_rename": 1,
 "autoname": "naming_series:",
 "beta": 0,
 "creation": "2025-01-15 10:00:00.000000",
 "custom": 0,
 "docstatus": 0,
 "doctype": "DocType",
 "document_type": "Document",
 "engine": "InnoDB",
 "field_order": [
  "naming_series",
  "title",
  "description"
 ],
 "fields": [
  {
   "fieldname": "naming_series",
   "fieldtype": "Select",
   "label": "Series",
   "options": "MY-.YYYY.-",
   "reqd": 1
  },
  {
   "fieldname": "title",
   "fieldtype": "Data",
   "label": "Title",
   "reqd": 1
  },
  {
   "fieldname": "description",
   "fieldtype": "Text",
   "label": "Description"
  }
 ],
 "icon": "fa fa-file",
 "idx": 0,
 "is_submittable": 0,
 "is_virtual": 0,
 "issingle": 0,
 "istable": 0,
 "max_attachments": 0,
 "modified": "2025-01-15 10:00:00.000000",
 "modified_by": "Administrator",
 "module": "Financed Sales",
 "name": "My DocType",
 "naming_rule": "By \"Naming Series\" field",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  }
 ],
 "quick_entry": 0,
 "read_only": 0,
 "read_only_onload": 0,
 "show_name_in_global_search": 0,
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "track_changes": 1,
 "track_seen": 0,
 "track_views": 0
}
```

### 5. Import the DocType
```bash
bench --site [site-name] import-doc apps/financed_sales/financed_sales/doctype/my_doctype/my_doctype.json
```

## Why Complete Structure is Required

When `bench import-doc` imports a DocType definition:
1. Creates the DocType in the database ✅
2. Calls `on_update()` which tries to load the Python module ❌ (fails without proper structure)

The error without proper structure:
```
ModuleNotFoundError: No module named 'financed_sales.financed_sales.doctype.my_doctype'
```

## Import Permissions

**IMPORTANT**: If you set `"import": 1` in any role permissions, you MUST also set `"allow_import": 1` at the DocType level, otherwise the import will fail with validation error:

```
Cannot set import as DocType(Your DocType) is not importable
```

Example with import enabled:
```json
{
 "allow_import": 1,
 "permissions": [
  {
   "import": 1,
   "role": "Your Role"
  }
 ]
}
```

## Field Types Reference

Common field types for JSON definition:
- `Data`: Short text (< 140 chars)
- `Text`: Long text
- `Select`: Dropdown with options
- `Link`: Reference to another DocType
- `Table`: Child table
- `Check`: Boolean checkbox
- `Date`, `Datetime`: Date fields
- `Currency`, `Float`, `Int`: Numeric fields

## Naming Conventions

- **DocType names**: PascalCase (e.g., "My DocType")
- **Fieldnames**: snake_case (e.g., "my_field")
- **Module names**: snake_case (e.g., "financed_sales")
- **File names**: snake_case (e.g., "my_doctype.py")

## Testing DocType Creation

Verify the DocType was created:
```bash
bench --site [site-name] console
```
```python
import frappe
print('DocType exists:', frappe.db.exists('DocType', 'My DocType'))
```

## Modifying Existing DocTypes

For core DocTypes (owned by your app):
1. Edit the JSON file directly
2. Run: `bench --site [site-name] import-doc path/to/doctype.json`
3. Clear cache

Alternative: Use `bench --site [site-name] migrate` which processes all changes automatically.
