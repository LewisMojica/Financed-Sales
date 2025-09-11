# 💰 Financed Sales

> **An ERPNext application for financed sales workflows**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-0.29.4-green.svg)](https://github.com/your-repo/financed_sales)
[![ERPNext Compatible](https://img.shields.io/badge/ERPNext-Compatible-orange.svg)](https://erpnext.com/)

**Financed Sales** is an ERPNext application designed for financed sales workflows - selling products or services with payment plans. It converts quotations into structured financing applications with automated payment plans, interest calculations, and payment tracking.

**Note**: This application is specifically for financed sales (selling items with installment payments), not general financing like cash loans or credit facilities.

## 📋 **Table of Contents**

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ Core Architecture](#️-core-architecture)
- [🚀 Quick Start](#-quick-start)
- [💡 Usage Examples](#-usage-examples)
- [🎭 User Journey](#-user-journey)
- [🔬 Payment Logic](#-payment-logic)
- [🎨 Customization Options](#-customization-options)
- [📈 Benefits](#-benefits)
- [🔧 Development & Contributing](#-development--contributing)
- [📚 Documentation](#-documentation)
- [🤝 Support & Community](#-support--community)
- [📜 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)

---

## 🎯 **Overview**

Financed Sales addresses the need for structured financed sales within ERPNext. The application provides tools for selling items with financing terms, managing approval workflows, and tracking installment payments from quotation to final collection.

### **Key Challenges Addressed**
- Manual calculations for financing terms and interest distribution
- Disconnected workflows between sales, finance, and collections teams
- Limited payment tracking and installment management capabilities
- Manual processes prone to errors
- Lack of structured approval workflows for financing decisions

### **Solution Approach**
A structured financing system that automates the process from quotation to payment collection.

---

## ✨ **Key Features**

### 🚀 **Financing Workflows**
```
📋 Finance Application → ✅ Approval → 💰 Payment Collection
        ↓ (auto)              ↓ (auto)
   📄 Sales Order     💳 Invoice + Payment Plan
```

**Key automation points:**
- **POS/Quotation** → Finance Application (one-click creation)
- **Submission** → Sales Order (auto-created)  
- **Approval** → Invoice + Payment Plan (auto-created, installment tracking starts)

### 🧮 **Interest Calculations**
- **Proportional Distribution**: Interest distributed accurately across items using banker's rounding
- **Flexible Terms**: Monthly or annual interest rates with customizable periods
- **Down Payment Management**: Configurable down payment percentages
- **Application Fees**: Built-in support for processing fees

### 🔐 **Approval System**
- **Multi-State Workflow**: Draft → Pending → Approved/Rejected
- **Role-Based Permissions**: Separate roles for sales users and managers
- **Automatic Document Creation**: Sales orders and invoices generated on approval
- **Audit Trail**: Complete history of all financing decisions

### 💳 **Payment Processing**
- **Multiple Payment Methods**: Cash, bank transfer, wire transfer, credit card
- **Sequential Payment Allocation**: Down payment first, then installments in order
- **Reference Number Tracking**: Required for wire transfers and credit cards
- **Confirmation Dialogs**: Prevent accidental payments with built-in safeguards

### 📊 **Comprehensive Tracking**
- **Real-Time Status Updates**: Active, completed, overdue payment plans
- **Payment History**: Complete audit trail of all transactions
- **Overdue Management**: Daily automated checks for late payments
- **Customer Dashboard**: Clear view of payment obligations

---

## 🏗️ **Core Architecture**

### **Essential DocTypes**

| DocType | Purpose | Key Features |
|---------|---------|--------------|
| **Finance Application** | Main financing document | Interest calculation, approval workflow, installment generation |
| **Payment Plan** | Payment schedule manager | Down payment tracking, installment allocation, status management |
| **Factura Proforma** | Custom invoice format | Financed item display, interest breakdown |
| **Financed Sales Settings** | Global configuration | Interest rates, down payment defaults, account setup |

### **Smart Integrations**
- **Point of Sale**: Direct financing from POS transactions
- **Quotation Enhancement**: One-click finance application creation
- **ERPNext Workflow**: Seamless integration with existing sales processes
- **Payment Entry Automation**: Auto-creation and allocation of payments

---

## 🚀 **Quick Start**

### **Prerequisites**
- **ERPNext v15** (this app extends ERPNext core functionality)
- Python 3.10+ (same as ERPNext v15 requirement)
- Frappe Framework

**Note**: This app is designed to work alongside ERPNext, leveraging core doctypes like Quotation, Sales Order, Sales Invoice, and Payment Entry.

### **Installation**

**Important**: Install this app on an existing Frappe site with ERPNext, not as a standalone application.

```bash
# Get the app
cd /path/to/your/bench
bench get-app https://github.com/LewisMojica/Financed-Sales.git

# Install on your Frappe site with ERPNext
bench --site your-site.com install-app financed_sales
```

### **Initial Configuration**

1. **Configure Financed Sales Settings**
   ```
   Setup > Financed Sales Settings
   ```
   - Set default interest rate (e.g., 5% monthly)
   - Configure down payment percentage (e.g., 40%)
   - Select interest account for accounting
   - Set application fee if applicable

2. **Setup User Permissions**
   - Assign **Financed Sales User** role to sales staff
   - Assign **Financed Sales Manager** role to approvers

3. **Ready to Go!** 🎉

---

## 💡 **Usage Examples**

### **Scenario 1: Electronics Store Financing**
```
📱 Customer wants $1,200 smartphone
💰 40% down payment = $480
📅 12-month financing at 3% monthly
💳 Monthly installment: $62.40
✅ Total with interest: $1,228.80
```

### **Scenario 2: Furniture Store Payment Plan**
```
🛋️ Customer buys $3,000 furniture set
💰 25% down payment = $750
📅 18-month plan at 2.5% monthly
💳 Monthly installment: $137.50
✅ Total with interest: $3,225.00
```

---

## 🎭 **User Journey**

### **👨‍💼 Sales Representative**
1. Create quotation for customer
2. Generate finance application with one click
3. Configure payment terms and interest
4. Submit for approval
5. Process payments when approved

### **👩‍💼 Finance Manager**
1. Review submitted applications
2. Approve or reject with comments
3. Monitor payment performance
4. Generate financing reports

### **👤 Customer**
1. Receive payment schedule
2. Make down payment
3. Complete monthly installments
4. Track payment history

---

## 🔬 **Payment Logic**

### **Sequential Payment Allocation Algorithm**
Payments are automatically allocated using an algorithm that ensures proper order:
- **Down payment first**: All payments go to down payment until fully paid
- **Installment sequence**: Payments then fill installments in chronological order
- **Partial payments**: Handles partial payments across multiple installments
- **Cents-based precision**: Uses integer cents internally to avoid floating point errors

### **Payment State Validation**
The system verifies that installment payment states make logical sense:
- **Sequential payment enforcement**: Installments must be paid in order (no skipping)
- **State consistency checking**: Validates current payment state against proposed changes
- **Payment integrity**: Ensures no gaps exist in the payment sequence

### **Progressive Penalty System**
Overdue installments trigger automatic penalty calculations:
- **Grace period**: 5 days with no penalty
- **Escalating penalties**: 5% per 30-day period after grace (5%, 10%, 15%...)
- **Daily automation**: Scheduled task checks for overdue payments
- **Smart state management**: Updates Payment Plan status based on due dates

---

## 🎨 **Customization Options**

### **Custom Fields Integration**
All custom fields are automatically managed through fixtures:
- `custom_financed_items` - Enhanced item tables with interest
- `custom_finance_application` - Links to financing documents
- `custom_payment_plan` - Payment schedule references

### **Workflow Customization**
Modify approval workflows through:
```
Setup > Workflow > Finance Application Approval
```

### **Print Format Customization**
Custom invoice formats available:
- **Factura Proforma**: Professional financing invoice
- Customizable headers and footers
- Multi-language support

---

## 📈 **Benefits**

| Business Impact | Technical Advantage |
|-----------------|-------------------|
| 🎯 **Structured Sales Process** | ⚡ **Automated Calculations** |
| 💰 **Payment Tracking** | 🔒 **Data Validation** |
| ⏱️ **Streamlined Processing** | 🔄 **ERPNext Integration** |
| 📊 **Cash Flow Management** | 📋 **Audit Trail** |
| 🎉 **Organized Customer Experience** | 🛡️ **Role-Based Security** |

---

## 🔧 **Development & Contributing**

### **Development Setup**
1. Create a Frappe site with Frappe v15 and ERPNext v15
2. Set developer mode on the site
3. Get and install the Financed Sales app
4. Unshallow `apps/financed_sales` for full git history
5. Install pre-commit hooks: `pre-commit install`

### **Code Quality Tools**
- **Ruff**: Python linting and formatting
- **ESLint**: JavaScript code quality
- **Prettier**: Code formatting
- **Pre-commit**: Automated quality checks

### **Testing**
```bash
# Run tests
bench --site your-site.com run-tests --app financed_sales

# Specific test
bench --site your-site.com run-tests financed_sales.tests.test_payment_plan
```


---

## 📚 **Documentation**

### **User Guides**
- [Complete Workflow Guide](USER-WORKFLOW.md) - Step-by-step user instructions
- [Development Notes](DEVELOPMENT_NOTES.md) - Technical implementation details

### **Technical Docs**
- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api.md)
- [Customization Guide](docs/customization.md)

---

## 🤝 **Support & Community**

### **Getting Help**
- 📧 **Email**: lewismojica3@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/financed_sales/issues)
- 💬 **Discussions**: [Community Forum](https://discuss.frappe.io)

### **Contributing**
We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for:
- Code style requirements
- Pull request process
- Issue reporting guidelines

**For AI assistants (Claude Code, etc.)**: This project includes comprehensive development guidance:
- [CLAUDE.md](CLAUDE.md) - Architecture overview, workflows, and AI-specific conventions
- [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md) - Technical implementation details and common pitfalls

---

## 📜 **License**

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

Built with ❤️ using:
- [Frappe Framework](https://frappeframework.com/) - The foundation
- [ERPNext](https://erpnext.com/) - The business platform
- [Vue.js](https://vuejs.org/) - Frontend reactivity

**Special thanks** to the Frappe community for continuous inspiration and support.

---

<div align="center">

**⭐ Star this repo if Financed Sales helped your business grow! ⭐**

[⬆️ Back to Top](#-financed-sales)

</div>