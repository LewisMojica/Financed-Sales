# Triage Bugs with Severity-Based Prioritization
<!-- Template Version: 2 | ContextKit: 0.0.0 | Updated: 2025-09-16 -->

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

## Description
Process bugs from inbox through systematic 5-step triage with severity-based binary search positioning. Orchestrates user interaction and calls database operations defined in Bugs-Backlog.md.

## User Input Format

```
────────────────────────────────────────────────────────────────
**💬 [Insert the specific question here]**
────────────────────────────────────────────────────────────────

**Bug:** [Bug name or description]

[Additional context fields]

────────────────────────────────────────────────────────────────
```

## Execution Flow (main)

### Phase 1: Setup & Inventory

1. **Check Bug Infrastructure**
   - Use `Glob` tool to verify: `Glob Context/Backlog Bugs-Inbox.md Bugs-Backlog.md`
   - If missing files:
     ```
     ❌ Bug infrastructure incomplete!

     Missing files detected. Run /ctxk:proj:init to setup complete backlog system.
     Required: Context/Backlog/Bugs-Inbox.md and Bugs-Backlog.md
     ```
     → END (exit with error)

2. **Load Bug Inventory**
   - Use `Read` tool to read Bugs-Inbox.md: `Read Context/Backlog/Bugs-Inbox.md`
   - Parse all bugs awaiting triage (look for `## [BUG-###]` entries)
   - If no bugs in inbox:
     ```
     🐛 Bug inbox is empty!

     All bugs have been triaged. Use /ctxk:bckl:add-bug to capture new bug reports.
     Current state: Ready for development with existing backlog.
     ```
     → END (success - no work needed)

3. **Load Existing Bug Backlog Database**
   - Use `Read` tool to read Bugs-Backlog.md: `Read Context/Backlog/Bugs-Backlog.md`
   - Review documented database operations (SEVERITY_BINARY_SEARCH_INSERT, ADD_BUG_ENTRY, etc.)
   - Parse existing Priority Index for binary search reference material

### Phase 2: Systematic Bug Triage

4. **Process Each Bug from Inbox Using 5-Step Triage**
   - For each bug in Bugs-Inbox.md, execute systematic triage:

   **Step 1: Severity Assessment**
   ```
   ────────────────────────────────────────────────────────────────
   **🔥 SEVERITY: How severe is this bug's impact?**
   ────────────────────────────────────────────────────────────────

   **Bug:** [Bug Title]
   **Source:** [Reporter information]
   **Context:** [Bug description/context]

   A) Critical - App crashes, data loss, security issue
   B) High - Core functionality completely broken
   C) Medium - Feature degraded but has workarounds
   D) Low - Minor UI issue or cosmetic problem

   Choose A, B, C, or D:
   ────────────────────────────────────────────────────────────────
   ```
   - Document detailed impact analysis based on user input

   **Step 2: Effort Estimation**
   ```
   ────────────────────────────────────────────────────────────────
   **⏱️ EFFORT: How much human review/testing time would this fix require with AI assistance?**
   > *Note: Estimate AI-assisted development time (Claude Code implements fix + human reviews/tests), not manual coding time.*
   ────────────────────────────────────────────────────────────────

   **Bug:** [Bug Title]
   **Severity:** [Determined severity level]

   A) Simple - 1-3 hours *(AI-assisted)* (UI fix, text change, obvious bug)
   B) Medium - 4-12 hours *(AI-assisted)* (logic fix, single component)
   C) Complex - 1-3 days *(AI-assisted)* (architecture issue, multiple systems)
   D) Major - 1+ weeks *(AI-assisted)* (fundamental redesign required)

   Choose A, B, C, or D:
   ────────────────────────────────────────────────────────────────
   ```
   - If Major complexity: Ask if bug should be converted to feature specification
   - Document effort reasoning and any clarifications

   **Step 3: Binary Search Priority Placement (Severity-Effort Matrix)**
   - **Call SEVERITY_BINARY_SEARCH_INSERT operation from Bugs-Backlog.md**
   - Present exactly 3 reference bugs from existing Priority Index:
   ```
   ────────────────────────────────────────────────────────────────
   **📍 PRIORITY: Where does this bug rank for fixing?**
   ────────────────────────────────────────────────────────────────

   **New Bug:** [Bug Title] ([Severity], [Effort])

   A) ← Higher priority to fix
   ─────────────────────────────────
   • [Existing bug with severity/effort context]
   ─────────────────────────────────
   B) ← Between here
   ─────────────────────────────────
   • [Another existing bug with context]
   ─────────────────────────────────
   C) ← Lower priority to fix

   ────────────────────────────────────────────────────────────────
   ```
   - **Continue narrowing** until exact insertion point identified
   - **Never stop** until position between two consecutive bugs found

   **Step 4: Impact Analysis & Dependencies**
   ```
   ────────────────────────────────────────────────────────────────
   **🔗 IMPACT: Does this bug block other work or affect multiple areas?**
   ────────────────────────────────────────────────────────────────

   **Bug:** [Bug Title]
   **Priority:** [Placement decided via binary search]

   Examples:
   • "Blocks feature X development"
   • "Affects multiple customers"
   • "Related to security vulnerability"
   • "Causes other bugs as side effect"
   • "No dependencies or blocking impact"

   ────────────────────────────────────────────────────────────────
   ```
   - Document blocking relationships and cascade effects for metadata tables

   **Step 5: Finalize Using ADD_BUG_ENTRY Operation**
   - **Call ADD_BUG_ENTRY operation from Bugs-Backlog.md** with collected information:
     - Priority score from severity-effort matrix binary search
     - Severity assessment
     - Effort estimation
     - Impact analysis and dependencies
     - Source attribution
     - Full context and triage notes
   - **Remove processed item from Bugs-Inbox.md**
   - Continue with next inbox bug

### Phase 3: Session Completion & Database Maintenance

5. **Execute Session Management Operations**
   - **Call CRITICAL_ESCALATION operation** to handle any critical bugs
   - **Call SEVERITY_REBALANCE operation** if priority gaps have become too small
   - Update triage tracking information in Bugs-Backlog.md

6. **Clean Inbox and Update Status**
   - Use `Edit` tool to remove all processed bugs from Bugs-Inbox.md
   - Update "Last Triage Session" date in Bugs-Backlog.md
   - Update critical bug count and next triage due triggers

7. **Display Triage Summary**
   ```
   🐛 Bug triage complete!

   ✅ Triaged: [X] bugs from inbox
   ✅ Database operations: SEVERITY_BINARY_SEARCH_INSERT, ADD_BUG_ENTRY, [others if used]
   ✅ Updated: Context/Backlog/Bugs-Backlog.md with severity-based priorities

   📊 Summary:
   • Critical: [X] bugs requiring immediate attention
   • High: [X] bugs for next sprint
   • Medium: [X] bugs for regular development
   • Low: [X] bugs for convenient fixing

   🚨 Critical Actions Required:
   • [BUG-###] [Critical Bug Title] - [Impact description]
   • [Additional critical bugs if any]

   🔗 Next Steps:
   • Review Context/Backlog/Bugs-Backlog.md for complete prioritized list
   • Address critical bugs immediately with hotfix process
   • Plan high-priority bugs for next development sprint

   🐛 Bugs are now ready for systematic fixing!
   ```

## Severity-Effort Matrix Implementation

### Reference Bug Selection Strategy
- **Pick 3 bugs** from different severity-effort combinations in existing Priority Index
- **Include meaningful context**: severity, effort, user impact, source
- **Example format**: "Login crash (Critical, 4h, affects all users)" not just "Login bug"

### User Interaction Flow
- If user picks "A) Higher priority": Select references from higher priority range and continue
- If user picks "C) Lower priority": Select references from lower priority range and continue
- **Never terminate** until exact insertion point between consecutive bugs identified
- **Calculate severity-weighted score** using formula from SEVERITY_BINARY_SEARCH_INSERT operation

### Database Operation Calls
- **SEVERITY_BINARY_SEARCH_INSERT**: For finding exact priority position using severity-effort matrix
- **ADD_BUG_ENTRY**: For adding bug with complete triage metadata
- **CRITICAL_ESCALATION**: For handling critical bugs requiring immediate attention
- **SEVERITY_REBALANCE**: For maintaining priority score spacing within severity groups
- **REMOVE_FIXED**: If user indicates bugs are already resolved

## Severity-Effort Priority Rules

### Severity Levels
- **Critical**: App crashes, data loss, security issues, complete feature failures
- **High**: Core functionality broken, significant user impact, difficult workarounds
- **Medium**: Feature degraded but usable, minor user impact, workarounds available
- **Low**: Cosmetic issues, minor UI problems, edge cases, polish items

### Effort Classifications
- **Simple**: 1-3 hours - UI fixes, text changes, obvious bugs
- **Medium**: 4-12 hours - Logic fixes, single component changes
- **Complex**: 1-3 days - Architecture issues, multiple system fixes
- **Major**: 1+ weeks - Fundamental redesigns (consider converting to feature)

### Priority Matrix Application
- **Critical + Any Effort** = Negative scores (immediate attention via CRITICAL_ESCALATION)
- **High + Simple** = 1-10 range
- **High + Medium/Complex** = 10-20 range
- **Medium + Simple** = 20-30 range
- **Low + Any Effort** = 50-100 range

## Error Conditions

- **"Bugs-Inbox.md empty"** → No bugs to triage, suggest adding bug reports first
- **"Bugs-Backlog.md missing operations"** → Database template may be corrupted
- **"Binary search incomplete"** → Must continue until exact position found
- **"Critical bug overflow"** → Too many critical bugs may indicate systemic issues
- **"Database operation failed"** → Check Bugs-Backlog.md structure and operations

## Validation Gates

**Prerequisites:**
- Bug infrastructure files exist and are readable?
- At least one bug exists in inbox for triage?
- Bugs-Backlog.md contains documented database operations?

**Processing:**
- Each bug goes through complete 5-step triage evaluation?
- Severity and effort assessments completed for all bugs?
- Binary search continues until exact position identified?

**Output:**
- Bugs moved from inbox to backlog using documented operations?
- Priority Index maintained in correct severity-weighted order?
- Critical bugs properly flagged for immediate attention?

## Integration Points

- **Bug Capture**: Processes bugs from `/ctxk:bckl:add-bug` command
- **Database Operations**: Uses methods documented in Bugs-Backlog.md self-managing database
- **Development Workflow**: Feeds prioritized bugs to development planning
- **Session Management**: Supports session-based triage and priority reassessment
- **Source Tracking**: Preserves reporter attribution throughout triage process

════════════════════════════════════════════════════════════════════════════════
👩‍💻 DEVELOPER CUSTOMIZATIONS - EDITABLE SECTION
════════════════════════════════════════════════════════════════════════════════

This section is preserved during ContextKit migrations and updates.
Add project-specific instructions, examples, and overrides below.

## Custom Severity Rules

<!-- Add project-specific severity assessment guidelines -->

## Binary Search Customization

<!-- Modify reference bug selection or positioning logic -->

## Database Operation Overrides

<!-- Override specific database operations if needed for project -->