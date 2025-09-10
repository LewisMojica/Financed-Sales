# Workspace Visibility Quirk in Frappe

## Problem

Frappe workspaces have a non-intuitive visibility system that requires specific configuration to work properly. Simply adding roles to a workspace doesn't guarantee users with those roles will see it.

## Root Cause

Based on research and [GitHub Issue #28119](https://github.com/frappe/frappe/issues/28119), Frappe workspace visibility depends on **both** workspace roles AND module doctype permissions.

## Solution

To make a workspace visible to specific roles, you need **TWO** configurations:

### 1. Workspace Roles Configuration

In your workspace JSON file (`financed_sales.json`):

```json
{
  "roles": [
    {
      "role": "Sales User"
    },
    {
      "role": "Sales Manager"
    }
  ]
}
```

### 2. Module DocType Requirements

**Critical Steps**: Create a DocType with these **exact** specifications:

1. **DocType Name**: Must match your module name exactly ("Financed Sales")
2. **Module Field**: Must be set to "Financed Sales" 
3. **Permissions**: Must include the same roles as the workspace

Example DocType JSON structure:
```json
{
  "doctype": "DocType",
  "module": "Financed Sales",
  "name": "Financed Sales",
  "permissions": [
    {
      "role": "Sales User",
      "read": 1
    },
    {
      "role": "Sales Manager", 
      "read": 1
    },
    {
      "role": "System Manager",
      "read": 1
    }
  ]
}
```

### File Structure

```
financed_sales/
├── doctype/
│   └── financed_sales/              # DocType with same name as module
│       ├── financed_sales.json      # module: "Financed Sales"
│       └── financed_sales.py        # permissions: same roles as workspace
└── workspace/
    └── financed_sales/
        └── financed_sales.json      # roles: same as doctype permissions
```

## Why This Happens

Frappe checks **both**:
1. Whether the user has permission to access the workspace (workspace roles)
2. Whether the user has permission to access the module (module doctype permissions)

The module doctype acts as a "gatekeeper" for the entire module's visibility.

## Alternative Solution

From GitHub Issue #28119, you can also set workspace roles to empty array `[]` to make it accessible to all users:

```json
{
  "roles": []
}
```

This follows the pattern used by core ERPNext workspaces like "Selling".

## Debugging Steps

If workspace still doesn't appear:

1. **Check workspace roles**: Verify roles in workspace JSON
2. **Check module doctype exists**: Must have exact same name as module
3. **Check module field**: DocType module must be "Financed Sales"
4. **Check doctype permissions**: Verify user roles have Read permission  
5. **Clear cache**: `bench --site [site-name] clear-cache`
6. **Reload**: Hard refresh browser (Ctrl+F5)
7. **Check user roles**: Verify user actually has the assigned roles

## Implementation Example

For the Financed Sales module:

```bash
# 1. Create/verify DocType exists
# File: financed_sales/doctype/financed_sales/financed_sales.json
# Ensure: "module": "Financed Sales"

# 2. Update workspace roles  
# File: financed_sales/workspace/financed_sales/financed_sales.json

# 3. Clear cache
bench --site dev.localhost clear-cache

# 4. Restart server if needed
bench restart
```

## Related Links

- [Frappe GitHub Issue #28119](https://github.com/frappe/frappe/issues/28119)
- [Frappe Workspace Documentation](https://frappeframework.com/docs/user/en/desk/workspace)

This quirk affects all custom Frappe apps and is a common source of confusion for developers.

## Research Notes

**Further Investigation Needed**: The exact requirements may be simpler than initially thought. It's possible that:

1. **Any DocType** with `"module": "Financed Sales"` may satisfy the requirement (not necessarily one with the same name)
2. **Core modules** like ERPNext "Selling" may work differently and use existing DocTypes within that module
3. The **module field** may be the key requirement, not the DocType name matching

This theory could explain how core ERPNext workspaces function, as they likely rely on existing DocTypes within their respective modules rather than creating dedicated DocTypes with matching names.

**Testing Needed**:
- Try using existing DocTypes (like "Finance Application") with correct module field
- Analyze core ERPNext workspace configurations
- Test minimal DocType requirements for workspace visibility

This documentation will be updated as more research is conducted.