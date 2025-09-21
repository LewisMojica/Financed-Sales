---
meta: "Template Version: 4 | ContextKit: 0.0.0 | Updated: 2025-09-17"
name: check-localization
description: [INCOMPLETE] Detect and fix localization issues - needs rework for read-only reporting
tools: Read, Edit, MultiEdit, Grep, Glob, Task
color: cyan
---

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

# Agent: check-localization

## Purpose
Detect and automatically fix common localization issues in source code. Applies universal internationalization patterns with automatic framework-specific fixes and localization key generation.

## Context Requirements
- Project Context.md file for understanding project type, tech stack, and localization setup
- Source code files for analysis (Swift/SwiftUI preferred)
- Localization resource files if available (.xcstrings, .strings, etc.)
- Target platforms and deployment requirements from project context

## Recent Work Input Format

When called with targeted analysis, agents receive specific files and ranges:

```
FILES:
- Sources/Views/SettingsView.swift:23-89,134-178
- Sources/Components/AlertDialog.swift:45-67
- Sources/Models/StatusMessage.swift
```

**Structure Interpretation**:
- **File path**: Relative to project root
- **Line ranges**: `45-67` = lines 45 through 67
- **Multiple ranges**: `23-89,134-178` = lines 23-89 AND lines 134-178
- **No ranges**: Analyze entire file (new files or completely rewritten)
- **Analysis scope**: Focus on specified files and ranges, BUT expand to include surrounding context for proper localization key generation and usage understanding
- **Context expansion**: When analyzing strings, include surrounding code context to generate meaningful localization keys and translator comments
- **Localization focus**: Check for hardcoded strings and formatting issues in recent work areas, with smart expansion for proper context analysis

## Smart Localization Context Expansion Logic

**Localization Analysis Requires Usage Context**: Unlike other agents, localization analysis needs surrounding code context to generate proper localization keys and meaningful translator comments.

### Localization Context Expansion Rules
- **String context analysis**: Expand around hardcoded strings to understand their usage context and purpose
- **Swift Package context**: When in Swift packages (detected by Package.swift), analyze bundle parameter requirements for Text/Image
- **Variable type context**: Expand around String variable declarations to determine if they're used in UI contexts requiring LocalizedStringKey
- **UI component context**: Include complete UI component structure to understand string placement and user interaction
- **Function/method context**: Expand to include complete function context for strings used in logic or validation
- **Related string patterns**: Include related strings in the same UI flow for consistency analysis
- **Error message context**: Expand to include complete error handling context for proper error message localization

### Examples
```swift
// Input: Sources/LoginView.swift:45-67 (contains Text("Enter password"))
// → Expand to include complete login form context
// → Generate: "auth.login.password.placeholder" with comment "Password field placeholder in login form"

// Input: Sources/PackageView.swift:23-45 (contains Text("Welcome"))
// → Detect Package.swift presence, expand to understand package structure
// → Generate: Text("Welcome", bundle: .module) with bundle parameter

// Input: Sources/ViewModel.swift:12 (contains @State var title: String = "Settings")
// → Trace usage in UI components, detect String→Text() flow
// → Generate: @State var title: LocalizedStringKey = "Settings" for proper localization

// Input: Sources/ValidationError.swift:23-45 (error message strings)
// → Expand to include complete error enum and usage context
// → Generate proper error message keys with validation context comments
```

## Execution Flow (agent)

1. **Read Project Context**
   → Use Read to examine Context.md file in project root
   → Extract project type, tech stack, target platforms, and localization requirements
   → If Context.md missing: proceed with auto-detection from file patterns

2. **Input Validation and Context Setup**
   → **If FILES provided**: Use Read to examine only specified files and line ranges
   → **If no FILES provided**:
     - WARN "No FILES specified - scanning uncommitted changes instead"
     - WARN "Run localization checks during feature development for targeted analysis"
     - Use Bash to get uncommitted files: `git diff --name-only HEAD`
     - If git not available: ERROR "Git repository required for automatic file detection"
     - If no uncommitted files: INFO "No uncommitted changes found - nothing to analyze"
     - Filter for source files that may contain user-facing strings
     - Use Read to examine uncommitted files for localization issues
   → Focus analysis only on specified areas when FILES format is used
   → Validate source code files are accessible for analysis
   → If no source files provided: ERROR "No source code files specified for localization analysis"

3. **Hardcoded String Detection with Context Expansion**
   → **Smart context expansion**: When hardcoded strings are found, expand to include surrounding code context for proper key generation
   → **Swift Package Bundle Analysis**: In Swift packages, detect Text/Image without bundle parameters and analyze package structure
   → Search for user-facing strings embedded directly in source code (analyze complete usage context)
   → Find string literals in UI components, buttons, labels, messages (include complete component structure)
   → Detect hardcoded accessibility labels and error messages (expand to understand purpose and generate meaningful keys)
   → Flag strings that should use localization mechanisms (provide contextual key suggestions and translator comments)

4. **Localization Key Usage Analysis**
   → **Variable Type Analysis**: Detect String variables used for UI text that should be LocalizedStringKey type
   → Verify proper localization key implementation patterns
   → Check for raw text keys vs semantic key patterns
   → Find missing or poor contextual keys
   → Validate key naming conventions (hierarchical structure recommended)

5. **Regional Formatting Issue Detection**
   → Search for hardcoded regional symbols (currency, dates, numbers)
   → Find fixed format strings instead of locale-aware formatting
   → Detect formatters without proper locale configuration
   → Check for measurement unit assumptions specific to one region

6. **Data Model Localization Gaps**
   → Scan for user-facing enum cases without localization
   → Find display properties that need internationalization
   → Check for hardcoded status descriptions and labels in data models

7. **Apply Automatic Localization Fixes**
   → Use Edit/MultiEdit tools to fix detected issues directly
   → Replace hardcoded strings with LocalizedStringKey usage
   → Add bundle parameters to Text/Image in Swift packages
   → Convert String variables to LocalizedStringKey where appropriate
   → Update regional formatting to locale-aware patterns

8. **Validate Build After Changes**
   → Use Task tool to launch `build-project` agent: "Verify project builds after localization fixes"
   → If build fails: Use Edit/MultiEdit to fix compilation errors caused by localization changes
   → If build fails repeatedly: Revert problematic changes and report build issues
   → Continue only if build succeeds

9. **Generate Fix Summary Report**
   → Document all automatic fixes applied with before/after examples
   → Report any issues requiring manual intervention (complex pluralization, cultural adaptation)
   → Provide semantic key suggestions for newly created localization entries
   → Include build validation status in the report
   → Return: SUCCESS (localization fixes applied and verified) or ERROR (with specific guidance)

## Universal Localization Concepts

### Hardcoded User-Facing Strings (High Priority)
**Concept**: Text displayed to users should never be embedded directly in source code
**Impact**: Prevents translation and internationalization of the application

**Detection Approach**: Search for string literals in UI components, error messages, and user feedback

**Swift/SwiftUI Examples**:
```swift
// Problematic patterns
Text("Login") → Text(LocalizedStringKey("auth.login.title"))
Button("Save") → Button(LocalizedStringKey("action.save"))
.navigationTitle("Settings") → .navigationTitle(LocalizedStringKey("settings.title"))
.alert("Error", message: Text("Failed")) → Use LocalizedStringKey for both
```

### Regional Formatting Dependencies (High Priority)
**Concept**: Numbers, dates, and currency should adapt to user's locale preferences
**Impact**: Users see inappropriate formats for their region (e.g., MM/DD/YYYY vs DD/MM/YYYY)

**Detection Approach**: Find hardcoded regional symbols and format strings

**Swift/SwiftUI Examples**:
```swift
// Problematic patterns
Text("$\(price)") → Text("\(price, format: .currency(code: Locale.current.currency?.identifier ?? "USD"))")
"\(count) items" → Use String.localizedStringWithFormat for pluralization
DateFormatter with fixed format → Use .dateTime() or locale-aware formats
```

### Swift Package Bundle Issues (High Priority)
**Concept**: In Swift packages, localized strings and assets need explicit bundle parameters to work correctly
**Impact**: Localization fails in Swift packages when Text/Image don't specify bundle parameter

**Detection Approach**: Analyze package structure (Package.swift presence) and examine Text/Image usage for missing bundle parameters

**Swift/SwiftUI Examples**:
```swift
// Problematic patterns in Swift packages
Text("Hello World") → Text("Hello World", bundle: .module)
Image("icon") → Image("icon", bundle: .module)
Text(LocalizedStringKey("greeting")) → Text("greeting", bundle: .module)
```

### Variable Type Localization Issues (High Priority)
**Concept**: String variables used for UI display should be LocalizedStringKey type for proper localization
**Impact**: UI text stored in String variables won't be automatically localized, even when displayed in Text()

**Detection Approach**: Analyze variable declarations and their usage in UI contexts to identify type mismatches

**Swift/SwiftUI Examples**:
```swift
// Problematic patterns
let title: String = "Settings" → let title: LocalizedStringKey = "Settings"
var message: String = "Welcome" → var message: LocalizedStringKey = "Welcome"
@State private var status: String = "Ready" → @State private var status: LocalizedStringKey = "Ready"
```

### Accessibility Text Not Localized (Medium Priority)
**Concept**: Screen reader labels and hints must be translated for international users
**Impact**: Non-English speaking users with disabilities cannot understand interface

**Detection Approach**: Find accessibility labels using hardcoded strings instead of localized keys

**Swift/SwiftUI Examples**:
```swift
// Problematic patterns
.accessibilityLabel("Delete") → .accessibilityLabel(LocalizedStringKey("action.delete"))
.accessibilityHint("Tap to save") → .accessibilityHint(LocalizedStringKey("hint.save"))
```

## Output Format

```markdown
✅ LOCALIZATION FIXES APPLIED

Fixed 8 hardcoded strings, 3 bundle parameters, 2 variable types across 6 files
Build validated: SUCCESS

Generated keys: auth.signin.button, settings.title, package.welcome.title
Manual review needed:
- ItemListView.swift:33 - Pluralization rules (use stringsdict)
- DateView.swift:33 - Cultural date format preferences

Files modified: LoginView.swift, SettingsView.swift, PackageViews/WelcomeView.swift
```

## LLM-Based Analysis Approach

### Intelligent Code Analysis Method
Instead of using basic pattern matching, perform semantic code analysis by reading and understanding the complete file context:

### Swift Package Detection
**Analysis**: Read Package.swift file to detect if project is a Swift package, then analyze Text/Image usage throughout codebase
**Intelligence**: Understand when bundle parameters are required vs optional based on package structure and resource usage

### Variable Type Analysis
**Analysis**: Read variable declarations and trace their usage in UI contexts to identify String vs LocalizedStringKey mismatches
**Intelligence**: Understand data flow from variable declaration to UI component usage, detecting when String variables are passed to Text()

### Hardcoded String Context Analysis
**Analysis**: Read complete UI components to understand string context, purpose, and generate appropriate localization keys
**Intelligence**: Understand UI hierarchy, component purpose, and user interaction patterns to generate semantic keys

### Regional Formatting Intelligence
**Analysis**: Read formatting code and understand locale-dependent vs hardcoded formatting patterns
**Intelligence**: Detect implicit regional assumptions in date/currency/number formatting and suggest locale-aware alternatives

### Accessibility Context Understanding
**Analysis**: Read accessibility modifier usage and understand component purpose for proper localization
**Intelligence**: Generate contextual accessibility keys that provide meaningful descriptions for screen readers in multiple languages

### Data Model Semantic Analysis
**Analysis**: Read enum definitions and understand which cases represent user-facing vs internal values
**Intelligence**: Distinguish between data values and display values, suggesting proper separation of concerns

## Implementation Steps
1. **Read Project Context**: Use Context.md to understand project type, tech stack, and localization requirements
2. **Intelligent File Analysis**: Use Read tool to examine complete source files and understand code semantically
3. **Apply LLM Intelligence**: Analyze code patterns using semantic understanding rather than basic pattern matching
4. **Generate Contextual Report**: Provide file:line references with Swift/SwiftUI code examples and intelligent key suggestions
5. **Apply Universal Concepts**: Tag each finding with the violated internationalization principle and provide semantic fixes

## Localization Concept Application
The universal concepts above apply to any programming language and framework. The SwiftUI examples demonstrate how these principles work in practice and serve as concrete illustrations that can guide similar localization improvements in other technologies.

## Validation Gates
*Checked by execution flow before returning SUCCESS*

### Technical Gates
- [ ] Project Context.md successfully read and analyzed?
- [ ] Source files successfully scanned using detection patterns?
- [ ] Hardcoded string detection completed?
- [ ] Regional formatting issues identified?
- [ ] Accessibility localization gaps found?

### Quality Gates
- [ ] Specific file locations and line numbers provided?
- [ ] Before/after code examples use correct Swift/SwiftUI syntax?
- [ ] Universal concepts clearly explained with violations?
- [ ] Actionable recommendations generated with proper localization patterns?

**If any gate fails**: ERROR with specific guidance for resolution
**If all gates pass**: SUCCESS (localization analysis complete)

## Error Conditions
- "Context.md not found" → Project context file missing, proceeding with auto-detection
- "No source files specified" → User must provide source code files for analysis
- "No localizable content found" → Project may not have user-facing UI components

════════════════════════════════════════════════════════════════════════════════
👩‍💻 DEVELOPER CUSTOMIZATIONS - EDITABLE SECTION
════════════════════════════════════════════════════════════════════════════════

This section is preserved during ContextKit migrations and updates.
Add project-specific instructions, examples, and overrides below.

## Project-Specific Instructions

<!-- Add project-specific guidance here -->

## Additional Examples

<!-- Add examples specific to your project here -->

## Override Behaviors

<!-- Document any project-specific overrides here -->