# Research and Design Architecture
<!-- Template Version: 6 | ContextKit: 0.0.0 | Updated: 2025-09-19 -->

> [!WARNING]
> **👩‍💻 FOR DEVELOPERS**: Do not edit the content above the developer customization section - changes will be overwritten during ContextKit updates.
>
> For project-specific customizations, use the designated section at the bottom of this file.
>
> Found a bug or improvement for everyone? Please report it: https://github.com/FlineDev/ContextKit/issues

## Description
Generate technical research and architecture plan by detecting current feature, validating prerequisites, executing integrated research phase, and creating comprehensive research and architectural documentation.

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

### Phase 1: Setup Validation & Prerequisites

1. **Check Project Setup**
   - Use `Glob` tool to verify Context.md exists: `Glob . Context.md`
   - If Context.md missing:
     ```
     ❌ ContextKit not initialized in this project!

     Run /ctxk:proj:init first to setup ContextKit in this project.
     This command requires project context to detect tech stack and apply
     appropriate development guidelines.
     ```
     → END (exit with error)

2. **Verify ContextKit Global Installation**
   ```bash
   ls -la ~/.ContextKit/Templates/Features/Tech.md || echo "❌ ContextKit not installed globally. Run: curl -fsSL https://raw.githubusercontent.com/FlineDev/ContextKit/main/install.sh | sh"
   ```

### Phase 2: Feature Detection & Validation

3. **Detect Current Feature**
   - Use `Bash` tool to check current git branch: `git branch --show-current`
   - If on feature/[prefix]-[name] branch: Extract feature name from branch
   - If not on feature branch: Ask user which feature to work on using consistent format
   - Use `Glob` tool to find numbered feature directory: `Glob Context/Features/???-[FeatureName]`
   - Store the found directory path for use in subsequent steps

4. **Validate Prerequisites**
   - Use `Read` tool to check Spec.md exists in the found numbered directory: `Read [numbered-feature-directory]/Spec.md`
   - If Spec.md missing:
     ```
     ❌ Feature specification not found!

     Run /ctxk:plan:1-spec first to create the business requirements.
     Technical planning requires completed specification as input.
     ```
     → END (exit with error)
   - Check for 🚨 [NEEDS CLARIFICATION] markers in specification
   - If clarifications exist: WARN user to resolve them first

### Phase 3: Research Phase Execution

5. **Copy Research Template**
   ```bash
   cp ~/.ContextKit/Templates/Features/Research.md [numbered-feature-directory]/Research.md
   echo "✅ Copied technical research template"
   ```

6. **Execute Research Template System Instructions**
   - Use `Read` tool to read the **ENTIRE** copied Research.md template: `Read [numbered-feature-directory]/Research.md`
   - **CRITICAL**: The template contains 300+ lines with detailed system instructions - read it completely to understand all phases
   - **CRITICAL**: Follow the Research.md template's **🤖 EXECUTION FLOW** instructions step by step:

   **Phase 1: Knowledge Gap Identification** (Steps 1-4 in Research.md)
   - Load feature specification and project context
   - Identify all research targets from specification
   - Launch comprehensive codebase integration agent if needed

   **Phase 2: Active Knowledge Acquisition** (Steps 5-7 in Research.md)
   - Launch technology research agents using `Task` tool for each mentioned technology
   - Launch API research agents for external services using `Task` tool
   - Launch architecture pattern research agents using `Task` tool
   - **CRITICAL**: Instruct ALL agents to RETURN findings as text responses, NOT create markdown files
   - **Wait for ALL agents to complete** before proceeding

   **Phase 3: Research Consolidation** (Steps 8-12 in Research.md)
   - Use `Edit` tool to replace template header with specific feature information
   - Use `Edit` tool to document ALL technology research results from completed agents
   - Use `Edit` tool to document ALL API & service research results from completed agents
   - Use `Edit` tool to document codebase integration analysis from completed agents
   - Use `Edit` tool to document ALL architectural pattern research from completed agents

   **Phase 4: Completion** (Steps 13-15 in Research.md)
   - Validate research completeness against specification
   - Generate research summary with key decisions
   - Use `Edit` tool to **remove the entire boxed system instructions section** from Research.md

   **Research execution**: You must populate the Research.md file with actual findings, not leave it as a template

7. **Validate Research Completion**
   - Use `Read` tool to verify research completion: `Read [numbered-feature-directory]/Research.md`
   - Ensure all technologies mentioned in specification have been researched
   - Verify research findings are documented with decisions and rationale
   - If research incomplete: WARN user to complete research before proceeding

### Phase 4: Technical Architecture Planning

8. **Copy Technical Architecture Template**
   ```bash
   cp ~/.ContextKit/Templates/Features/Tech.md [numbered-feature-directory]/Tech.md
   echo "✅ Copied technical architecture template"
   ```

9. **Execute Technical Architecture Template**
   - Use `Read` tool to read the copied Tech.md: `Read [numbered-feature-directory]/Tech.md`
   - Follow the **system instructions** section (boxed area) step by step
   - The template contains technical architecture generation logic informed by research results
   - Use tools (`Read`, `Edit`) as directed by the template instructions
   - **Template execution**: The copied Tech.md handles architecture decisions, Context/Guidelines compliance, and complexity assessment
   - **Progress tracking**: User can see architectural planning checkboxes being completed in the copied file

10. **Validate Research Cleanup**
    - Use `Read` tool to check if Research.md still contains system instructions: `Read [numbered-feature-directory]/Research.md`
    - Search for "🤖 EXECUTION FLOW" or "VALIDATION & EXECUTION STATUS" sections
    - If system instructions remain: Use `Edit` tool to remove all boxed instruction sections
    - Ensure final Research.md contains only clean research results

11. **Validate Technical Architecture Cleanup**
    - Use `Read` tool to check if Tech.md still contains system instructions: `Read [numbered-feature-directory]/Tech.md`
    - Search for "🤖 EXECUTION FLOW" or "VALIDATION & EXECUTION STATUS" sections
    - If system instructions remain: Use `Edit` tool to remove all boxed instruction sections
    - Ensure final Tech.md contains only clean technical architecture content

12. **Display Success Message** (see Success Messages section)

## Error Conditions

- **"Context.md not found"** → User must run `/ctxk:proj:init` to initialize ContextKit
- **"ContextKit not installed globally"** → Run installation: `curl -fsSL https://raw.githubusercontent.com/FlineDev/ContextKit/main/install.sh | sh`
- **"Feature specification not found"** → Must run `/ctxk:plan:1-spec` first
- **"Technical template not found"** → Check global ContextKit installation integrity
- **"Specification has unresolved clarifications"** → Resolve [NEEDS CLARIFICATION] markers in Spec.md first
- **"Template execution failed"** → Verify Research.md and Tech.md templates contain system instructions sections
- **"Research.md not populated"** → Research agents completed but findings not documented in Research.md - must execute template's Phase 3 consolidation steps
- **"Cleanup validation failed"** → System instruction sections remain after template execution - manual cleanup required

## Validation Gates

- ContextKit globally installed and accessible?
- Project Context.md exists (ContextKit project setup complete)?
- Feature specification exists and is complete?
- No unresolved [NEEDS CLARIFICATION] markers in specification?
- Technical template copied to feature directory successfully?
- Template system instructions executed successfully?
- System instructions sections removed from both Research.md and Tech.md?
- User informed to review and commit technical plan before proceeding?

## Integration Points

- **Global ContextKit**: Uses Templates/Features/Tech.md template for technical architecture generation
- **Project Setup**: Requires Context.md created by /ctxk:proj:init for project detection and context
- **Template Execution**: Delegates all technical logic to copied Tech.md template (follows init-workspace pattern)
- **Development Workflow**: Creates foundation for /ctxk:plan:3-steps implementation planning phase
- **Team Collaboration**: Creates committed technical plan for team review and development guidance
- **Git Integration**: Works within existing feature branch for systematic development workflow
- **Workspace Integration**: Template inherits coding standards and constitutional overrides from workspace Context.md

## Success Messages

### Research & Technical Plan Created Successfully
```
🎉 Technical research and architecture planning completed successfully!

✅ Created: Context/Features/[Name]/Research.md
✅ Created: Context/Features/[Name]/Tech.md
✅ Researched all technologies mentioned in specification
✅ Applied Context/Guidelines/Swift.md and SwiftUI.md standards
✅ All mandatory sections completed with research-informed decisions
✅ System instruction sections cleaned up from both files

[If 🚨 [NEEDS CLARIFICATION] items exist in plans:]
⚠️  Technical clarifications needed for:
• [Templates will list specific questions that need answers]

🔗 Next Steps:
1. Review Context/Features/[Name]/Research.md to verify research findings
2. Review Context/Features/[Name]/Tech.md to ensure technical decisions are sound
3. [If clarifications needed:] Edit the files to resolve marked questions
4. When satisfied with both research and technical plan: commit your changes with git
5. Run /ctxk:plan:3-steps to proceed with implementation task breakdown

💡 Research-informed technical architecture ready for your review and approval!
```

════════════════════════════════════════════════════════════════════════════════
👩‍💻 DEVELOPER CUSTOMIZATIONS - EDITABLE SECTION
════════════════════════════════════════════════════════════════════════════════

This section is preserved during ContextKit migrations and updates.
Add project-specific instructions, examples, and overrides below.

## Project-Specific Instructions

<!-- Add any project-specific guidance for technical architecture planning here -->

## Additional Examples

<!-- Add examples of architectural patterns that work well with your project -->

## Override Behaviors

<!-- Document any project-specific architectural requirement overrides here -->