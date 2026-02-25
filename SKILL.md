---
name: project-guardian
description: Intelligent project knowledge management system with AUTO-DETECTION. Automatically initializes when user asks project-related questions in uninitialized codebases. Use when user asks about project architecture/structure, conventions, wants to track bugs/requirements, or asks about similar issues. ALWAYS check for .project-ai/ directory first - if missing and user asks project questions, proactively offer to initialize. Supports English and Chinese.
icon: 🛡️
version: 1.0.0
author: taokoplay
tags: [project-management, knowledge-base, bug-tracking, architecture, auto-detection]
---

# Project Guardian Skill

## Overview

Project Guardian Skill maintains a lightweight, token-efficient knowledge base about your codebase. It automatically learns your project's architecture, conventions, and history to provide context-aware assistance and prevent recurring issues.

**Key Features:**
- Zero-configuration project scanning
- Automatic tech stack and tool detection
- Progressive context loading (<2k tokens core)
- Bug/requirement tracking with similarity search
- Architecture decision records (ADR)
- Prevention of recurring issues

## 📋 Response Format

**IMPORTANT**: When this skill is invoked, ALWAYS include a brief status indicator at the start or end of your response:

### Format Examples

**When checking initialization:**
```
🔍 [Project Guardian] Checking project initialization status...
```

**When scanning project:**
```
✓ [Project Guardian] Scanned project and created knowledge base
```

**When recording bug:**
```
✓ [Project Guardian] Recorded bug #BUG-20260225-001
```

**When searching similar issues:**
```
🔎 [Project Guardian] Found 3 similar issues in history
```

**When loading project context:**
```
📚 [Project Guardian] Loaded project context from .project-ai/
```

### Response Template

```
[Brief status indicator with skill name]

[Main response content]

[Optional: What was accomplished]
```

**Example:**
```
✓ [Project Guardian] Scanned project and initialized knowledge base

Detected:
- Project Type: full-stack
- Tech Stack: React 18.2.0, Express 4.18.2
- Tools: pnpm, Vite, ESLint, Prettier

Knowledge base created at .project-ai/
```

## 🤖 Intelligent Auto-Detection

**IMPORTANT**: Before following any workflow, ALWAYS check if the project has been initialized:

### Auto-Detection Logic

1. **Check for knowledge base**:
   ```bash
   # Quick check using helper script
   python scripts/check_initialized.py

   # Or manual check
   ls -la .project-ai/ 2>/dev/null || ls -la ../.project-ai/ 2>/dev/null
   ```

   The helper script returns:
   - Exit code 0: Project is initialized
   - Exit code 1: Not initialized
   - JSON output with detailed status

2. **If NOT found AND user is asking project-related questions**:
   - Questions about architecture: "how does X work", "where is Y", "explain Z"
   - Questions about conventions: "what's the naming convention", "how should I structure"
   - Questions about bugs/issues: "have we seen this", "similar issues"
   - Questions about tech stack: "what framework", "what version"
   - Code modification requests in a project context

   **→ Proactively suggest initialization**:
   ```
   🔍 [Project Guardian] This project doesn't have a knowledge base yet.

   Would you like me to scan and initialize? This will:
   - Automatically detect your tech stack and tools
   - Learn your code conventions and architecture
   - Enable smart bug tracking and prevention
   - Take ~10 seconds for most projects

   Should I proceed with the scan? (yes/no)
   ```

3. **If found**:
   - Load core context from `.project-ai/core/`
   - Proceed with user's request using project knowledge

### Smart Initialization Triggers

**Auto-initialize when**:
- User explicitly requests: "scan project", "initialize", "setup guardian"
- User asks architecture questions in uninitialized project
- User tries to record bugs/requirements without knowledge base
- User asks "what's in this project" or similar exploratory questions

**Don't auto-initialize when**:
- User is just asking general coding questions
- Working directory is not a code project (no package.json, go.mod, etc.)
- User is in a temporary/test directory
- User explicitly says "no" to initialization

## Workflow Decision Tree

### First Time Setup
**Trigger**: "setup project guardian", "scan this project", "initialize knowledge base"
→ Use **Initial Project Scan** workflow

### Recording Information
- **Bug encountered** → Use **Record Bug** workflow
- **New requirement** → Use **Record Requirement** workflow
- **Architecture decision** → Use **Record Decision** workflow

### Querying Information
- **"How does X work?"** → Use **Query Architecture** workflow
- **"Have we seen this before?"** → Use **Search Similar Issues** workflow
- **"What's our convention for Y?"** → Use **Query Conventions** workflow

### Maintenance
- **After significant changes** → Use **Incremental Update** workflow
- **Knowledge base too large** → Run compression (manual)

## Initial Project Scan

**When to use**: First time setting up Project Guardian for a codebase.

### Workflow

1. **Run scanner**:
   ```bash
   python scripts/scan_project.py /path/to/project
   ```

2. **Scanner automatically detects**:
   - **Project type**: web-frontend, web-backend, full-stack, mobile-ios, mobile-android, library, cli-tool
   - **Tech stack**: Languages (TypeScript, Python, Go, Rust, Java), frameworks (React, Vue, Express, Django, etc.)
   - **Tools**: Package managers (npm, pnpm, yarn, poetry), build tools (Vite, Webpack), linters (ESLint, Pylint), formatters (Prettier), testing frameworks (Vitest, Jest, Playwright)
   - **Conventions**: Naming patterns, import styles, formatting rules from config files
   - **Structure**: Directory layout, entry points, key files

3. **Creates knowledge base** at `<project-root>/.project-ai/`:
   ```
   .project-ai/
   ├── core/                    # Always loaded (<2k tokens)
   │   ├── profile.json        # Project metadata
   │   ├── tech-stack.json     # Technologies used
   │   └── conventions.json    # Code standards
   ├── indexed/                 # Loaded on demand
   │   ├── architecture.json   # System architecture
   │   ├── modules.json        # Module descriptions
   │   ├── tools.json          # Development tools
   │   └── structure.json      # Directory structure
   └── history/                 # Searchable records
       ├── bugs/               # Bug records by date
       ├── requirements/       # Requirement records
       └── decisions/          # Architecture decisions
   ```

4. **Review and confirm**: Scanner presents findings for user confirmation before creating files.

### Example Output

```
✓ [Project Guardian] Scanning project...

🔍 Scanning project: /Users/dev/my-app

📊 SCAN RESULTS
============================================================

🏷️  Project Type: full-stack

💻 Tech Stack:
  languages: TypeScript, JavaScript
  frameworks: React 18.2.0, Express 4.18.2
  libraries: Tailwind CSS, Axios
  runtime: Node.js

🛠️  Tools:
  version_control: Git
  package_manager: pnpm
  build_tool: Vite
  linter: ESLint
  formatter: Prettier
  testing: Vitest, Playwright
  ci_cd: GitHub Actions

📐 Conventions:
  naming: ['camelCase for variables', 'PascalCase for components']
  imports: ['Use @ alias for absolute imports']
  formatting: {'semi': True, 'singleQuote': True, 'tabWidth': 2}

📂 Structure:
  Root dirs: src, public, server, tests, docs
  Entry points: src/main.tsx, server/index.ts

✅ Create knowledge base with these settings? (y/n):
```

## Progressive Loading Strategy

**Core principle**: Only load what's needed for the current task to minimize token usage.

### Level 1: Always Loaded (~1.5k tokens)
From `.project-ai/core/`:
- Project type and tech stack
- Key conventions
- Basic project metadata

### Level 2: Conditional Loading
Triggered by keywords or context:
- User mentions "auth" or "authentication" → Load `indexed/modules.json` auth section
- Discussing "architecture" or "design" → Load `indexed/architecture.json`
- Bug report → Search `history/bugs/` for similar issues
- Mentions specific tool → Load `indexed/tools.json`

### Level 3: Search-Based Loading
For specific queries:
- "How did we handle X before?" → Full-text search in history
- "Similar to bug #123" → Semantic similarity search
- Tag-based search → Use bug index for fast lookup

**Implementation details**: See [references/knowledge-schema.md](references/knowledge-schema.md) for complete schema and token budgets.

## Recording Bugs

**When to use**: After fixing a bug to prevent recurrence.

### Workflow

1. **Extract bug information from conversation**:
   - Title: Brief description
   - Description: What went wrong and how to reproduce
   - Root cause: Why it happened
   - Solution: How it was fixed
   - Files changed: List of modified files
   - Tags: Categorization (api, timeout, auth, etc.)
   - Severity: low, medium, high, critical

2. **Create bug record file**:
   ```bash
   # Use template from assets/bug-template.json
   cat > /tmp/bug.json << EOF
   {
     "title": "Payment API timeout",
     "description": "Stripe API calls timing out after 5 seconds",
     "root_cause": "Missing timeout configuration in axios",
     "solution": "Added 30s timeout to axios config",
     "files_changed": ["src/api/payment.ts"],
     "tags": ["api", "timeout", "payment"],
     "severity": "high"
   }
   EOF
   ```

3. **Check for similar issues**:
   ```bash
   python scripts/search_similar.py /path/to/project "payment timeout"
   ```

4. **Record to knowledge base**:
   ```bash
   python scripts/update_knowledge.py /path/to/project --type bug --data /tmp/bug.json
   ```

5. **Respond to user**:
   ```
   ✓ [Project Guardian] Recorded bug #BUG-20260225-001

   Title: Payment API timeout
   Severity: high
   Tags: api, timeout, payment

   This bug has been saved to the knowledge base and will help prevent similar issues.
   ```

6. **Auto-prevention**: Next time similar code is written, search for related bugs and warn the user.

### Example Prevention

```
⚠️ [Project Guardian] Similar issue found in knowledge base:

Bug: Payment API timeout (2024-02-15)
Root Cause: Missing timeout configuration
Solution: Added 30s timeout to axios config

Consider applying the same fix to avoid this issue.
```

## Recording Requirements

**When to use**: Capturing new features or changes to implement.

### Workflow

1. **Extract requirement information**:
   - Title: Brief description
   - Description: Detailed explanation
   - Status: planned, in-progress, completed, cancelled
   - Priority: low, medium, high, critical
   - Related modules: Which parts of codebase are affected
   - Acceptance criteria: List of conditions for completion
   - Tags: Categorization

2. **Create requirement file** using `assets/requirement-template.json`:
   ```json
   {
     "title": "WeChat login support",
     "description": "Users should be able to login with WeChat OAuth",
     "status": "planned",
     "priority": "high",
     "related_modules": ["auth", "user"],
     "acceptance_criteria": [
       "WeChat OAuth integration",
       "User profile sync from WeChat",
       "Existing account linking"
     ],
     "tags": ["authentication", "oauth", "wechat"]
   }
   ```

3. **Record requirement**:
   ```bash
   python scripts/update_knowledge.py /path/to/project --type requirement --data req.json
   ```

4. **Respond to user**:
   ```
   ✓ [Project Guardian] Recorded requirement #REQ-20260225-001

   Title: WeChat login support
   Priority: high
   Status: planned
   Related modules: auth, user

   Requirement saved to knowledge base.
   ```

5. **Track implementation**: Update status as work progresses.

## Recording Architecture Decisions

**When to use**: Documenting important technical decisions for future reference.

### Workflow

Use the Architecture Decision Record (ADR) format from `assets/decision-template.json`:

```json
{
  "title": "Use PostgreSQL for primary database",
  "context": "Need to choose database for user data and transactions",
  "decision": "Use PostgreSQL as primary database",
  "rationale": "ACID compliance, JSON support, mature ecosystem",
  "consequences": [
    "Positive: Strong consistency guarantees",
    "Positive: Rich query capabilities",
    "Negative: More complex setup than SQLite",
    "Trade-off: Vertical scaling limits"
  ],
  "alternatives": [
    "MongoDB: Rejected due to lack of transactions",
    "MySQL: Rejected due to weaker JSON support"
  ],
  "tags": ["database", "architecture", "postgresql"]
}
```

Record with:
```bash
python scripts/update_knowledge.py /path/to/project --type decision --data decision.json
```

## Querying Project Knowledge

### Query Architecture

**Example queries**:
- "What's our authentication flow?"
- "How does the payment system work?"
- "What's the data model for users?"

**Workflow**:
1. Load `core/profile.json` and `core/tech-stack.json` (always loaded)
2. If architecture info exists, load `indexed/architecture.json`
3. If specific module mentioned, load that section from `indexed/modules.json`
4. Provide answer based on loaded context

### Query Conventions

**Example queries**:
- "What's the naming convention for API routes?"
- "How should I format imports?"
- "What's our testing approach?"

**Workflow**:
1. Load `core/conventions.json` (always loaded)
2. Extract relevant convention
3. Provide answer with examples

### Search Similar Issues

**Example queries**:
- "Have we had database connection issues before?"
- "Similar bugs to this timeout problem?"
- "What bugs are tagged with 'authentication'?"

**Workflow**:
1. Run similarity search:
   ```bash
   python scripts/search_similar.py /path/to/project "database connection"
   ```

2. Or search by tags:
   ```bash
   python scripts/search_similar.py /path/to/project --tags authentication,oauth
   ```

3. Display top 3 most similar issues with:
   - Title and ID
   - Date recorded
   - Root cause
   - Solution
   - Tags

## Incremental Updates

**When to use**: After implementing features, fixing bugs, or making architectural changes.

### Automatic Update Triggers

Project Guardian should automatically update knowledge base when:
- Bug is fixed → Record bug and solution
- Feature is implemented → Update module descriptions
- Architecture changes → Update architecture.json
- New conventions adopted → Update conventions.json

### Manual Update

For module information:
```bash
# Create module info file
cat > /tmp/module.json << EOF
{
  "description": "Handles user authentication and authorization",
  "responsibilities": [
    "OAuth integration",
    "Session management",
    "Permission checks"
  ],
  "dependencies": ["user", "database"],
  "key_files": ["src/auth/oauth.ts", "src/auth/session.ts"]
}
EOF

# Update knowledge base
python scripts/update_knowledge.py /path/to/project --module auth --info /tmp/module.json
```

## Multi-Project Usage

**Data Isolation Guarantee**: Each project's knowledge base is completely isolated. Multiple projects will never interfere with each other.

### How Isolation Works

Each project stores its knowledge base in its own root directory:
```
/Users/you/projects/
├── project-a/.project-ai/    # project-a's knowledge base
├── project-b/.project-ai/    # project-b's knowledge base
└── project-c/.project-ai/    # project-c's knowledge base
```

The scanner uses absolute paths (`Path.resolve()`) to ensure each project's data stays separate.

### Working with Multiple Projects

```bash
# Initialize project A
cd ~/projects/ecommerce-frontend
python scripts/scan_project.py .

# Initialize project B
cd ~/projects/blog-backend
python scripts/scan_project.py .

# Work in project A
cd ~/projects/ecommerce-frontend
python scripts/search_similar.py . "timeout"
# Only searches ecommerce-frontend/.project-ai/

# Work in project B
cd ~/projects/blog-backend
python scripts/search_similar.py . "timeout"
# Only searches blog-backend/.project-ai/
```

### Team Collaboration

**Option 1: Share via Git** (recommended for core knowledge)
```bash
git add .project-ai/core/ .project-ai/indexed/
git commit -m "Add project knowledge base"
```

**Option 2: Individual knowledge bases** (for personal bug tracking)
```bash
echo ".project-ai/" >> .gitignore
# Each team member maintains their own
```

## Best Practices

1. **Review scanner output**: Always confirm auto-detected information before creating knowledge base
2. **Tag consistently**: Use consistent tags for better search (e.g., always use "auth" not "authentication" sometimes)
3. **Update regularly**: Record bugs and requirements as they happen, not in batches
4. **Be specific**: Include root causes and solutions, not just symptoms
5. **Link related items**: Reference related bugs in requirements, requirements in decisions
6. **Keep it lean**: Knowledge base should stay under 50k tokens total
7. **One knowledge base per project**: Don't create multiple `.project-ai/` directories in the same project

## Integration with Development Workflow

### Git Hooks (Optional)

Add to `.git/hooks/post-commit`:
```bash
#!/bin/bash
# Auto-update knowledge base after commits
python .project-ai/scripts/update_knowledge.py . --auto
```

### CI/CD Integration (Optional)

Add to GitHub Actions workflow:
```yaml
- name: Validate Architecture
  run: |
    python .project-ai/scripts/validate_architecture.py
```

## Troubleshooting

**Scanner fails to detect project type**:
- Manually edit `.project-ai/core/profile.json` and set `project_type`

**Knowledge base too large (>50k tokens)**:
- Run compression (future feature)
- Archive old bugs (>6 months)
- Summarize completed requirements

**Search returns irrelevant results**:
- Improve tagging consistency
- Use more specific keywords
- Try tag-based search instead

**Missing conventions**:
- Manually add to `.project-ai/core/conventions.json`
- Scanner only detects conventions from config files

## Advanced Configuration

For detailed schema documentation and token optimization strategies, see:
- [references/knowledge-schema.md](references/knowledge-schema.md) - Complete schema definitions and token budgets

## Templates

Use these templates for creating records:
- `assets/bug-template.json` - Bug record template
- `assets/requirement-template.json` - Requirement template
- `assets/decision-template.json` - Architecture decision template
