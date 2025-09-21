# Capture Bug Reports with Quick Dump
<!-- Template Version: 1 | ContextKit: 0.0.0 | Updated: 2025-09-15 -->

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

## Description
Quick bug capture with minimal overhead. Takes description as parameter and dumps to inbox immediately with source extraction if mentioned.

## Parameters
- `description` (required): The bug description (e.g., "Login crashes on iOS 18" or "Customer reported export button broken")

## Execution Flow (main)

### Phase 1: Setup Validation

1. **Check Bug Infrastructure**
   - Use `Glob` tool to verify: `Glob Context/Backlog Bugs-Inbox.md`
   - If Bugs-Inbox.md missing:
     ```
     ❌ Bug infrastructure not found!
     Run /ctxk:proj:init to setup ContextKit backlog system.
     ```
     → END (exit with error)

### Phase 2: Quick Processing

2. **Parse Description and Extract Source**
   - Take description from command parameter
   - If no description provided: ERROR "Description required: /ctxk:bckl:add-bug 'Bug description here'"
   - **Extract source if mentioned**: Look for patterns like:
     - "Customer reported...", "User said...", "QA found..."
     - "Support ticket...", "Jack mentioned...", "Sarah noticed..."
     - If found: Extract as source, clean description
     - If not found: Source = "Me"

3. **Generate ID and Create Entry**
   - Use `Read` tool to read Bugs-Inbox.md: `Read Context/Backlog/Bugs-Inbox.md`
   - Generate next sequential ID: BUG-001, BUG-002, etc.
   - Create title from description (fix obvious typos, keep intent)
   - Generate current date

4. **Add to Bug Inbox**
   - Use `Edit` tool to add entry at top of "Bugs Awaiting Triage" section:
     ```markdown
     ## [BUG-###] [Title from description]
     **Added**: YYYY-MM-DD
     **Source**: [Extracted source or "Me"]
     **Context**: [Full description if longer than title]
     ```

5. **Show Success Message**
   ```
   🐛 Bug captured: [BUG-###] [Title]
   📁 Added to Context/Backlog/Bugs-Inbox.md
   🔄 Run /ctxk:bckl:prioritize-bugs to triage and prioritize
   ```

## Error Conditions

- **"No description provided"** → Show usage: `/ctxk:bckl:add-bug "Bug description"`
- **"Bugs-Inbox.md missing"** → Run `/ctxk:proj:init` to setup infrastructure
- **"File write failed"** → Check permissions and disk space

## Source Extraction Patterns

Look for these patterns in description and extract as source:
- "Customer reported login crashes" → Source: "Customer", Description: "Login crashes"
- "QA found export button broken" → Source: "QA team", Description: "Export button broken"
- "Jack mentioned dark mode issues" → Source: "Jack", Description: "Dark mode issues"
- "Login crashes on iOS 18" → Source: "Me", Description: "Login crashes on iOS 18"

## Integration Points

- **Quick capture**: Minimal questions, fast entry
- **Triage later**: `/ctxk:bckl:prioritize-bugs` handles all impact assessment
- **Source tracking**: Basic attribution for follow-up

════════════════════════════════════════════════════════════════════════════════
👩‍💻 DEVELOPER CUSTOMIZATIONS - EDITABLE SECTION
════════════════════════════════════════════════════════════════════════════════

This section is preserved during ContextKit migrations and updates.
Add project-specific instructions, examples, and overrides below.

## Custom Source Patterns

<!-- Add project-specific source extraction patterns -->

## Quick Capture Rules

<!-- Add project-specific rapid entry customizations -->