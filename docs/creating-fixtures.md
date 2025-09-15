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

