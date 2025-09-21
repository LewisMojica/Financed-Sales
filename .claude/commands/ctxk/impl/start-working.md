# Begin Development with Context
<!-- Template Version: 7 | ContextKit: 0.0.0 | Updated: 2025-09-17 -->

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

## Description
Begin systematic development with context-aware setup, task analysis, and guided implementation initiation based on completed planning phases.

## User Input Format

```
═══════════════════════════════════════════════════
║ ❓ USER INPUT REQUIRED - [Topic]
═══════════════════════════════════════════════════
║
║ [Question and context]
║
║ [Response instruction]
```

## Execution Flow (main)

### Phase 1: Prerequisites & Feature Detection

1. **Check Project Setup**
   - Use `Glob` tool to verify Context.md exists: `Glob . Context.md`
   - If Context.md missing:
     ```
     ❌ ContextKit not initialized in this project!

     Run /ctxk:proj:init first to setup ContextKit in this project.
     This command requires project context for systematic development.
     ```
     → END (exit with error)

2. **Detect Current Feature from Git Branch**
   ```bash
   git branch --show-current || echo "⚠️ Not in git repository or no current branch"
   ```
   - If branch format is `feature/[prefix]-[kebab-case-name]`:
     - Extract full name from branch (e.g., `feature/001-visionos26-modernization` → `001-visionos26-modernization`)
     - Set FEATURE_NAME variable for directory matching
   - If not on feature branch:
     ```
     ⚠️ Not on a feature branch!

     Current branch: [current_branch_name]

     Expected: feature/[prefix]-[feature-name] branch from /ctxk:plan:1-spec

     Switch to feature branch or create one with /ctxk:plan:1-spec
     Continue anyway? (y/N):
     ```
     - Wait for user confirmation
     - If "N" or no response: EXIT
     - If "y": Ask user to specify feature name manually

3. **Validate Feature Planning Completion**
   - Use `Bash` tool to find numbered feature directory with flexible matching:
     ```bash
     # Try exact full name match first
     FEATURE_DIR=$(ls -d Context/Features/*/ | grep -i "[FEATURE_NAME]" | head -1)
     # If no match, try number-based matching (extract prefix number)
     if [[ -z "$FEATURE_DIR" ]]; then
       PREFIX=$(echo "[FEATURE_NAME]" | cut -d'-' -f1)
       FEATURE_DIR=$(ls -d Context/Features/${PREFIX}-*/ 2>/dev/null | head -1)
     fi
     ```
   - Expected format: `Context/Features/###-FeatureName/` (e.g., `001-VisionOS26Modernization/`)
   - Handles variations between prefixed kebab-case branch names and numbered PascalCase directory names
   - Use `Read` tool to check each required file exists and has content:
     ```bash
     ls -la [numbered-feature-directory]/Spec.md && echo "✅ Spec.md exists"
     ls -la [numbered-feature-directory]/Tech.md && echo "✅ Tech.md exists"
     ls -la [numbered-feature-directory]/Steps.md && echo "✅ Steps.md exists"
     ```
   - Use `Read` tool to verify Steps.md contains task breakdown (not empty placeholder)
   - If any file missing or empty:
     ```
     ❌ Feature planning incomplete!

     Missing or empty files detected:
     [List missing files]

     Complete the planning phases first:
     1. /ctxk:plan:1-spec - Business requirements
     2. /ctxk:plan:2-research-tech - Technical research and architecture
     3. /ctxk:plan:3-steps - Implementation tasks

     Cannot proceed with development until planning is complete.
     ```
     → END (exit with error)

### Phase 2: Context Loading & Environment Setup

4. **Load Development Context**
   - Use `Read` tool to read project Context.md: `Read Context.md`
   - Extract project type, architecture patterns, and coding standards
   - Use `Bash` tool to check for workspace context:
     ```bash
     cd .. && find . -name "Context.md" -path "*/Context.md" | head -1 || echo "No workspace context found"
     ```
   - If workspace Context.md found: Use `Read` tool to load workspace-specific overrides

5. **Verify Development Environment**
   ```bash
   git status --porcelain || echo "⚠️ Git not available"
   ```
   - If uncommitted changes exist:
     ```
     ⚠️ Uncommitted changes detected!

     You have uncommitted work that might be overwritten during development.
     Commit or stash changes before starting new development work.

     Continue anyway? (y/N):
     ```
     - Wait for user confirmation
     - If "N": EXIT (recommend committing first)
     - If "y": Continue with warning


### Phase 3: Task Analysis & Sequential Execution

6. **Load Complete Feature Context**
   - Use `Read` tool to read all planning files for full context:
     ```
     Read [numbered-feature-directory]/Spec.md     # Business requirements and user stories
     Read [numbered-feature-directory]/Tech.md     # Technical architecture and decisions
     Read [numbered-feature-directory]/Steps.md    # Implementation task breakdown
     ```
   - Extract key information:
     - **From Spec.md**: Feature purpose, user stories, acceptance criteria
     - **From Tech.md**: Architecture decisions, technology choices, constraints
     - **From Steps.md**: Task list, dependencies, S001-S999 numbered tasks with [P] parallel markers
   - Parse task completion status (checked/unchecked boxes)

7. **Determine Next Sequential Task**
   - Find the **first uncompleted task** in S001, S002, S003... sequence
   - Do NOT skip tasks based on complexity or manual requirements
   - Check dependencies are satisfied:
     - Extract "Dependencies: S001, S002" from task description
     - Verify all dependency tasks are completed (checked boxes)
     - If dependencies not met: Display which tasks need completion first
   - **CRITICAL**: Follow the planned sequence, don't auto-select "easier" tasks
   - If no valid next task: Display completion status and next steps

8. **Handle Task Execution Based on Type**

   **For MANUAL REQUIRED Tasks** (marked with ⚠️ MANUAL REQUIRED):

   **CRITICAL**: Always use the standardized user input box format below - never use custom formatting for manual tasks:

   ```
   ═══════════════════════════════════════════════════
   ║ 👤 MANUAL TASK REQUIRED - [TaskNumber]
   ═══════════════════════════════════════════════════
   ║
   ║ 📋 TASK: [TaskDescription]
   ║ 📂 Files: [file_paths or "Xcode project settings" for Xcode tasks]
   ║ 🛠️ Manual steps required:
   ║ [Extract detailed manual instructions from task notes]
   ║
   ║ 📝 CONTEXT:
   ║ • Feature: [brief_spec_summary]
   ║ • Why needed: [brief_reason_from_tech_context]
   ║ • Current progress: [completed_tasks]/[total_tasks] tasks done
   ║
   ║ Please complete this manual task, then return here.
   ║
   ║ Options:
   ║ ✅ 'done' - I completed the manual task
   ║ ⏭️  'skip' - Skip this task for now (breaks sequence)
   ║ ❓ 'help' - Show detailed instructions
   ║ 🔙 'back' - Return to task selection
   ║
   ║ Status:
   ```

   **IMPORTANT**:
   - Do NOT use custom formats like "⏺ Starting with..." or "⚠️ Manual Xcode Configuration Required"
   - Always use the exact user input box format above with ║ line prefixes
   - All manual task communication must follow this standardized format
   - If "back": Return to task analysis phase

   **For AUTOMATED Tasks** (no manual markers):

   **CRITICAL**: Always use the standardized user input box format below - never use custom formatting:
   ```
   ═══════════════════════════════════════════════════
   ║ 🚀 AUTOMATED TASK - [TaskNumber]
   ═══════════════════════════════════════════════════
   ║
   ║ 📋 TASK: [TaskDescription]
   ║ 📂 Files to modify: [file_paths]
   ║ 🎯 Acceptance criteria: [criteria_summary]
   ║
   ║ 📝 CONTEXT SUMMARY:
   ║ • Feature: [brief_spec_summary]
   ║ • Architecture: [brief_tech_summary]
   ║ • Current progress: [completed_tasks]/[total_tasks] tasks done
   ║
   ║ 🔧 IMPLEMENTATION APPROACH:
   ║ [Brief description of what will be implemented]
   ║
   ║ Ready to implement automatically? (Y/n):
   ```

   **IMPORTANT**:
   - Do NOT use custom formats like "⏺ Starting with..."
   - Always use the exact user input box format above with ║ line prefixes
   - All automated task communication must follow this standardized format
   - Wait for user confirmation
   - If "n": Ask for alternative approach or skip
   - If "Y": Continue to automated implementation

### Phase 4: Task Execution & Progress Tracking

9. **Execute Task Implementation**
   - **For Manual Tasks**: User delegation complete, mark as done
   - **For Automated Tasks**: Proceed with implementation:
     - Extract detailed task information: file paths, acceptance criteria, dependencies
     - Use `Read` tool to examine target files if they exist
     - Identify constitutional principles relevant to task type (UI, models, services, etc.)
     - Show current task description and acceptance criteria
     - Display relevant file paths and expected changes
     - Reference appropriate guidelines based on project type:
       - iOS/macOS App projects → `Context/Guidelines/Swift.md` and `Context/Guidelines/SwiftUI.md`
       - Swift Package projects → `Context/Guidelines/Swift.md`
     - Display constitutional reminders for current task type
     - Provide starting guidance based on project patterns
     - Begin implementation work

10. **Update Progress Tracking**
    - Mark completed task as checked in Steps.md: `- [x] **S001**...`
    - Add completion timestamp in task notes if desired
    - Save progress to maintain state

11. **Continue Sequential Execution**
    - After task completion, automatically check for next sequential task
    - **Do not exit** - continue with next task in sequence
    - Display progress update:
    ```
    ✅ Task [TaskNumber] completed successfully!

    📊 Progress: [completed_tasks+1]/[total_tasks] tasks done
    🔄 Checking next sequential task...
    ```
    - Return to Phase 3, Step 7 to determine next task
    - **Only exit when**:
      - All tasks completed
      - Dependency blocking (cannot proceed)
      - User explicitly requests to stop

12. **Quality Assurance Integration with Targeted Context**
    - **After completing any step or significant changes**: Run systematic quality validation with targeted file analysis
    - **Context Passing**: Provide recently modified files and line ranges to focus agent analysis

    **Example Agent Calls**:
    ```
    Use Task tool with build-project:
    "Execute project build and report status."

    <!-- TODO: check-* agents currently disabled (untested, need rework to read-only)
    Use Task tool with check-modern-code:
    "Check for outdated patterns in recent code.

    FILES:
    - Sources/Services/AuthService.swift:23-89,145-201
    - Sources/Models/User.swift:45-78
    - Sources/Views/LoginView.swift

    Focus analysis on these specific areas only."

    Use Task tool with check-accessibility:
    "Check accessibility issues in recent UI changes.

    FILES:
    - Sources/Views/ProfileView.swift:34-156
    - Sources/Components/CustomButton.swift

    Focus analysis on these specific areas only."
    -->
    ```

    - **Execution Order** (run sequentially, stop and fix if any fail):
      1. `build-project` - Verify compilation (project-wide)
      <!-- TODO: check-* agents incomplete - need rework to read-only reporting
      2. `check-modern-code` - Modernize APIs (recent files only) [INCOMPLETE]
      3. `check-error-handling` - Validate error patterns (recent files only) [INCOMPLETE]
      4. `check-accessibility` - Check UI accessibility (recent UI files only) [INCOMPLETE]
      5. `check-localization` - Verify localization (recent UI files only) [INCOMPLETE]
      6. `check-code-debt` - Clean up artifacts (recent files only) [INCOMPLETE]
      -->

    - **Optional Testing Agents** (use when working on tests or before releases):
      - `run-specific-test` - When debugging a failing test or validating new test code
      - `run-test-suite` - Before package releases or after significant changes to verify full test coverage

    - **File Context Rules**:
      - Include entire function ranges for significant modifications (60%+ changed)
      - Provide full file paths for new or completely rewritten files
      - Merge nearby line ranges (e.g., 23-25,27-29 → 23-29)
      - Focus agents only on recently modified code, not entire codebase

    - **When to run**: After completing views, features, models with user-facing content, or any substantial code changes
    - **If agents fail**: Focus on fixing the specific issue before continuing, then re-run the failed agent to verify the fix

## Error Conditions

- **"Context.md not found"** → User must run `/ctxk:proj:init` to initialize ContextKit
- **"Not on feature branch"** → Create feature branch with `/ctxk:plan:1-spec` or switch to existing one
- **"Planning phases incomplete"** → Complete `/ctxk:plan:1-spec`, `/ctxk:plan:2-research-tech`, `/ctxk:plan:3-steps` sequence
- **"No feature directory found"** → Feature name detection failed, verify branch name format
- **"Steps.md empty"** → Run `/ctxk:plan:3-steps` to create implementation breakdown
- **"Build environment broken"** → Resolve dependency issues before starting development
- **"All tasks complete"** → No pending work, consider `/ctxk:impl:commit-changes` or new feature

## Validation Gates

**Prerequisites:**
- ContextKit project setup complete?
- Git repository with feature branch active?
- All planning phases completed (Spec.md, Tech.md, Steps.md)?
- Development environment verified and functional?

**Context Loading:**
- Project and workspace context loaded successfully?
- Constitutional principles identified for project type?
- Development patterns and standards accessible?

**Task Selection:**
- Implementation plan parsed successfully?
- Valid task selected with clear acceptance criteria?
- Task dependencies satisfied and ready for execution?

**Development Ready:**
- Quality assurance hooks enabled?
- Relevant guidelines referenced for task type?
- Development guidance displayed and ready to proceed?
- User confirmation received for selected task and approach?

## Integration Points

- **Planning Commands**: Requires completed `/ctxk:plan:1-spec`, `/ctxk:plan:2-research-tech`, `/ctxk:plan:3-steps` workflow
- **Project Setup**: Uses Context.md from `/ctxk:proj:init` for project type detection and standards
- **Quality Agents**: Integrates with `build-project`, `run-test-*` agents (ready). `/run check-*` agents incomplete - pending rework
- **Workspace Context**: Inherits client-specific requirements from workspace-level Context.md files
- **Git Workflow**: Works within feature branch structure established by planning commands
- **Development Hooks**: Enables PostToolUse formatting and SessionStart version checking
- **Task Tracking**: Updates Steps.md progress tracking for systematic development workflow

## Success Messages

### Development Session Started
```
🚀 Development session started for [FeatureName]

📋 Current Task: [TaskNumber] [TaskDescription]
📂 Files to modify: [file_paths]
📖 Guidelines: Context/Guidelines/[RelevantGuideline].md

⚡ Quality validation runs automatically after substantial changes:
   build-project → [check-* agents incomplete pending rework]

💡 Ready to implement!
```

### All Tasks Complete
```
🎉 Feature [FeatureName] implementation complete!

🔗 Next steps:
   1. Quality validation will run automatically
   2. Test functionality manually
   3. Commit: /ctxk:impl:commit-changes
   4. Release: /ctxk:impl:release-app [version]
```

════════════════════════════════════════════════════════════════════════════════
👩‍💻 DEVELOPER CUSTOMIZATIONS - EDITABLE SECTION
════════════════════════════════════════════════════════════════════════════════

This section is preserved during ContextKit migrations and updates.
Add project-specific instructions, examples, and overrides below.

## Custom Task Selection Logic
<!-- Override automatic task selection with project-specific priority rules -->

## Additional Environment Checks
<!-- Add project-specific dependency or tool verification steps -->

## Custom Constitutional Reminders
<!-- Add project-specific architectural principles or coding standards -->