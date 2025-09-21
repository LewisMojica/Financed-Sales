# Capture New Ideas with Quick Dump
<!-- Template Version: 1 | ContextKit: 0.0.0 | Updated: 2025-09-15 -->

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

## Description
Quick idea capture with minimal overhead. Takes description as parameter and dumps to inbox immediately with source extraction if mentioned.

## Parameters
- `description` (required): The idea description (e.g., "Add dark mode support" or "Jack suggested export to CSV feature")

## Execution Flow (main)

### Phase 1: Setup Validation

1. **Check Ideas Infrastructure**
   - Use `Glob` tool to verify: `Glob Context/Backlog Ideas-Inbox.md`
   - If Ideas-Inbox.md missing:
     ```
     ❌ Ideas infrastructure not found!
     Run /ctxk:proj:init to setup ContextKit backlog system.
     ```
     → END (exit with error)

### Phase 2: Quick Processing

2. **Parse Description and Extract Source**
   - Take description from command parameter
   - If no description provided: ERROR "Description required: /ctxk:bckl:add-idea 'Your idea here'"
   - **Extract source if mentioned**: Look for patterns like:
     - "Jack said...", "Customer suggested...", "Sarah mentioned..."
     - "User reported...", "Support ticket mentioned..."
     - If found: Extract as source, clean description
     - If not found: Source = "Me"

3. **Generate ID and Create Entry**
   - Use `Read` tool to read Ideas-Inbox.md: `Read Context/Backlog/Ideas-Inbox.md`
   - Generate next sequential ID: IDEA-001, IDEA-002, etc.
   - Create title from description (fix obvious typos, keep intent)
   - Generate current date

4. **Add to Ideas Inbox**
   - Use `Edit` tool to add entry at top of "Ideas Awaiting Evaluation" section:
     ```markdown
     ## [IDEA-###] [Title from description]
     **Added**: YYYY-MM-DD
     **Source**: [Extracted source or "Me"]
     **Context**: [Full description if longer than title]
     ```

5. **Show Success Message**
   ```
   💡 Idea captured: [IDEA-###] [Title]
   📁 Added to Context/Backlog/Ideas-Inbox.md
   🔄 Run /ctxk:bckl:prioritize-ideas to evaluate and prioritize
   ```

## Error Conditions

- **"No description provided"** → Show usage: `/ctxk:bckl:add-idea "Your idea description"`
- **"Ideas-Inbox.md missing"** → Run `/ctxk:proj:init` to setup infrastructure
- **"File write failed"** → Check permissions and disk space

## Source Extraction Patterns

Look for these patterns in description and extract as source:
- "Jack said we need dark mode" → Source: "Jack", Description: "Dark mode support"
- "Customer reported wanting CSV export" → Source: "Customer", Description: "CSV export functionality"
- "Support ticket mentioned offline mode" → Source: "Support ticket", Description: "Offline mode"
- "Add dark mode" → Source: "Me", Description: "Dark mode support"

## Integration Points

- **Quick capture**: Minimal questions, fast entry
- **Evaluation later**: `/ctxk:bckl:prioritize-ideas` handles all assessment
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