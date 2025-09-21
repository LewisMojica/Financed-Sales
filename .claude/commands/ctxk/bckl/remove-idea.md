# Remove Completed Ideas from Backlog
<!-- Template Version: 1 | ContextKit: 0.0.0 | Updated: 2025-09-15 -->

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

## Description
Remove completed or cancelled ideas from the backlog database. Identifies target idea through search and calls database removal operations defined in Ideas-Backlog.md.

## Parameters
- `description` (required): The idea description or ID (e.g., "dark mode" or "IDEA-001")

## Execution Flow (main)

### Phase 1: Setup & Infrastructure Check

1. **Check Ideas Infrastructure**
   - Use `Glob` tool to verify: `Glob Context/Backlog Ideas-Backlog.md`
   - If Ideas-Backlog.md missing:
     ```
     ❌ Ideas backlog not found!

     Expected: Context/Backlog/Ideas-Backlog.md
     Run /ctxk:proj:init to setup ContextKit backlog system first.
     ```
     → END (exit with error)

### Phase 2: Idea Identification

2. **Parse User Input**
   - Extract search term from command parameter
   - If no description provided: ERROR "Description required: /ctxk:bckl:remove-idea 'search term or IDEA-001'"

3. **Search Existing Backlog**
   - Use `Read` tool to read Ideas-Backlog.md: `Read Context/Backlog/Ideas-Backlog.md`
   - Search Priority Index and Idea Details sections for matches
   - **Perfect ID match**: If input exactly matches "IDEA-###" format and exists, skip to confirmation
   - **Partial matches**: Search titles and descriptions for keywords

4. **Present Search Results**
   - If no matches found:
     ```
     💡 No matching ideas found for: "[search term]"

     Check Context/Backlog/Ideas-Backlog.md for available ideas.
     Use exact ID like "IDEA-001" or keywords from the idea title.
     ```
     → END (no matches)

   - If single match found: Skip to confirmation step
   - If multiple matches found: Present selection menu:
     ```
     🔍 Multiple ideas match "[search term]":

     A) [IDEA-001] Dark mode UI support (Score: 5.2, 8h effort)
     B) [IDEA-003] Dark theme for settings (Score: 15.0, 2h effort)
     C) [IDEA-007] Night mode accessibility (Score: 25.5, 4h effort)

     Which idea do you want to remove? (A/B/C or type new search)
     ```
   - Wait for user selection and validate choice

### Phase 3: Confirmation & Removal

5. **Confirm Removal Intent**
   - Present selected idea with details:
     ```
     ────────────────────────────────────────────────────────────────
     **🗑️ CONFIRM REMOVAL: Are you sure you want to remove this idea?**
     ────────────────────────────────────────────────────────────────

     **Idea**: [IDEA-###] [Title]
     **Priority Score**: [Score from backlog]
     **Effort**: [Hours estimated]
     **Source**: [Who suggested it]
     **Status**: This will be permanently removed from the backlog

     Type 'yes' to confirm removal, or anything else to cancel.
     ────────────────────────────────────────────────────────────────
     ```
   - Wait for user confirmation
   - If not confirmed: Cancel and exit gracefully

6. **Execute REMOVE_COMPLETED Operation**
   - **Call REMOVE_COMPLETED operation from Ideas-Backlog.md** with:
     - Confirmed idea ID
     - Reason for removal (completed/cancelled/implemented)
   - The backlog file handles all database cleanup operations
   - Preserve operation result for success message

7. **Display Removal Confirmation**
   ```
   ✅ Idea removed successfully!

   🗑️ Removed: [IDEA-###] [Title]
   📊 Database operations: REMOVE_COMPLETED executed
   🧹 Cleaned: Priority Index, Metadata Tables, and Idea Details

   📋 Updated backlog status:
   • Total active ideas: [Remaining count]
   • Next highest priority: [Next idea if any]

   💡 Backlog is now updated and ready for continued development!
   ```

## Search Strategy Details

### ID-Based Search
- **Exact match**: "IDEA-001" → Direct match if exists
- **Partial ID**: "001" → Search for "IDEA-001"
- **Case insensitive**: "idea-001" → Matches "IDEA-001"

### Keyword Search
- **Title matching**: Search idea titles for keywords
- **Description content**: Search context and evaluation notes
- **Source matching**: Search source attribution fields
- **Multi-word**: "dark mode" → Matches titles containing both words

### Search Results Priority
1. **Exact ID matches** (highest priority)
2. **Title keyword matches** (high priority)
3. **Description content matches** (medium priority)
4. **Source attribution matches** (lower priority)

## Error Conditions

- **"Ideas-Backlog.md missing"** → Run `/ctxk:proj:init` to setup infrastructure
- **"No description provided"** → Show usage: `/ctxk:bckl:remove-idea "search term"`
- **"No matching ideas found"** → Suggest checking backlog file or using different keywords
- **"User cancelled removal"** → Graceful exit without changes
- **"Database operation failed"** → Check Ideas-Backlog.md structure and REMOVE_COMPLETED operation

## Validation Gates

**Prerequisites:**
- Ideas backlog infrastructure exists and is readable?
- User provided meaningful search term or ID?
- Ideas-Backlog.md contains REMOVE_COMPLETED operation?

**Processing:**
- Search identified at least one matching idea?
- User confirmed removal of correct idea?
- REMOVE_COMPLETED operation executed successfully?

**Output:**
- Idea removed from all backlog database sections?
- Database integrity maintained after removal?
- User informed of successful removal and updated status?

## Integration Points

- **Database Operations**: Uses REMOVE_COMPLETED method documented in Ideas-Backlog.md self-managing database
- **Search & Discovery**: Flexible search across ID, title, description, and source fields
- **User Safety**: Confirmation step prevents accidental removals
- **Status Tracking**: Updates overall backlog metrics after removal

════════════════════════════════════════════════════════════════════════════════
👩‍💻 DEVELOPER CUSTOMIZATIONS - EDITABLE SECTION
════════════════════════════════════════════════════════════════════════════════

This section is preserved during ContextKit migrations and updates.
Add project-specific instructions, examples, and overrides below.

## Custom Search Patterns

<!-- Add project-specific search keyword patterns -->

## Removal Confirmation Overrides

<!-- Modify confirmation flow if needed for project -->

## Database Operation Customizations

<!-- Override REMOVE_COMPLETED behavior if needed -->