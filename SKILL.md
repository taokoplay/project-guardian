---
name: project-guardian
description: Intelligent project knowledge management system with AUTO-DETECTION and SMART CACHING. Automatically initializes when user asks project-related questions. Features intelligent trigger detection, 40% faster loading with adaptive caching, and Git hooks automation. Use when user asks about project architecture/structure, conventions, wants to track bugs/requirements, or asks about similar issues. ALWAYS check for .project-ai/ directory first. Supports English and Chinese.
icon: 🛡️
version: 1.4.0
author: taokoplay
tags: [project-management, knowledge-base, bug-tracking, architecture, auto-detection, caching, automation]
---

# Project Guardian Skill

**Version:** 1.4.0 | **Author:** taokoplay | **License:** MIT

## Overview

Project Guardian Skill maintains a lightweight, token-efficient knowledge base about your codebase. It automatically learns your project's architecture, conventions, and history to provide context-aware assistance and prevent recurring issues.

**Key Features:**
- 🚀 Zero-configuration project scanning
- 🔍 Automatic tech stack and tool detection
- 📚 Progressive context loading (<2k tokens core)
- 🐛 Bug/requirement tracking with similarity search
- 🏛️ Architecture decision records (ADR)
- 🛡️ Prevention of recurring issues
- **NEW v1.4.0:**
  - 🧠 Intelligent trigger detection (multi-language)
  - ⚡ Smart caching (40% faster, adaptive TTL)
  - 🔗 Git hooks automation (auto-update on commit/merge)
  - 📊 Cache statistics and monitoring

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
- **Check health** → Use **Health Check** workflow
- **Analyze usage patterns** → Use **Pattern Analysis** workflow

## 🚀 New Features in v1.3.0

### 1. Query Pattern Learning 🧠

**Problem**: Don't know what users are asking about or where knowledge gaps exist.

**Solution**: Automatic query logging and pattern analysis to optimize knowledge base.

```bash
# Log a query (automatic in workflows)
python scripts/query_logger.py . --log "How does authentication work?"

# View recent queries
python scripts/query_logger.py . --recent 20

# Search queries by keyword
python scripts/query_logger.py . --search "auth"

# Get query statistics
python scripts/query_logger.py . --stats
```

**Pattern Analysis**:
```bash
# Full analysis report
python scripts/pattern_analyzer.py .

# Frequent questions
python scripts/pattern_analyzer.py . --frequent 10

# Knowledge gaps (queries without results)
python scripts/pattern_analyzer.py . --gaps

# Popular modules
python scripts/pattern_analyzer.py . --modules

# Time patterns
python scripts/pattern_analyzer.py . --time

# Get recommendations
python scripts/pattern_analyzer.py . --recommend
```

**Example Report**:
```
📊 QUERY PATTERN ANALYSIS REPORT
============================================================

🔥 Top 5 Frequent Question Patterns:
  1. auth + login + work (12 times)
  2. payment + stripe + timeout (8 times)
  3. database + query + slow (6 times)

📝 Knowledge Gaps: 15 queries without results
  Recent examples:
    - How to implement rate limiting?
    - What's our caching strategy?

📦 Top 5 Popular Modules:
  1. auth: 25 queries
  2. api: 18 queries
  3. database: 12 queries

💡 Recommendations:
  📝 Found 15 queries without results. Consider documenting:
     - rate (5 queries)
     - cache (4 queries)
     - performance (3 queries)
  🔥 Most queried module: auth (25 queries). Consider adding more documentation.
```

**Benefits**:
- Identify frequently asked questions
- Discover knowledge gaps
- Understand which modules need more documentation
- Track usage patterns over time
- Get actionable recommendations

### 2. Semantic Search (Optional) 🎯

**Problem**: Keyword-based search misses semantically similar content.

**Solution**: Optional semantic search using AI embeddings for better results.

**Installation** (optional):
```bash
pip install sentence-transformers
```

**Build embeddings**:
```bash
python scripts/semantic_search.py . --build
```

**Search with semantic understanding**:
```bash
# Semantic search (understands meaning)
python scripts/semantic_search.py . --search "login not working" --top 5

# Search specific type
python scripts/semantic_search.py . --search "payment fails" --type bug

# Check status
python scripts/semantic_search.py . --status
```

**Comparison**:

| Feature | TF-IDF (Default) | Semantic Search (Optional) |
|---------|------------------|----------------------------|
| Installation | ✅ Built-in | ⚙️ Requires sentence-transformers |
| Speed | ⚡ Fast | 🐢 Slower (first time) |
| Accuracy | 📊 Good | 🎯 Excellent |
| Understanding | 🔤 Keywords only | 🧠 Semantic meaning |
| Example | "auth bug" ≠ "login issue" | "auth bug" ≈ "login issue" |

**Automatic fallback**: If semantic search is not installed, the system automatically falls back to TF-IDF search.

**Integration**: `search_similar.py` now supports `--semantic` flag:
```bash
# Use semantic search if available
python scripts/search_similar.py . --query "payment timeout" --semantic
```

## 🚀 New Features in v1.2.0

### 1. Version Tracking & Git Integration 📌

**Problem**: Can't trace when knowledge base was updated or which code version it corresponds to.

**Solution**: Automatic Git commit tracking with every knowledge base update.

```bash
# View current Git commit
python scripts/version_tracker.py . --current

# View recent versions
python scripts/version_tracker.py . --recent 10

# Associate bug with commit
python scripts/version_tracker.py . --bug BUG-20260225-001 \
  --fixed abc1234 \
  --introduced def5678

# Generate knowledge base changelog
python scripts/version_tracker.py . --changelog

# Find bugs fixed in commit range
python scripts/version_tracker.py . --bugs-in-range v1.0.0 HEAD
```

**Features**:
- Automatically records Git commit hash with each update
- Tracks commit message, author, date, and branch
- Associates bugs with the commits that fixed/introduced them
- Generates knowledge base changelog from version history
- Enables historical analysis and code evolution tracking

**Auto-integration**:
- `scan_project.py` automatically records initial version
- `incremental_update.py` automatically records update version
- No manual intervention needed!

### 2. Health Monitoring 🏥

**Problem**: Don't know if knowledge base is up-to-date, complete, or being used effectively.

**Solution**: Comprehensive health checker with actionable recommendations.

```bash
# Run health check
python scripts/health_checker.py .

# Output as JSON
python scripts/health_checker.py . --json
```

**Health Check Report**:
```
🏥 Running knowledge base health check...

Checking Freshness...
  ✅ Knowledge base is 2 days old (fresh)

Checking Completeness...
  ✅ All required files and directories exist

Checking Bug Quality...
  🟡 3/10 bugs missing solution
  ℹ️  2/10 bugs missing tags

Checking Size...
  📊 Total records: 25 (10 bugs, 8 requirements, 7 decisions)

Checking Usage...
  ✅ 5 bugs recorded in the last 30 days (active)

============================================================
📊 HEALTH CHECK RESULTS
============================================================

🎯 Overall Score: 82/100
📈 Status: 🟡 Good

📋 Detailed Scores:
  Freshness: 100/100
  Completeness: 100/100
  Bug Quality: 70/100
  Size: 100/100
  Usage: 100/100

💡 Recommendations:
  1. 📝 Review and update bug records with solutions
  2. 🔎 Analyze bugs and document root causes

⏰ Checked at: 2026-02-25T22:30:00
============================================================
```

**What it checks**:
- **Freshness**: How recently was the knowledge base updated?
- **Completeness**: Are all required files present?
- **Bug Quality**: Do bugs have solutions and root causes?
- **Size**: Is the knowledge base too large or too small?
- **Usage**: Is it being actively used?

**Scoring**:
- 🟢 90-100: Excellent
- 🟡 75-89: Good
- 🟠 60-74: Fair
- 🔴 <60: Needs Attention

## 🚀 New Features in v1.1.0

### 1. Quick Recording (No JSON Files Needed!)

**Before (v1.0.x)**: Had to create JSON files manually
```bash
# Old way - tedious
echo '{"title":"Bug","description":"..."}' > bug.json
python update_knowledge.py . --bug bug.json
```

**Now (v1.1.0)**: Direct command-line recording
```bash
# Quick bug recording
python scripts/update_knowledge.py . --quick-bug \
  --title "Payment API timeout" \
  --desc "Stripe API times out after 5 seconds" \
  --cause "No retry logic implemented" \
  --solution "Added exponential backoff retry" \
  --tags "api,payment,stripe" \
  --severity high

# Quick requirement recording
python scripts/update_knowledge.py . --quick-req \
  --title "Dark mode support" \
  --desc "Users want dark mode for better UX" \
  --rationale "Reduce eye strain for night users" \
  --priority high \
  --status approved

# Quick decision recording
python scripts/update_knowledge.py . --quick-decision \
  --title "Use PostgreSQL over MongoDB" \
  --context "Need ACID transactions for payments" \
  --decision "Chose PostgreSQL for reliability" \
  --consequences "More complex schema migrations"
```

### 2. Incremental Updates (Keep Knowledge Base Fresh!)

**Problem**: Knowledge base becomes outdated as code changes.

**Solution**: Incremental update script that only scans changed files.

```bash
# Run after making code changes
python scripts/incremental_update.py .

# Output:
# 🔄 Running incremental update...
# 📊 Detected changes:
#   + Added: 3 files
#   ~ Modified: 5 files
#   - Deleted: 1 file
# 📦 Updating tech stack...
# 📂 Updating project structure...
# ✅ Incremental update completed
```

**Features**:
- Tracks file checksums to detect changes
- Only updates affected parts of knowledge base
- Much faster than full rescan (seconds vs minutes)
- Preserves manually edited knowledge

**When to use**:
- After adding new dependencies (package.json changed)
- After restructuring directories
- After adding/removing major files
- Periodically (weekly/monthly)

### 3. Context-Aware Loading (Smarter Knowledge Retrieval!)

**Problem**: Loading entire knowledge base wastes tokens.

**Solution**: Intelligently load only relevant knowledge based on context.

**Load for specific file**:
```bash
python scripts/context_loader.py . --file src/auth/login.ts

# Automatically loads:
# - Auth module information
# - Related bugs in auth system
# - Relevant conventions
```

**Load for user query**:
```bash
python scripts/context_loader.py . --query "How does authentication work?" \
  --current-file src/pages/Login.tsx

# Intelligently loads:
# - Auth-related modules
# - Authentication bugs
# - Login requirements
# - Security decisions
```

**Load minimal (for general questions)**:
```bash
python scripts/context_loader.py . --minimal

# Only loads core context:
# - Project profile
# - Tech stack
# - Basic conventions
```

**Benefits**:
- Reduces token usage by 50-70%
- Faster responses
- More relevant context
- Automatic module detection

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

### 🔗 Git Hooks Automation (v1.4.0)

**NEW**: Automatic knowledge base updates with Git hooks!

#### Quick Installation

```bash
# Interactive installation
cd /path/to/your/project
/path/to/project-guardian/scripts/install_hooks.sh

# Or direct installation
python /path/to/project-guardian/scripts/auto_hooks.py . --install
```

#### Available Hooks

1. **post-commit**: Automatically records Git commit in version history
   ```bash
   python auto_hooks.py . --install-post-commit
   ```

2. **pre-push**: Validates knowledge base health before push
   ```bash
   python auto_hooks.py . --install-pre-push
   ```

3. **post-merge**: Runs incremental update after merge
   ```bash
   python auto_hooks.py . --install-post-merge
   ```

4. **commit-msg**: Extracts bug fixes from commit messages (e.g., "fix #123")
   ```bash
   python auto_hooks.py . --install-commit-msg
   ```

#### Hook Management

```bash
# List installed hooks
python auto_hooks.py . --list

# Test hooks
python auto_hooks.py . --test

# Uninstall all hooks
python auto_hooks.py . --uninstall
```

### ⚡ Smart Caching (v1.4.0)

**NEW**: Intelligent caching system for 40% faster loading!

#### Features

- **Content-based invalidation**: MD5 hash validation
- **Adaptive TTL**: Adjusts based on file change frequency
  - Core files: 1 hour (rarely changes)
  - Indexed files: 30 minutes (occasionally changes)
  - History files: No cache (real-time data)
- **LRU eviction**: Automatic memory management
- **Cache warming**: Pre-loads frequently accessed files

#### Usage

```bash
# Cache is enabled by default in context_loader.py
python context_loader.py . --query "authentication bugs"

# View cache statistics
python context_loader.py . --cache-stats

# Clear cache
python context_loader.py . --clear-cache

# Disable cache for specific operation
python context_loader.py . --query "..." --no-cache
```

#### Cache Statistics

```bash
python cache_manager.py . --stats

# Output:
# 📊 Cache Statistics:
#   Size: 15/100
#   Hit Rate: 85.3%
#   Hits: 127
#   Misses: 22
#   Invalidations: 8
#   Evictions: 0
```

### 🧠 Intelligent Trigger Detection (v1.4.0)

**NEW**: Automatically detects when to activate Project Guardian!

#### Features

- **Multi-language support**: English and Chinese
- **Context awareness**: Considers current file and conversation history
- **Intent classification**: Query, record, update, analyze, initialize
- **Confidence scoring**: 0-1 confidence level
- **Smart suggestions**: Recommends appropriate actions

#### Usage

```bash
# Detect trigger from text
python trigger_detector.py "find similar bugs about authentication"

# Output:
# 🎯 Trigger Detection Result:
# {
#   "should_trigger": true,
#   "confidence": 0.85,
#   "intent": "query",
#   "matched_patterns": ["query:en:find.*bug"],
#   "suggestions": [
#     "Use search_similar.py to find related records"
#   ]
# }

# Check if auto-initialization should be suggested
python trigger_detector.py --check-init /path/to/project

# Get trigger statistics
python trigger_detector.py --stats /path/to/project
```

#### Trigger Patterns

**Query Intent**:
- English: "find bugs", "search issues", "show requirements"
- Chinese: "查找bug", "搜索问题", "显示需求"

**Record Intent**:
- English: "record bug", "add requirement", "create decision"
- Chinese: "记录bug", "添加需求", "创建决策"

**Update Intent**:
- English: "update bug", "mark resolved", "incremental update"
- Chinese: "更新bug", "标记已解决", "增量更新"

**Analyze Intent**:
- English: "analyze health", "show stats", "knowledge gaps"
- Chinese: "分析健康", "显示统计", "知识缺口"

### 🤖 Conversation Analysis & Auto-Recording (v1.4.0+)

**NEW**: Automatically detect and record important information from conversations!

#### Overview

Project Guardian can analyze conversations to identify:
- 🐛 Bug discoveries and solutions
- 🏛️ Architecture decisions and rationale
- 📋 Requirements and clarifications
- 📏 Code conventions and best practices
- ⚡ Performance insights and optimizations

#### Quick Start

```bash
# Analyze a conversation
python response_analyzer.py . \
  --user "I found a bug in authentication" \
  --assistant "The bug is caused by missing token validation..."

# With auto-recording
python conversation_hook.py . \
  --user "..." --assistant "..."
```

#### How It Works

1. **Pattern Detection**: Analyzes text for recordable patterns
2. **Confidence Scoring**: Calculates 0-1 confidence score
3. **Auto-Record** (≥0.8): Automatically creates knowledge base entry
4. **Suggest** (≥0.5): Notifies with recording suggestions
5. **Skip** (<0.5): No action taken

#### Configuration

```bash
# Copy configuration template
cp assets/conversation-hook-config.json .project-ai/config/

# Edit thresholds
{
  "auto_record_threshold": 0.8,
  "suggest_threshold": 0.5,
  "notification_style": "inline",
  "auto_record": {
    "bug": true,
    "decision": true,
    "requirement": false
  }
}
```

#### Detection Patterns

**Bug Detection**:
- Triggers: "bug found", "error encountered", "root cause", "solution"
- Chinese: "发现bug", "遇到错误", "解决方案"
- Auto-record: Yes (default)

**Decision Detection**:
- Triggers: "decided to", "architecture decision", "trade-off"
- Chinese: "决定", "架构决策", "权衡"
- Auto-record: Yes (default)

**Requirement Detection**:
- Triggers: "requirement", "feature", "user story", "must"
- Chinese: "需求", "功能", "用户故事"
- Auto-record: No (suggest only)

**Convention Detection**:
- Triggers: "convention", "best practice", "always use"
- Chinese: "约定", "最佳实践", "总是使用"
- Auto-record: No (suggest only)

**Performance Detection**:
- Triggers: "performance", "optimization", "bottleneck"
- Chinese: "性能", "优化", "瓶颈"
- Auto-record: No (suggest only)

#### Notification Styles

**Inline** (brief):
```
🤖 [Project Guardian] Auto-recorded bug (confidence: 0.85)
```

**Summary** (detailed):
```
💡 [Project Guardian] Recordable content detected:
   Type: bug
   Confidence: 0.85
   Suggestions:
     - Record bug with error: missing token validation
     - Use: python update_knowledge.py . --quick-bug
```

**Silent** (no output, check logs)

#### Statistics

```bash
python conversation_hook.py . --stats

# Output:
{
  "total_conversations": 150,
  "auto_recorded": 12,
  "suggested": 28,
  "by_type": {
    "bug": 8,
    "decision": 4,
    "requirement": 15
  }
}
```

#### Integration with Claude Code

After important conversations, the skill can:
1. Analyze conversation content
2. Detect recordable patterns
3. Auto-record or suggest recording
4. Update knowledge base automatically

For detailed documentation, see: [docs/conversation-analysis.md](docs/conversation-analysis.md)

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

## 🚀 What's New in v1.4.0

### Performance Improvements

- **40% faster loading**: Intelligent caching reduces file I/O
- **75% faster response**: Cache hit rate typically 80-90%
- **Adaptive TTL**: Automatically adjusts cache duration based on file change patterns
- **Zero overhead**: Cache warming happens in background

### Automation Features

- **Git hooks**: Automatic updates on commit, merge, push
- **Trigger detection**: Smart activation based on user intent
- **Auto-initialization**: Proactive suggestions for uninitialized projects
- **Health validation**: Pre-push checks ensure quality

### Intelligence Upgrades

- **Multi-language triggers**: English and Chinese support
- **Context awareness**: Considers current file and conversation
- **Intent classification**: Understands what you want to do
- **Confidence scoring**: Knows when to activate

### Upgrade from v1.3.0

If you're upgrading from v1.3.0, no migration needed! Just:

1. **Pull latest code**:
   ```bash
   cd /path/to/project-guardian-skill
   git pull origin main
   ```

2. **Optional: Install Git hooks**:
   ```bash
   cd /path/to/your/project
   /path/to/project-guardian-skill/scripts/install_hooks.sh
   ```

3. **Optional: Enable caching** (enabled by default):
   ```bash
   # Test cache
   python context_loader.py . --cache-stats
   ```

That's it! All new features work with existing knowledge bases.

## 📦 Version Information

### Check Installed Version

Use the version info tool to check your installed version and features:

```bash
# Display version information
python scripts/version_info.py

# Output as JSON
python scripts/version_info.py --format json

# View changelog
python scripts/version_info.py --changelog

# Check for updates
python scripts/version_info.py --check-update
```

### Example Output

```
============================================================
🛡️  PROJECT GUARDIAN SKILL - VERSION INFORMATION
============================================================

📦 Version:        1.4.0
👤 Author:         taokoplay
📝 Name:           project-guardian

📍 Installation:
   Path:           /Users/you/.craft-agent/skills/project-guardian
   Date:           2026-02-27 11:57:07

🔧 Git Information:
   Branch:         main
   Commit:         b7eb2f79
   Commit Date:    2026-02-27 11:43:18 +0800
   Status:         ✅ Clean

✨ Key Features (v1.4.0):
   🧠 Intelligent trigger detection (multi-language)
   ⚡ Smart caching (40% faster, adaptive TTL)
   🔗 Git hooks automation (auto-update on commit/merge)
   📊 Cache statistics and monitoring

📚 Description:
   Intelligent project knowledge management system with
   AUTO-DETECTION and SMART CACHING...
============================================================
```

### Version Comparison

Use this to verify which version you have installed and what features are available:

| Version | Key Features |
|---------|-------------|
| 1.4.0 | Intelligent triggers, smart caching, Git hooks, multi-language |
| 1.3.1 | Test suite, validation, file locking, production-ready |
| 1.3.0 | Query patterns, semantic search, pattern analysis |
| 1.2.0 | Version tracking, health monitoring, changelog |
| 1.1.0 | Quick recording, incremental updates, context-aware loading |
| 1.0.0 | Initial release, project scanning, bug tracking |

## Templates

Use these templates for creating records:
- `assets/bug-template.json` - Bug record template
- `assets/requirement-template.json` - Requirement template
- `assets/decision-template.json` - Architecture decision template
