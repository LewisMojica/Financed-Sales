# Project Context: Financed Sales

## Project Overview

- **Version**: ContextKit 0.0.0
- **Setup Date**: 2025-09-20
- **Components**: 1 component discovered and analyzed
- **Workspace**: None (standalone project)
- **Primary Tech Stack**: Python/Frappe Framework (ERPNext App)

## Component Architecture

**Project Structure**:

```
📁 Financed Sales
└── 📦 Financed Sales App (ERPNext App) - Customer financed sales workflows - Python/Frappe/ERPNext - ./
```

**Component Summary**:
- **1 Frappe/ERPNext component** - Python 3.10+, Frappe Framework v15, ERPNext v15
- **Dependencies**: Managed by Frappe bench, no additional external dependencies
- **Documentation**: 7 specialized docs covering workflow, development, and customization

---

## Component Details

### Financed Sales App - ERPNext Application

**Location**: `./`
**Purpose**: Enables customer financed sales workflows in ERPNext - creates financing applications from quotations and POS transactions with structured payment plans, interest calculations, and installment tracking
**Tech Stack**: Python 3.10+, Frappe Framework v15, ERPNext v15, JavaScript/Vue.js

**File Structure**:
```
financed_sales/
├── docs/                     # Developer documentation
├── financed_sales/           # Main app module
│   ├── debug/               # Development utilities
│   ├── doctype/             # Core DocTypes (Finance Application, Payment Plan, etc.)
│   ├── fixtures/            # JSON configuration data
│   ├── public/              # Frontend assets
│   └── TODO.md             # Development backlog
├── pyproject.toml          # Python project configuration
├── CLAUDE.md               # Development instructions
└── README.md               # Project overview
```

**Dependencies** (from pyproject.toml):
- **Python**: >=3.10 (required)
- **Frappe Framework**: ~=15.0.0 (managed by bench - ERPNext core dependency)
- **Build System**: flit_core >=3.4,<4 (packaging)
- **Code Quality**: Ruff (linting and formatting with custom rules)

**Development Commands**:
```bash
# Build Frontend (validated during setup) - MANDATORY after JavaScript changes
cd ~/frappe-env/dev-env && ~/frappe-env/bin/bench --site dev.localhost build --app financed_sales

# Test Suite (validated during setup)
cd ~/frappe-env/dev-env && ~/frappe-env/bin/bench --site dev.localhost run-tests --app financed_sales

# Import Fixtures (after DocType JSON edits)
cd ~/frappe-env/dev-env && ~/frappe-env/bin/bench --site dev.localhost import-doc apps/financed_sales/financed_sales/fixtures/custom_field.json

# Environment Setup (activate virtualenv first)
source ~/frappe-env/bin/activate
```

**Code Style** (detected):
- **Python**: Ruff formatting with tab indentation, 110 character line limit
- **Quotes**: Double quotes preferred
- **Target**: Python 3.10+ features
- **Docstrings**: Google style formatting with code examples
- **Custom Rules**: Frappe-specific imports and typing modules configured

---

## Development Environment

**Requirements** (from analysis):
- **Python**: 3.10+ (matches ERPNext v15 requirements)
- **Frappe Bench**: Active virtual environment at `~/frappe-env/`
- **ERPNext v15**: Base platform with core business logic
- **Node.js/npm**: For frontend asset compilation
- **Development Site**: `dev.localhost` (configured for testing)

**Build Tools** (detected):
- **Frappe Bench**: Primary development and build orchestration
- **Ruff**: Python linting and formatting (configured in pyproject.toml)
- **ESBuild**: JavaScript/CSS compilation (via Frappe bench)
- **Flit**: Python packaging system

**Formatters** (configured):
- **Python**: Ruff with tab indentation, 110-char lines, double quotes
- **JavaScript/CSS**: ESBuild via Frappe bench build system
- **JSON**: Custom field fixtures with structured formatting

## Constitutional Principles

**Core Principles**:
- ✅ Accessibility-first design (ERPNext UI accessibility standards)
- ✅ Privacy by design (ERPNext role-based permissions, data protection)
- ✅ Localizability from day one (ERPNext translation framework support)
- ✅ Code maintainability (Frappe conventions, structured DocTypes)
- ✅ Platform-appropriate UX (ERPNext design system, user workflows)

**ERPNext-Specific Principles**:
- ✅ DocType-driven development (structured data models)
- ✅ Permission-based security (role hierarchies, document-level access)
- ✅ Workflow automation (approval processes, state management)
- ✅ Audit trail integrity (all changes tracked and timestamped)

**Workspace Inheritance**: None - using global defaults with ERPNext adaptations

## ContextKit Workflow

**Systematic Feature Development**:
- `/ctxk:plan:1-spec` - Create business requirements specification (prompts interactively)
- `/ctxk:plan:2-research-tech` - Define technical research, architecture and implementation approach
- `/ctxk:plan:3-steps` - Break down into executable implementation tasks

**Development Execution**:
- `/ctxk:impl:start-working` - Continue development within feature branch (requires completed planning phases)
- `/ctxk:impl:commit-changes` - Auto-format code and commit with intelligent messages

**Quality Assurance**: Automated agents validate code quality during development
**Project Management**: All validated build/test commands documented above for immediate use

## Development Automation

**Quality Agents Available**:
- `build-project` - Execute Frappe builds with ERPNext compliance validation
- `check-accessibility` - ERPNext UI accessibility and assistive technology validation
- `check-localization` - Translation framework and multi-language validation
- `check-error-handling` - Frappe exception patterns and user-friendly error messages
- `check-modern-code` - Python 3.10+ features and Frappe best practices
- `check-code-debt` - Technical debt cleanup and documentation validation

## Configuration Hierarchy

**Inheritance**: None (Standalone Project) → **This Project**

**This Project Inherits From**:
- **Workspace**: None (standalone project)
- **Project**: Frappe/ERPNext conventions and component configurations documented above

**Override Precedence**: Project-specific settings take precedence over Frappe/ERPNext defaults

---
*Generated by ContextKit with comprehensive component analysis. Manual edits preserved during updates.*