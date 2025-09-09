# Creating Frappe Pages

This document explains how to create custom pages in Frappe/ERPNext apps, based on the sales funnel pattern.

## Overview

Frappe pages are custom web interfaces that provide specialized views and functionality beyond standard DocTypes. They consist of multiple files working together to create a complete user interface.

## File Structure

A Frappe page requires these files in the directory `{app_name}/{app_name}/page/{page_name}/`:

```
page_name/
├── __init__.py                 # Python module file (empty)
├── page_name.json             # Page metadata and configuration
├── page_name.js               # Frontend JavaScript logic
├── page_name.py               # Backend Python API methods
└── page_name.css              # Optional styling
```

## Step-by-Step Implementation

### 1. Create Directory Structure

```bash
mkdir -p {app_name}/{app_name}/page/{page_name}
```

### 2. Create Page Metadata (JSON)

File: `page_name.json`

```json
{
 "creation": "YYYY-MM-DD HH:MM:SS.microseconds",
 "docstatus": 0,
 "doctype": "Page",
 "icon": "fa fa-icon-name",
 "idx": 1,
 "modified": "YYYY-MM-DD HH:MM:SS.microseconds",
 "modified_by": "Administrator",
 "module": "Your Module Name",
 "name": "page-slug",
 "owner": "Administrator",
 "page_name": "page-slug",
 "roles": [
  {
   "role": "System Manager"
  }
 ],
 "standard": "Yes",
 "title": "Page Display Title"
}
```

**Important**: Use `date '+%Y-%m-%d %H:%M:%S.%6N'` for timestamp format.

### 3. Create Frontend JavaScript (JS)

File: `page_name.js`

```javascript
frappe.pages["page-slug"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Page Title"),
		single_column: true,
	});

	wrapper.page_instance = new YourApp.PageClass(wrapper);
	frappe.breadcrumbs.add("Module Name");
};

YourApp.PageClass = class PageClass {
	constructor(wrapper) {
		var me = this;
		setTimeout(function () {
			me.setup(wrapper);
			me.get_data();
		}, 0);
	}

	setup(wrapper) {
		// Add filters and UI elements
		this.company_field = wrapper.page.add_field({
			fieldtype: "Link",
			fieldname: "company",
			options: "Company",
			label: __("Company"),
			reqd: 1,
			default: frappe.defaults.get_user_default("company"),
			change: function () {
				me.company = this.value;
				me.get_data();
			},
		});

		// Add refresh button
		this.refresh_btn = wrapper.page.set_primary_action(
			__("Refresh"),
			function () { me.get_data(); },
			"fa fa-refresh"
		);
	}

	get_data(btn) {
		frappe.call({
			method: "app_name.app_name.page.page_name.page_name.method_name",
			args: {
				company: this.company,
			},
			btn: btn,
			callback: function (r) {
				if (!r.exc) {
					me.data = r.message;
					me.render();
				}
			},
		});
	}

	render() {
		// Render your UI here
	}
};
```

### 4. Create Backend Python (PY)

File: `page_name.py`

```python
# Copyright (c) YEAR, Your Name and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _


@frappe.whitelist()
def method_name(company):
	"""Your method description."""
	if not company:
		frappe.throw(_("Please select a company"))

	# Your implementation here
	return []
```

### 5. Create Styling (CSS) - Optional

File: `page_name.css`

```css
.your-page-wrapper {
	margin: 15px;
	width: 100%;
}
```

### 6. Create Python Module File

File: `__init__.py`

```python
# Empty __init__.py file
```

## Import Page into Database

After creating all files, import the page into the database:

```bash
# Activate virtual environment
source ~/frappe-env/bin/activate

# Import page into database
bench --site [site-name] import-doc apps/{app_name}/{app_name}/{app_name}/page/{page_name}/{page_name}.json

# Build frontend (MANDATORY after JavaScript changes)
bench --site [site-name] build --app {app_name}
```

## Access Your Page

The page will be available at:
- URL: `http://site-url:port/app/page-slug`
- Search in Awesome Bar for the page title
- Access from the module workspace

## Key Patterns

### UI Elements
- **Filters**: Use `wrapper.page.add_field()` for form controls
- **Buttons**: Use `wrapper.page.set_primary_action()` for main actions
- **Layout**: Access main content area via `$(wrapper).find(".layout-main")`

### Data Flow
1. JavaScript calls Python method via `frappe.call()`
2. Python method processes data and returns JSON
3. JavaScript receives data in callback and renders UI

### Error Handling
- Python: Use `frappe.throw(_("Error message"))` for user errors
- JavaScript: Check `!r.exc` in callback before processing data

## Best Practices

1. **Timestamps**: Always use current timestamp format for `creation` and `modified`
2. **Permissions**: Set appropriate roles in JSON file
3. **Module**: Set correct module name for organization
4. **Frontend Build**: Always run `bench build` after JavaScript changes
5. **Error Messages**: Use translatable strings with `_()` and `__()`
6. **Responsive**: Handle window resize events if needed
7. **Loading States**: Show loading indicators during API calls

## Example: Sales Funnel Reference

See the ERPNext sales funnel page at:
`apps/erpnext/erpnext/selling/page/sales_funnel/`

This provides a complete reference implementation with charts, filters, and multiple data views.