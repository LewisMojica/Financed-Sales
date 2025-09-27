# Frappe/ERPNext Development Guidelines

## Documentation Sources (Priority Order)

### 1. Local Project Documentation
**Location**: `/home/slart/frappe-env/dev-env/apps/financed_sales/docs/`

**Available Guides**:
- `creating-custom-fields.md` - Custom field creation patterns
- `creating-doctypes.md` - DocType creation and modification
- `creating-fixtures.md` - Fixture management for deployment
- `creating-frappe-pages.md` - Custom page development
- `financed-sales-user-journey.md` - App-specific user workflows
- `workspace-visibility.md` - Workspace configuration
- `frappe-console-alternative-for-debugging.md` - Debugging techniques

**Usage**: Check local docs first for app-specific patterns and established conventions.

### 2. Official Frappe Framework Documentation
**Base URL**: https://docs.frappe.io/framework/user/en/introduction

**Key Sections** (from sidebar navigation):
- **Basics**: Introduction, Installation, Tutorial
- **DocTypes**: Fields, Controllers, Forms, Lists, Permissions
- **Development**: API, Hooks, Client Scripting, Server Scripts
- **Database**: ORM, Migrations, Querying
- **Python API**: Database API, Document API, Utilities
- **JavaScript API**: Controls, Page, Dialog
- **Testing**: Unit Tests, Integration Tests
- **Deployment**: Production Setup, Updates

**Note**: May have gaps or outdated information - supplement with other sources.

### 3. Source Code (Ultimate Truth)
**Locations**:
- **Frappe Framework**: `/home/slart/frappe-env/dev-env/apps/frappe/`
- **ERPNext Application**: `/home/slart/frappe-env/dev-env/apps/erpnext/`

**Usage**: When documentation is missing or unclear, examine source code for:
- Implementation patterns in similar features
- Method signatures and parameters
- Error handling approaches
- Database schema definitions

## Framework Version Information

**Target Version**: ERPNext v15, Frappe Framework v15
**Important**: Ignore patterns from older versions (v13, v14) that may appear in training data

## File Structure Patterns

### ERPNext App Structure
```
financed_sales/                    # Project directory
├── financed_sales/                # App directory
│   ├── financed_sales/            # Module directory
│   │   ├── doctype/               # DocType definitions
│   │   ├── page/                  # Custom pages
│   │   ├── report/                # Custom reports
│   │   └── *.py                   # Python modules
│   ├── hooks.py                   # App hooks configuration
│   ├── modules.txt                # Module definitions
│   └── patches.txt                # Database patches
└── setup.py                       # App installation
```

### File Naming Conventions
- **DocTypes**: snake_case directory and file names
- **Python modules**: snake_case.py
- **JavaScript files**: snake_case.js
- **Templates**: snake_case.html

## Development Patterns

### DocType Development

#### Core DocTypes (Owned by this app)
- **Controllers**: Define the DocType behavior in Python (not extensions - they ARE the behavior)
- **Creation**: Follow patterns in local `docs/creating-doctypes.md`
- **Example**: Finance Application is a core DocType of Financed Sales app

#### External DocTypes (Owned by other apps)
- **Custom Fields**: Add fields to external DocTypes using `custom_` prefix
- **Property Setters**: Modify properties of external DocTypes
- **Hooks**: Hook into external DocType events (see financed_sales hooks.py for reference)
- **Example**: Payment Entry is a core DocType of ERPNext - we can only customize via custom fields, property setters, and hooks

#### Fixtures
- **Purpose**: DocType instances you want deployed with the app
- **Example**: An Account named 'Penalty' (type: Income) - Account is the DocType, 'Penalty' is the instance
- **Usage**: Any DocType instance that should exist when the app is installed
- **Reference**: See local `docs/creating-fixtures.md`

### Server-Side Hooks
**Primary Purpose**: Modify and hook into external DocTypes events
**Reference**: Check `financed_sales/hooks.py` for existing patterns
**Common Hook Types**:
- `doc_events` - Document lifecycle events for external DocTypes
- `override_whitelisted_methods` - API method overrides
- `boot_session` - Session initialization

### API Development
**Whitelist Methods**: Use `@frappe.whitelist()` for API endpoints
**Error Handling**: Use `frappe.throw()` for user-facing errors
**Database Operations**: Use Frappe ORM, avoid raw SQL when possible

### JavaScript/Client-Side
**Form Scripts**: Use client scripts for form customization
**Page Scripts**: For custom page development
**Dialog API**: For user interactions and confirmations

## Common Mistakes to Avoid

### Deprecated Patterns (v13/v14)
- ❌ Old database API methods
- ❌ Deprecated JavaScript patterns
- ❌ Outdated hook configurations

### Performance Issues
- ❌ Expensive database queries in loops
- ❌ Loading large datasets without pagination
- ❌ Blocking operations in form events

### Security Issues
- ❌ Non-whitelisted API methods
- ❌ SQL injection vulnerabilities
- ❌ Missing permission checks

## When Documentation is Missing

1. **Check local docs/** first for app-specific guidance
2. **Examine existing code** in financed_sales for established patterns
3. **Look at ERPNext source** for similar implementations
4. **Search Frappe framework source** for method definitions
5. **Ask for clarification** if implementation approach is unclear

## Pending Topics

**Testing/Debugging**: Guidelines for testing and debugging patterns will be added when this becomes a priority.

---

**Remember**: Source code is the ultimate truth. When in doubt, look at how similar features are implemented in the existing codebase or ERPNext core.