# App Fixes & Improvements

## High Priority
- [ ] If there is an open or accepted finance approval, shouldn't be possible to ammend source quotation.
- [ ] If a quotation is cancelled it's associated finance approval should be cancelled or deleted.
- [ ] A warning should be given when cancelling the quote will delete or cancel a finance approval
- [ ] Many valitations missing.
- [ ] some thing shouldn't be done in the client side, like generating the installments in the Finance Proposal form?
- [ ] One quotation shouldn't be able to create many Finance Application
- [ ] # TODO: Validate that 'INTEREST' item has a proper income account set. If not, show frappe.msgprint and warn user on invoice validation
- [ ] need to pupolate the last two fields in finance application
## Medium Priority  
- [ ] maybe check if dgii compliance is installed an ask if the credit invoice should be with ncf? 

## Low Priority
- [ ] the button in quotation that creates a finance application does it with a frappe.call of frappe.insert.
the method int api.py also creates a finace application. Both should do it calling a function in the server side 
## ??

- [ ] En que momento se cobra el avance? y como relacionar el payment entry
- [ ] incluir itbis en total a credito en factura proforma?
