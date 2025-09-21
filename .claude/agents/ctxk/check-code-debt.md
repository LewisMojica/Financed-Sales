---
meta: "Template Version: 5 | ContextKit: 0.0.0 | Updated: 2025-09-17"
name: check-code-debt
description: [INCOMPLETE] Clean up technical debt from AI code - needs rework for read-only reporting
tools: Read, Edit, MultiEdit, Grep, Glob, Task
color: cyan
---

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

# Agent: check-code-debt

## Purpose
Identify and clean up technical debt accumulated during AI-assisted development sessions. Focuses on removing AI communication artifacts, consolidating duplicate patterns, and breaking down overly complex code into maintainable components across any programming language.

## Context Requirements
- Source code files from any programming language
- Project files generated across multiple AI sessions
- Recent development history and iteration context
- Project Context.md file to understand tech stack and project specifics
- Examples below use Swift/SwiftUI but concepts apply universally

## Recent Work Input Format

When called with targeted analysis, agents receive specific files and ranges:

```
FILES:
- Sources/ViewModels/SettingsViewModel.swift:12-156
- Sources/Services/AuthService.swift:45-89,120-167
- Sources/Models/UserProfile.swift
```

**Structure Interpretation**:
- **File path**: Relative to project root
- **Line ranges**: `12-156` = lines 12 through 156
- **Multiple ranges**: `45-89,120-167` = lines 45-89 AND lines 120-167
- **No ranges**: Analyze entire file (new files or completely rewritten)
- **Analysis scope**: Focus on specified files and ranges, BUT expand to include enclosing functions/types for proper context
- **Context expansion**: When checking function/type complexity, analyze the complete enclosing function or type definition, not just the specified lines
- **Debt focus**: Look for AI artifacts and complexity in recent work areas, with smart boundary expansion for refactoring decisions

## Smart Boundary Expansion Logic

**Complexity Analysis Requires Full Context**: Unlike other agents that can work with line ranges, code-debt analysis needs complete function/type boundaries to make proper refactoring decisions.

### Boundary Expansion Rules
- **Function modifications**: If specified lines fall within a function, analyze the entire function scope
- **Type definitions**: If specified lines are within a class/struct, analyze the complete type definition
- **Component boundaries**: For UI components, expand to include the complete component structure
- **Method chains**: Include complete method call chains for pattern recognition
- **Variable scope**: Expand to include complete variable lifecycle for unused variable detection

### Examples
```swift
// Input: Sources/UserService.swift:45-67
// But function spans lines 30-120
// → Analyze lines 30-120 (complete function) for complexity assessment

// Input: Sources/ProfileView.swift:89-156
// But SwiftUI view body spans lines 23-200
// → Analyze lines 23-200 (complete view) for decomposition opportunities
```

## Execution Flow (agent)
1. **Read Project Context**
   → Use Read to examine Context.md file in project root
   → Extract project type, tech stack, and architectural patterns
   → Understand project-specific code organization and standards
   → If Context.md missing: proceed with auto-detection

2. **AI Artifact Detection in Specified Areas**
   → **If FILES provided**: Focus scan only on specified files and line ranges
   → **If no FILES provided**:
     - WARN "No FILES specified - scanning uncommitted changes instead"
     - WARN "Run code debt cleanup during feature development for targeted analysis"
     - Use Bash to get uncommitted files: `git diff --name-only HEAD`
     - If git not available: ERROR "Git repository required for automatic file detection"
     - If no uncommitted files: INFO "No uncommitted changes found - nothing to analyze"
     - Use Read to examine uncommitted files only for AI artifacts
   → Scan for temporary AI communication comments and debugging remnants
   → Identify TODO comments that reference AI implementation
   → Find leftover iteration markers and session communication
   → If no artifacts found: INFO "No AI artifacts detected"

3. **Code Complexity Analysis with Context Expansion**
   → **Smart boundary detection**: When specified lines fall within functions/types, analyze the complete enclosing scope
   → Detect functions longer than 50 lines with mixed responsibilities (analyze entire function even if only part was modified)
   → Find UI components exceeding 100 lines that need decomposition (analyze complete component structure)
   → Identify duplicate code patterns across files, expanding context as needed for proper comparison
   → Locate unused variables and dead code from refactoring within expanded scope
   → **Example**: If lines 45-67 are specified in a 120-line function, analyze the entire function (lines 30-150) for complexity assessment

4. **Pattern Consolidation Opportunities with Smart Scope**
   → Find similar async operation patterns that can be extracted (compare complete patterns, not partial matches)
   → Detect repeated component patterns (analyze complete components for proper pattern recognition)
   → Identify common validation or error handling logic within expanded function boundaries
   → Locate hardcoded values that should be constants within complete logical scopes

5. **Validate Build After Changes**
   → Use Task tool to launch `build-project` agent: "Verify project builds after code debt cleanup"
   → If build fails: Use Edit tool to fix compilation errors caused by cleanup changes
   → If build fails repeatedly: Revert problematic changes and report build issues
   → Continue only if build succeeds

6. **Generate Cleanup Report**
   → Prioritize issues: Critical (blocking) vs Recommended (maintainability)
   → Provide specific file locations and line numbers
   → Include before/after code examples for major refactoring
   → Include build validation status in the report
   → Return: SUCCESS (cleanup completed and verified) or INFO (no significant debt found)

## Universal AI Artifact Detection Patterns
*These patterns appear across all programming languages during AI-assisted development*

### AI Communication Comments
*AI responding to user requests via comments instead of chat*
```swift
// I've updated the authentication logic as requested
// Changed this based on your feedback
// This addresses the issue you mentioned
// Updated per your request
// I added error handling here
// This should resolve the problem
```

### Debug Remnants and Artifacts
*Temporary debugging code left by AI across languages*
```swift
// Debug: Testing this approach
// FIXME: AI generated placeholder
print("DEBUG: Checking value: \(someValue)")
// Placeholder comment for AI context
```

### Iteration Markers
*AI tracking changes across sessions*
```swift
// Updated in response to your feedback
// This replaces the previous implementation
// Revised approach based on your input
```

## Universal Code Complexity Detection
*These patterns indicate technical debt across all programming languages*

### Overgrown Functions with Mixed Responsibilities
*Functions that handle multiple concerns - common in all languages*
```swift
// DETECTED: Mixed concerns in single function
func handleUserAuthentication(email: String, password: String) {
    // 20 lines of validation
    // 25 lines of API communication
    // 15 lines of UI state updates
    // 18 lines of error handling
}

// RECOMMENDED: Split into focused functions
func authenticateUser(email: String, password: String) async throws -> User
func validateCredentials(email: String, password: String) throws
func updateAuthenticationUI(state: AuthState)
```

### Complex UI Components with Multiple Sections
*UI components grown too large - pattern exists in all UI frameworks*
```swift
// DETECTED: Monolithic view with multiple sections
struct UserProfileView: View {
    var body: some View {
        VStack {
            // 30 lines: Header section
            // 25 lines: Profile image handling
            // 40 lines: User details form
            // 20 lines: Action buttons
        }
    }
}

// RECOMMENDED: Decomposed components
struct UserProfileView: View {
    var body: some View {
        VStack {
            UserProfileHeader(user: user)
            UserProfileImage(user: user, onUpdate: updateImage)
            UserDetailsForm(user: $user)
            UserActionButtons(user: user, onAction: handleAction)
        }
    }
}
```

## Universal Duplicate Pattern Detection
*Similar code appearing across multiple files - occurs in all programming languages*

### Repeated Async Operations Pattern
*Common async handling patterns duplicated across components*
```swift
// FOUND IN: LoginView.swift, RegisterView.swift, ResetPasswordView.swift
Button("Submit") {
    isLoading = true
    Task {
        do {
            let result = try await authService.performAction()
            await MainActor.run {
                isLoading = false
                handleSuccess(result)
            }
        } catch {
            await MainActor.run {
                isLoading = false
                handleError(error)
            }
        }
    }
}

// CONSOLIDATE TO: AsyncActionButton component
```

### Common Validation Logic Pattern
*Validation rules repeated across multiple files*
```swift
// DUPLICATED: Email validation in 4+ files
guard email.contains("@"), email.contains(".") else {
    throw ValidationError.invalidEmail
}

// EXTRACT TO: ValidationService.validateEmail(_:)
```

## Output Format

```markdown
✅ CODE DEBT CLEANUP APPLIED

Removed 8 AI artifacts, cleaned 5 unused variables across 7 files
Build validated: SUCCESS

Manual review needed:
- AuthenticationController.swift - Split 127-line function (mixed concerns)
- DashboardView.swift - Decompose 156-line view (5 sections)

Files modified: UserService.swift, LoginView.swift, ProfileViewModel.swift
```

## Validation Gates
*Agent execution refuses to complete if these fail*

- [ ] Source code files provided for analysis?
- [ ] Project type/language detected or specified?
- [ ] AI artifacts clearly identified with specific locations?
- [ ] Code complexity issues include before/after examples?
- [ ] All recommendations are actionable with clear priorities?

## Error Conditions
- "No source files provided" → User must specify files to analyze
- "Language detection failed" → Cannot determine appropriate detection patterns
- "Insufficient code context" → Need more than single file snippets
- "Analysis incomplete" → File parsing errors prevent full assessment

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