### Debugging with bench execute
For faster debugging than console copy-paste, create debug scripts in the `financed_sales/debug/` directory:

```python
# Create file: financed_sales/debug/debug_[feature].py
def debug_function():
    import frappe
    # Your debug code here
    print("Debug output")
```

Execute with:
```bash
bench --site [site-name] execute "financed_sales.debug.debug_[feature].debug_function"
```

**Debug Directory Structure:**
```
financed_sales/
├── debug/                    # Ignored by git
│   ├── README.md            # Debug patterns and examples
│   ├── debug_penalty.py     # Penalty calculation debugging
│   └── debug_[feature].py   # Feature-specific debugging
```

**Benefits:**
- Immediate execution and output
- No interactive session management needed  
- Can include complex multi-step debugging logic
- Full access to Frappe context and database
- Organized and reusable debug scripts
- Debug files ignored by git for clean repository


