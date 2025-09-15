# Workspace Visibility in Frappe

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

**Critical Steps**: Create (or reuse)  a DocType with these specifications:

1. **Module Field**: Must be set to "Financed Sales" 
2. **Permissions**: Must include the same roles as the workspace

Example DocType JSON structure:
```json
{
  "doctype": "DocType",
  "module": "Financed Sales",
  "name": "Doctype Financed Sales",
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

## Alternative Solution [needs verification]

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

