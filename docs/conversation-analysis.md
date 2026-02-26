# Conversation Analysis & Auto-Recording

## Overview

Project Guardian can automatically analyze conversations to detect important information that should be recorded in the knowledge base.

## Quick Start

```bash
# Analyze a conversation
python response_analyzer.py /path/to/project \
  --user "I found a bug in authentication" \
  --assistant "The bug is caused by missing token validation. Fix: add validation in middleware."

# With auto-recording
python conversation_hook.py /path/to/project \
  --user "..." --assistant "..."
```

## Detection Types

### 🐛 Bug Detection
- Error messages and exceptions
- Root causes and solutions
- Reproduction steps
- **Auto-record**: Yes (default)

### 🏛️ Architecture Decisions
- Design choices and rationale
- Trade-offs and alternatives
- Technical decisions
- **Auto-record**: Yes (default)

### 📋 Requirements
- Feature descriptions
- User stories and use cases
- Acceptance criteria
- **Auto-record**: No (suggest only)

### 📏 Conventions
- Coding standards
- Naming conventions
- Best practices
- **Auto-record**: No (suggest only)

### ⚡ Performance
- Bottlenecks and optimizations
- Performance metrics
- Caching strategies
- **Auto-record**: No (suggest only)

## Configuration

### Setup

```bash
# Copy template
cp assets/conversation-hook-config.json .project-ai/config/

# Edit thresholds
{
  "auto_record_threshold": 0.8,  // Auto-record if confidence ≥ 0.8
  "suggest_threshold": 0.5,      // Suggest if confidence ≥ 0.5
  "notification_style": "inline" // inline, summary, or silent
}
```

### Notification Styles

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
```

**Silent** (no output, check logs)

## Integration with Claude Code

### Option 1: Manual Trigger

After important conversations, run:
```bash
python conversation_hook.py . \
  --user "last user message" \
  --assistant "last assistant response"
```

### Option 2: Skill Integration

Add to SKILL.md workflow:
```markdown
After providing solution, analyze if recordable:
1. Check for bug/decision/requirement patterns
2. If confidence ≥ 0.5, suggest recording
3. If confidence ≥ 0.8, auto-record
```

### Option 3: Post-Conversation Hook

Create a wrapper script that Claude Code calls after each turn:
```bash
#!/bin/bash
# Save last conversation to temp file
# Call conversation_hook.py
# Display notification if needed
```

## Statistics

View conversation analysis statistics:
```bash
python conversation_hook.py /path/to/project --stats

# Output:
{
  "total_conversations": 150,
  "auto_recorded": 12,
  "suggested": 28,
  "by_type": {
    "bug": 8,
    "decision": 4,
    "requirement": 15,
    "convention": 10,
    "performance": 3
  }
}
```

## Advanced Usage

### Custom Context

Provide additional context for better analysis:
```bash
python conversation_hook.py . \
  --user "..." --assistant "..." \
  --context context.json

# context.json:
{
  "current_file": "src/auth/middleware.ts",
  "module": "auth",
  "conversation_history": [...]
}
```

### Batch Analysis

Analyze multiple conversations:
```bash
for conv in conversations/*.json; do
  python conversation_hook.py . --json "$conv"
done
```

### Custom Patterns

Extend detection patterns in `response_analyzer.py`:
```python
self.recordable_patterns["custom_type"] = {
    "indicators": [r"pattern1", r"pattern2"],
    "chinese": [r"中文模式1", r"中文模式2"]
}
```

## Best Practices

1. **Review auto-recorded items**: Check `.project-ai/history/` periodically
2. **Adjust thresholds**: Start conservative (0.8), tune based on results
3. **Use context**: Provide current file/module for better accuracy
4. **Check statistics**: Monitor false positives/negatives
5. **Customize patterns**: Add domain-specific patterns for your project

## Troubleshooting

**Too many false positives:**
- Increase `auto_record_threshold` to 0.9
- Disable auto-record for certain types
- Add skip patterns

**Missing important content:**
- Decrease `suggest_threshold` to 0.3
- Check if patterns match your domain
- Add custom patterns

**No notifications:**
- Check `enabled: true` in config
- Verify notification_style is not "silent"
- Check if knowledge base exists

## Examples

### Example 1: Bug Auto-Recorded

**Input:**
```
User: Login fails with "Invalid token" error
Assistant: The issue is in auth middleware. Token validation is missing.
          Fix: Add token.verify() before processing request.
```

**Output:**
```
🤖 [Project Guardian] Auto-recorded bug (confidence: 0.92)

Bug recorded as: BUG-20260226-001
- Error: Invalid token
- Root cause: Missing token validation in middleware
- Solution: Add token.verify() call
```

### Example 2: Decision Suggested

**Input:**
```
User: Should we use REST or GraphQL?
Assistant: I recommend GraphQL because it reduces over-fetching and provides
          better type safety. Trade-off: steeper learning curve.
```

**Output:**
```
💡 [Project Guardian] Recordable content detected:
   Type: decision
   Confidence: 0.75
   Suggestions:
     - Record as Architecture Decision Record (ADR)
     - Use: python update_knowledge.py . --quick-decision
```

## Performance

- Analysis time: ~50ms per conversation
- Memory usage: <10MB
- No impact on conversation flow
- Async processing recommended for production

## Future Enhancements

- [ ] Machine learning-based classification
- [ ] Semantic similarity for duplicate detection
- [ ] Integration with issue trackers
- [ ] Automatic tagging and categorization
- [ ] Multi-turn conversation analysis
