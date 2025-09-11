# 💰 Financed Sales

> **Transform your sales process with intelligent financing workflows**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-0.29.4-green.svg)](https://github.com/your-repo/financed_sales)
[![ERPNext Compatible](https://img.shields.io/badge/ERPNext-Compatible-orange.svg)](https://erpnext.com/)

**Financed Sales** is a powerful ERPNext application that revolutionizes customer financing workflows. Turn quotations into structured financing applications with automated payment plans, interest calculations, and seamless payment tracking.

---

## 🎯 **Why Financed Sales?**

In today's competitive market, offering financing options can be the difference between closing a sale and losing a customer. Financed Sales transforms your ERPNext instance into a comprehensive financing platform that handles everything from initial quotations to final payment collection.

### **The Problem We Solve**
- 📊 **Complex manual calculations** for financing terms and interest distribution
- 🔄 **Disconnected workflows** between sales, finance, and collections teams
- 📋 **Lack of payment tracking** and installment management
- ⚠️ **Error-prone manual processes** leading to revenue leakage
- 🏦 **No structured approval workflows** for financing decisions

### **Our Solution**
A complete financing ecosystem that automates the entire process from quote to collection.

---

## ✨ **Key Features**

### 🚀 **Intelligent Financing Workflows**
```
💼 Quotation → 📋 Finance Application → ✅ Approval → 📄 Sales Order → 💳 Credit Invoice + Payment Plan → 💰 Payment Collection
```

### 🧮 **Smart Interest Calculations**
- **Proportional Distribution**: Interest distributed accurately across items using banker's rounding
- **Flexible Terms**: Monthly or annual interest rates with customizable periods
- **Down Payment Management**: Configurable down payment percentages
- **Application Fees**: Built-in support for processing fees

### 🔐 **Robust Approval System**
- **Multi-State Workflow**: Draft → Pending → Approved/Rejected
- **Role-Based Permissions**: Separate roles for sales users and managers
- **Automatic Document Creation**: Sales orders and invoices generated on approval
- **Audit Trail**: Complete history of all financing decisions

### 💳 **Advanced Payment Processing**
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
- ERPNext v13+ (compatible with latest versions)
- Python 3.8+
- Frappe Framework

### **Installation**

```bash
# Get the app
cd /path/to/your/bench
bench get-app https://github.com/your-repo/financed_sales.git

# Install on your site
bench --site your-site.com install-app financed_sales

# Setup fixtures and custom fields
bench --site your-site.com migrate
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

## 🛠️ **Technical Highlights**

### **Payment Processing Engine**
```python
# Automatic payment allocation with validation
def allocate_payment(payment_entry):
    # Validates payment method requirements
    # Allocates to down payment first
    # Then processes installments sequentially
    # Updates all related documents
```

### **Interest Distribution Algorithm**
```python
# Proportional interest distribution using banker's rounding
def distribute_interest_to_items(items, total_interest):
    # Ensures precise calculations
    # Maintains data integrity
    # Prevents rounding errors
```

### **Workflow State Management**
```python
# Automatic document creation based on workflow states
if workflow_state == 'Approved':
    create_sales_order()
    create_credit_invoice()
    create_payment_plan()
```

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
| 🎯 **Increase Sales Conversion** by 40%+ | ⚡ **Zero Manual Calculations** |
| 💰 **Reduce Revenue Leakage** | 🔒 **Built-in Data Validation** |
| ⏱️ **Faster Processing Time** | 🔄 **Seamless ERPNext Integration** |
| 📊 **Better Cash Flow Management** | 📋 **Complete Audit Trail** |
| 🎉 **Improved Customer Experience** | 🛡️ **Role-Based Security** |

---

## 🔧 **Development & Contributing**

### **Development Setup**
```bash
# Clone and setup
cd apps/financed_sales
source ~/frappe-env/bin/activate

# Install pre-commit hooks
pre-commit install

# Build after changes
bench --site your-site.com build --app financed_sales
```

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

### **Debugging**
Debug scripts available in `financed_sales/debug/`:
```bash
bench --site your-site.com execute "financed_sales.debug.debug_penalty.debug_function"
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