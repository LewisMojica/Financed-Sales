---
meta: "Template Version: 7 | ContextKit: 0.0.0 | Updated: 2025-09-17"
name: check-accessibility
description: [INCOMPLETE] Detect and fix accessibility issues in UI code - needs rework for read-only reporting
tools: Read, Edit, MultiEdit, Grep, Glob, Task
color: cyan
---

# Agent: check-accessibility

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

## Purpose
Detect and automatically fix accessibility issues in UI code including missing screen reader labels, text scaling gaps, and keyboard navigation problems. Applies universal accessibility principles with automatic framework-specific fixes.

**⚡ AI Capabilities**: Static code analysis, automatic label insertion, Dynamic Type support detection, missing accessibility label detection, color contrast pattern validation (code-level)
**🧪 Requires Manual Testing**: VoiceOver navigation, actual device testing, user experience validation, all real app interaction and accessibility verification

## Recent Work Input Format

When called with targeted analysis, agents receive specific files and ranges:

```
FILES:
- Sources/Views/ProfileView.swift:34-156
- Sources/Components/CustomButton.swift
```

**Structure Interpretation**:
- **File path**: Relative to project root
- **Line ranges**: `34-156` = lines 34 through 156
- **Multiple ranges**: `23-89,145-201` = lines 23-89 AND lines 145-201
- **No ranges**: Analyze entire file (new files or completely rewritten)
- **Analysis scope**: Focus ONLY on specified files and ranges, ignore rest of codebase

## Execution Flow (agent)

1. **Read Project Context**
   → Use Read to examine Context.md file in project root
   → Extract project type, tech stack, and accessibility requirements
   → If Context.md missing: proceed with auto-detection

2. **Scan Specified UI Code Files**
   → **If FILES provided**: Use Read to examine only specified files and line ranges
   → **If no FILES provided**:
     - WARN "No FILES specified - scanning uncommitted changes instead"
     - WARN "Run accessibility checks during feature development for targeted analysis"
     - Use Bash to get uncommitted files: `git diff --name-only HEAD`
     - If git not available: ERROR "Git repository required for automatic file detection"
     - If no uncommitted files: INFO "No uncommitted changes found - nothing to analyze"
     - Filter for UI files based on project context (.swift, .jsx, .tsx, .vue, etc.)
     - Use Read to examine uncommitted UI files only
   → Focus analysis only on specified areas when FILES format is used
   → If no UI files found: ERROR "No UI code files to analyze"

3. **Detect Universal Accessibility Issues**
   → **Missing Labels**: Interactive elements without screen reader labels
   → **Text Scaling**: Hardcoded font sizes that prevent user scaling preferences
   → **Color Dependency**: Information conveyed only through color
   → **Keyboard Navigation**: Interactive elements missing keyboard focus support
   → **Contrast Issues**: Insufficient color contrast for readability

4. **Apply Automatic Accessibility Fixes**
   → Use Edit/MultiEdit tools to fix detected issues directly
   → Add missing accessibility labels to interactive elements
   → Replace hardcoded font sizes with dynamic type
   → Add accessibility actions for custom gestures
   → Update accessibility traits for proper component behavior

5. **Validate Build After Changes**
   → Use Task tool to launch `build-project` agent: "Verify project builds after accessibility fixes"
   → If build fails: Use Edit/MultiEdit to fix compilation errors caused by accessibility changes
   → If build fails repeatedly: Revert problematic changes and report build issues
   → Continue only if build succeeds

6. **Generate Fix Summary Report**
   → Document all automatic fixes applied with before/after examples
   → Report any issues requiring manual intervention (complex color contrast fixes)
   → Provide file locations and line numbers for all changes made
   → Include build validation status in the report
   → Return: SUCCESS (accessibility fixes applied and verified) or ERROR (with specific guidance)

## Universal Accessibility Principles

### Screen Reader Labels
**Concept**: All interactive elements need descriptive labels for screen readers
**Impact**: Users with visual impairments cannot understand element purpose

**Detection Approach**: Search for interactive elements (buttons, images, inputs) without accessibility labels

### Text Scaling Support
**Concept**: Text must scale with user's font size preferences
**Impact**: Users with vision difficulties cannot enlarge text to readable sizes

**Detection Approach**: Find hardcoded font sizes instead of relative/semantic sizing

### Color Independence
**Concept**: Information cannot rely solely on color to convey meaning
**Impact**: Users with color blindness or visual impairments miss critical information

**Detection Approach**: Identify status indicators, alerts, or data that use only color differentiation

### Keyboard Navigation
**Concept**: All interactive elements must be reachable and usable via keyboard
**Impact**: Users with motor impairments or who cannot use pointing devices are blocked

**Detection Approach**: Find interactive elements missing keyboard focus or navigation support

## Detection Patterns (SwiftUI Examples)

### Missing Screen Reader Labels
```bash
# Find buttons and images without accessibility labels
grep -n "Button\|Image" *.swift | grep -v "accessibilityLabel"
```

### Fixed Font Sizes
```bash
# Find hardcoded font sizes that prevent scaling
grep -n "\.font.*size:" *.swift
grep -n "Font\.system(size:" *.swift
```

### Color-Only Information
```bash
# Find potential color-only status indicators
grep -n "\.foregroundColor\|\.background.*Color" *.swift
```

### Missing Accessibility Elements
```bash
# Find custom controls that might need accessibility support
grep -n "TapGesture\|onTapGesture" *.swift | grep -v "accessibilityAction"
```

## Output Format

```markdown
✅ ACCESSIBILITY FIXES APPLIED

Fixed 5 missing labels, 2 dynamic type issues across 4 files
Build validated: SUCCESS

Manual review needed:
- StatusView.swift:67 - Color-only status indicator (add text/icon)
- CustomTabView.swift:45 - Complex gesture needs **manual VoiceOver testing by user**

Files modified: LoginView.swift, ProfileView.swift, HeaderView.swift, FormView.swift
```

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