I'll explore the codebase to understand the complete workflow for financed sales processes. Let me start by examining the key components and their relationships.


[11 tools called]

Now let me check the settings to understand the configuration:


[1 tool called]

Based on my exploration of the codebase, I can now provide you with a comprehensive description of the financed sales workflow. Here's the complete user journey:

# **Financed Sales Workflow - Complete User Journey**

## **Overview**
The financed sales system allows customers to purchase items on credit with structured payment plans. The workflow involves multiple stages from initial quotation to final payment completion.

## **1. Initial Setup & Configuration**

### **System Configuration (Admin)**
- **Financed Sales Settings** are configured with:
  - Default interest rate (e.g., 5% monthly)
  - Default down payment percentage (e.g., 40%)
  - Interest account for accounting
  - Application fee
  - Interest rate period (Monthly/Annual)

## **2. Sales Process Initiation**

### **Step 1: Create Quotation**
- Sales representative creates a standard **Quotation** with items and pricing
- This is a regular ERPNext quotation process
- Customer information and item details are captured

### **Step 2: Create Finance Application**
- From the quotation, a **Finance Application** is created
- **Key Fields Captured:**
  - Customer (from quotation)
  - Quotation reference
  - Repayment term (months)
  - Interest rate (defaults from settings)
  - Down payment amount (calculated from percentage)
  - First installment date
  - Application fee

- **System Calculations:**
  - Total amount to finance
  - Monthly installment amount (calculated automatically)
  - Interest calculations
  - Down payment amount

- **Proposed Payment Plan:**
  - System generates installment schedule
  - Shows due dates and amounts for each installment
  - Displays total credit amount and interest

## **3. Approval Workflow**

### **Workflow States:**
1. **Draft** → User creates and saves the application
2. **Pending** → User submits for approval
3. **Approved** → Manager approves the application
4. **Rejected** → Manager rejects the application

### **State Transitions:**
- **Submit**: Draft → Pending
- **Approve**: Pending → Approved
- **Reject**: Pending → Rejected

## **4. Document Creation (Automatic)**

### **When Finance Application moves to "Pending":**
- **Sales Order** is automatically created from the quotation
- Includes financed items with interest distributed proportionally
- Links back to the Finance Application

### **When Finance Application is "Approved":**
- **Credit Sales Invoice** is created (marked as credit invoice)
- **Payment Plan** is created with:
  - All installment details
  - Down payment tracking
  - Payment references
  - Status tracking

## **5. Payment Processing**

### **Down Payment Phase:**
- **Button Available**: "Pay down payment" (when pending amount > 0)
- **User Action**: Click button → Payment dialog opens
- **Payment Dialog Fields:**
  - Amount to pay (required)
  - Payment method (required - Link to Mode of Payment)
  - Reference number (for Wire Transfer/Credit Card)
  - Reference date (for Wire Transfer/Credit Card)

- **Confirmation Step**: 
  - Summary dialog shows payment details
  - User confirms before submission
  - Payment Entry is created and submitted automatically

### **Installment Payment Phase:**
- **Button Available**: "Pay Next Installment" (when down payment is complete)
- **Same Payment Process**: Identical dialog and confirmation flow
- **Automatic Allocation**: System allocates payments to installments in order

## **6. Payment Tracking & Management**

### **Payment Entry Processing:**
- **Validation**: Ensures exactly 1 reference and no unallocated amount
- **Automatic Updates**: 
  - Updates down payment amounts
  - Allocates payments to installments
  - Tracks paid vs pending amounts
  - Maintains payment references

### **Payment Plan Management:**
- **Status Tracking**: Active, Completed, Overdue, etc.
- **Installment Management**: Each installment tracks:
  - Due date
  - Amount
  - Paid amount
  - Pending amount
  - Payment references

### **Payment Allocation Logic:**
- **Sequential Processing**: Payments are allocated to installments in order
- **Down Payment First**: Must complete down payment before installments
- **Automatic Distribution**: System handles partial payments and overpayments
- **Reference Management**: Links Payment Entries to specific installments

## **7. Key User Interactions**

### **For Sales Representatives:**
1. Create quotation
2. Create finance application
3. Submit for approval
4. Process down payments (after approval)
5. Process installment payments

### **For Managers:**
1. Review finance applications
2. Approve or reject applications
3. Monitor payment status

### **For Customers:**
1. Receive payment notifications
2. Make payments through various methods
3. Track payment history

## **8. Technical Features**

### **Data Integrity:**
- **Validation**: Multiple validation layers (frontend and backend)
- **Error Handling**: Graceful error messages for missing data
- **Confirmation Dialogs**: Prevent accidental submissions

### **Payment Methods:**
- **Standard Methods**: Cash, Bank Transfer, etc.
- **Special Handling**: Wire Transfer and Credit Card require reference numbers
- **Account Integration**: Automatic account assignment based on payment method

### **Reporting & Tracking:**
- **Payment History**: Complete audit trail
- **Status Monitoring**: Real-time payment status
- **Installment Tracking**: Detailed installment management

## **9. Workflow Summary**

```
Quotation → Finance Application → [Approval] → Sales Order → [Approval] → Credit Invoice + Payment Plan → Down Payments → Installment Payments → Completion
```

This workflow ensures proper credit management, payment tracking, and financial control while providing a smooth user experience for both sales staff and customers.