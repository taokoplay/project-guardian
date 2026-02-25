# Knowledge Base Schema

This document describes the structure and schema of the Project Guardian knowledge base.

## Directory Structure

```
.project-ai/
├── core/                    # Always loaded (<2k tokens)
│   ├── profile.json        # Project metadata
│   ├── tech-stack.json     # Technologies used
│   └── conventions.json    # Code standards
│
├── indexed/                 # Loaded on demand
│   ├── architecture.json   # System architecture
│   ├── modules.json        # Module descriptions
│   ├── tools.json          # Development tools
│   └── structure.json      # Directory structure
│
└── history/                 # Searchable records
    ├── bugs/               # Bug records
    │   ├── _index.json    # Search index
    │   └── BUG-*.json     # Individual bugs
    ├── requirements/       # Requirement records
    │   └── REQ-*.json     # Individual requirements
    └── decisions/          # Architecture decisions
        └── DEC-*.json     # Individual decisions
```

## Core Schemas

### profile.json

```json
{
  "project_name": "string",
  "project_type": "web-frontend | web-backend | full-stack | mobile-ios | mobile-android | library | cli-tool | general",
  "scanned_at": "ISO 8601 timestamp",
  "last_updated": "ISO 8601 timestamp"
}
```

### tech-stack.json

```json
{
  "languages": ["string"],
  "frameworks": ["string"],
  "libraries": ["string"],
  "runtime": ["string"]
}
```

### conventions.json

```json
{
  "naming": ["string"],
  "imports": ["string"],
  "formatting": {
    "semi": boolean,
    "singleQuote": boolean,
    "tabWidth": number,
    "trailingComma": "string"
  },
  "testing": ["string"]
}
```

## Indexed Schemas

### architecture.json

```json
{
  "overview": "string",
  "layers": [
    {
      "name": "string",
      "description": "string",
      "components": ["string"]
    }
  ],
  "data_flow": "string",
  "key_patterns": ["string"],
  "last_updated": "ISO 8601 timestamp"
}
```

### modules.json

```json
{
  "module_name": {
    "path": "string",
    "description": "string",
    "responsibilities": ["string"],
    "dependencies": ["string"],
    "key_files": ["string"],
    "last_updated": "ISO 8601 timestamp"
  }
}
```

### tools.json

```json
{
  "version_control": "string | null",
  "package_manager": "string | null",
  "build_tool": "string | null",
  "linter": ["string"],
  "formatter": ["string"],
  "testing": ["string"],
  "ci_cd": ["string"]
}
```

### structure.json

```json
{
  "root_dirs": ["string"],
  "key_files": ["string"],
  "entry_points": ["string"]
}
```

## History Schemas

### Bug Record (BUG-*.json)

```json
{
  "id": "BUG-YYYYMMDDHHMMSS-xxxx",
  "recorded_at": "ISO 8601 timestamp",
  "title": "string",
  "description": "string",
  "root_cause": "string",
  "solution": "string",
  "files_changed": ["string"],
  "tags": ["string"],
  "severity": "low | medium | high | critical",
  "status": "resolved"
}
```

### Requirement Record (REQ-*.json)

```json
{
  "id": "REQ-YYYYMMDDHHMMSS-xxxx",
  "recorded_at": "ISO 8601 timestamp",
  "title": "string",
  "description": "string",
  "status": "planned | in-progress | completed | cancelled",
  "priority": "low | medium | high | critical",
  "related_modules": ["string"],
  "acceptance_criteria": ["string"],
  "tags": ["string"]
}
```

### Decision Record (DEC-*.json)

```json
{
  "id": "DEC-YYYYMMDDHHMMSS-xxxx",
  "recorded_at": "ISO 8601 timestamp",
  "title": "string",
  "context": "string",
  "decision": "string",
  "rationale": "string",
  "consequences": ["string"],
  "alternatives": ["string"],
  "tags": ["string"]
}
```

### Bug Index (_index.json)

```json
{
  "bugs": [
    {
      "id": "string",
      "title": "string",
      "tags": ["string"],
      "recorded_at": "ISO 8601 timestamp"
    }
  ],
  "tags": {
    "tag_name": ["bug_id"]
  }
}
```

## Token Budget Guidelines

### Core Files (Always Loaded)
- **profile.json**: ~100 tokens
- **tech-stack.json**: ~200 tokens
- **conventions.json**: ~300 tokens
- **Total**: ~600 tokens

### Indexed Files (Conditional)
- **architecture.json**: ~800 tokens
- **modules.json**: ~1000 tokens (load specific modules only)
- **tools.json**: ~200 tokens
- **structure.json**: ~200 tokens

### History Files (Search-Based)
- **Bug record**: ~300 tokens each
- **Requirement record**: ~250 tokens each
- **Decision record**: ~400 tokens each

## Loading Strategy

1. **Always load**: core/* files (~600 tokens)
2. **Conditional load**: indexed/* files based on context keywords
3. **Search load**: history/* files based on similarity search

## Maintenance

### Compression Triggers
- Total history size > 50k tokens
- Number of bug records > 100
- Number of requirement records > 50

### Compression Strategy
- Merge similar bugs (>80% similarity)
- Summarize old decisions (>6 months)
- Archive completed requirements (>3 months)
- Keep recent context (last 30 days) uncompressed
