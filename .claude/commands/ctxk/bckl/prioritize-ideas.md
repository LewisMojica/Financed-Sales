# Prioritize Ideas with Binary Search Evaluation
<!-- Template Version: 2 | ContextKit: 0.0.0 | Updated: 2025-09-16 -->

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

## Description
Process ideas from inbox through systematic 5-step evaluation with binary search priority placement. Orchestrates user interaction and calls database operations defined in Ideas-Backlog.md.

## User Input Format

```
────────────────────────────────────────────────────────────────
**💬 [Insert the specific question here]**
────────────────────────────────────────────────────────────────

**Idea:** [Idea name or description]

[Additional context fields]

────────────────────────────────────────────────────────────────
```

## Execution Flow (main)

### Phase 1: Setup & Inventory

1. **Check Ideas Infrastructure**
   - Use `Glob` tool to verify: `Glob Context/Backlog Ideas-Inbox.md Ideas-Backlog.md`
   - If missing files:
     ```
     ❌ Ideas infrastructure incomplete!

     Missing files detected. Run /ctxk:proj:init to setup complete backlog system.
     Required: Context/Backlog/Ideas-Inbox.md and Ideas-Backlog.md
     ```
     → END (exit with error)

2. **Load Ideas Inventory**
   - Use `Read` tool to read Ideas-Inbox.md: `Read Context/Backlog/Ideas-Inbox.md`
   - Parse all ideas awaiting evaluation (look for `## [IDEA-###]` entries)
   - If no ideas in inbox:
     ```
     💡 Ideas inbox is empty!

     All ideas have been processed. Use /ctxk:bckl:add-idea to capture new ideas.
     Current state: Ready for development with existing backlog.
     ```
     → END (success - no work needed)

3. **Load Existing Backlog Database**
   - Use `Read` tool to read Ideas-Backlog.md: `Read Context/Backlog/Ideas-Backlog.md`
   - Review documented database operations (BINARY_SEARCH_INSERT, ADD_ENTRY, etc.)
   - Parse existing Priority Index for binary search reference material

### Phase 2: Systematic Idea Processing

4. **Process Each Idea from Inbox Using 5-Step Evaluation**
   - For each idea in Ideas-Inbox.md, execute systematic evaluation:

   **Step 1: Effort Assessment**
   ```
   ────────────────────────────────────────────────────────────────
   **⏱️ EFFORT: How many hours of human review/testing time with AI assistance?**
   > *Note: Estimate AI-assisted development time (Claude Code implements + human reviews), not manual coding time.*
   ────────────────────────────────────────────────────────────────

   **Idea:** [Idea Title]
   **Source:** [Source attribution]
   **Context:** [Idea description/context]

   ────────────────────────────────────────────────────────────────
   ```
   - If >4 hours: Ask "This seems large. Should we split it into smaller pieces?"
   - Document effort assessment and any splitting decisions

   **Step 2: Deadline Assessment**
   ```
   ────────────────────────────────────────────────────────────────
   **📅 DEADLINE: Does this have a deadline or time-sensitive requirement?**
   ────────────────────────────────────────────────────────────────

   **Idea:** [Idea Title]
   **Effort:** ~[X] hours *(AI-assisted)*

   ────────────────────────────────────────────────────────────────
   ```
   - Document deadline requirements for DEADLINE_BUBBLE_UP operation

   **Step 3: Binary Search Priority Placement**
   - **Call BINARY_SEARCH_INSERT operation from Ideas-Backlog.md**
   - Present exactly 3 reference ideas from existing Priority Index:
   ```
   ────────────────────────────────────────────────────────────────
   **📍 PRIORITY: Where would you place this idea?**
   ────────────────────────────────────────────────────────────────

   **New Idea:** [Idea Title] ([Effort], [Source])

   A) ← Higher priority
   ─────────────────────────────────
   • [Existing idea with context (effort, source)]
   ─────────────────────────────────
   B) ← Between here
   ─────────────────────────────────
   • [Another existing idea with context]
   ─────────────────────────────────
   C) ← Lower priority

   ────────────────────────────────────────────────────────────────
   ```
   - **Continue narrowing** until exact insertion point identified
   - **Never stop** until position between two consecutive ideas found

   **Step 4: Dependencies and Grouping**
   ```
   ────────────────────────────────────────────────────────────────
   **🔗 DEPENDENCIES: Does this depend on any other ideas, or would it work well grouped with anything?**
   ────────────────────────────────────────────────────────────────

   **Idea:** [Idea Title]
   **Priority:** [Placement decided via binary search]

   ────────────────────────────────────────────────────────────────
   ```
   - Document dependencies for metadata tables

   **Step 5: Finalize Using ADD_ENTRY Operation**
   - **Call ADD_ENTRY operation from Ideas-Backlog.md** with collected information:
     - Priority score from binary search
     - Effort assessment
     - Deadline information (if any)
     - Dependencies
     - Source attribution
     - Full context and evaluation notes
   - **Remove processed item from Ideas-Inbox.md**
   - Continue with next inbox item

### Phase 3: Session Completion & Database Maintenance

5. **Execute Session Management Operations**
   - **Call DEADLINE_BUBBLE_UP operation** to check for urgent deadlines
   - **Call REBALANCE_SCORES operation** if priority gaps have become too small
   - Update session tracking information in Ideas-Backlog.md

6. **Clean Inbox and Update Status**
   - Use `Edit` tool to remove all processed ideas from Ideas-Inbox.md
   - Update "Last Priority Session" date in Ideas-Backlog.md
   - Calculate next review due date (7 days or when >5 new ideas)

7. **Display Session Summary**
   ```
   💡 Ideas prioritization complete!

   ✅ Processed: [X] ideas from inbox
   ✅ Database operations: BINARY_SEARCH_INSERT, ADD_ENTRY, [others if used]
   ✅ Updated: Context/Backlog/Ideas-Backlog.md with new priorities

   📊 Summary:
   • [X] ideas added to active backlog
   • Highest priority: [IDEA-###] [Title] (Score: [X])
   • [If deadlines exist] Urgent items: [count] ideas with approaching deadlines
   • Next review due: [Date] (7 days) or when >5 new ideas captured

   🔗 Next Steps:
   • Review Context/Backlog/Ideas-Backlog.md for complete prioritized list
   • Use /ctxk:plan:1-spec to begin work on highest priority ideas
   • Continue capturing new ideas with /ctxk:bckl:add-idea

   💡 Ideas are now ready for development planning!
   ```

## Binary Search Implementation Details

### Reference Selection Strategy
- **Pick 3 ideas** from different priority ranges in existing Priority Index
- **Include meaningful context**: effort estimate, source, deadline info
- **Example format**: "Dark mode UI support (8h, customer requests)" not just "Dark mode"

### User Interaction Flow
- If user picks "A) Higher priority": Select references from higher range and continue
- If user picks "C) Lower priority": Select references from lower range and continue
- **Never terminate** until exact insertion point between consecutive items identified
- **Calculate precise score** using formula from BINARY_SEARCH_INSERT operation

### Database Operation Calls
- **BINARY_SEARCH_INSERT**: For finding exact priority position
- **ADD_ENTRY**: For adding idea with complete metadata
- **DEADLINE_BUBBLE_UP**: For promoting urgent deadlines
- **REBALANCE_SCORES**: For maintaining priority score spacing
- **REMOVE_COMPLETED**: If user indicates ideas are already implemented

## Error Conditions

- **"Ideas-Inbox.md empty"** → No ideas to process, suggest adding ideas first
- **"Ideas-Backlog.md missing operations"** → Database template may be corrupted
- **"Binary search incomplete"** → Must continue until exact position found
- **"User abandoned session"** → Partially processed ideas remain in inbox
- **"Database operation failed"** → Check Ideas-Backlog.md structure and operations

## Validation Gates

**Prerequisites:**
- Ideas infrastructure files exist and are readable?
- At least one idea exists in inbox for processing?
- Ideas-Backlog.md contains documented database operations?

**Processing:**
- Each idea goes through complete 5-step evaluation?
- Binary search continues until exact position identified?
- Database operations called with complete information?

**Output:**
- Ideas moved from inbox to backlog using documented operations?
- Priority Index maintained in correct sorted order?
- Session tracking information updated properly?

## Integration Points

- **Idea Capture**: Processes ideas from `/ctxk:bckl:add-idea` command
- **Database Operations**: Uses methods documented in Ideas-Backlog.md self-managing database
- **Development Workflow**: Feeds prioritized ideas to `/ctxk:plan:1-spec` for specification
- **Session Management**: Supports session-based priority reassessment and context changes
- **Source Tracking**: Preserves source attribution throughout prioritization process

════════════════════════════════════════════════════════════════════════════════
👩‍💻 DEVELOPER CUSTOMIZATIONS - EDITABLE SECTION
════════════════════════════════════════════════════════════════════════════════

This section is preserved during ContextKit migrations and updates.
Add project-specific instructions, examples, and overrides below.

## Custom Priority Factors

<!-- Add project-specific priority weighting rules -->

## Binary Search Customization

<!-- Modify reference idea selection or positioning logic -->

## Database Operation Overrides

<!-- Override specific database operations if needed for project -->