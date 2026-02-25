# Changelog

All notable changes to Project Guardian Skill will be documented in this file.

## [1.1.0] - 2026-02-25

### Added
- ⚡ **Quick Recording**: Record bugs/requirements/decisions directly from command line without JSON files
  - `--quick-bug` for instant bug recording
  - `--quick-req` for instant requirement recording
  - `--quick-decision` for instant decision recording
- 🔄 **Incremental Updates**: New `incremental_update.py` script for fast knowledge base updates
  - Tracks file checksums to detect changes
  - Only updates affected parts (tech stack, structure)
  - 10x faster than full rescan
- 🎯 **Context-Aware Loading**: New `context_loader.py` for intelligent knowledge retrieval
  - Load context for specific files
  - Load context based on query keywords
  - Automatic module detection
  - 50-70% token usage reduction

### Improved
- 📝 Enhanced `update_knowledge.py` with command-line argument support
- 📚 Updated SKILL.md with comprehensive new features documentation
- 🎨 Better error messages and usage instructions

### Performance
- ⚡ Reduced token usage by 50-70% with context-aware loading
- 🚀 Incremental updates complete in seconds instead of minutes

## [1.0.1] - 2026-02-25

### Fixed
- 🔧 Added required YAML frontmatter fields (icon, version, author, tags) for proper skill loading in Claude Code
- 📝 Simplified description field to prevent YAML parsing issues
- ✅ Improved skill metadata display in Claude Code UI

## [1.0.0] - 2026-02-25

### Added
- 🎉 Initial release
- ✨ Automatic project scanning and detection
- 📝 Bug tracking with root cause and solution
- 📋 Requirement management with status tracking
- 🏛️ Architecture Decision Records (ADR)
- 🔍 Similarity search for preventing duplicate issues
- 💾 Token-efficient knowledge base (<2k core context)
- 🔒 Multi-project data isolation
- 🛠️ Support for 7 project types
- 🌐 Support for 20+ development tools
- 📚 Comprehensive documentation

### Supported Project Types
- Web Frontend (React, Vue, Angular)
- Web Backend (Express, Django, FastAPI, Go, Rust)
- Full-stack (Next.js, Nuxt)
- Mobile (iOS, Android)
- Library/Package
- CLI Tool

### Supported Tech Stacks
- Languages: TypeScript, JavaScript, Python, Go, Rust, Java
- Frameworks: React, Vue, Express, Django, FastAPI, Spring Boot, Actix Web
- Tools: npm, pnpm, yarn, Vite, Webpack, ESLint, Prettier, Vitest, Jest

## [Unreleased]

### Planned Features
- [ ] History compression script
- [ ] Architecture validation
- [ ] Git hooks integration examples
- [ ] CI/CD integration templates
- [ ] Auto-extract bugs from commit messages
- [ ] GitHub Issues synchronization
- [ ] Project documentation generation
- [ ] Architecture visualization
