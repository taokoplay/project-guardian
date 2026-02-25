#!/usr/bin/env python3
"""
Quick check if a project has Project Guardian initialized.
Returns exit code 0 if initialized, 1 if not.
"""

import sys
import json
from pathlib import Path


def find_project_root(start_path: Path) -> Path | None:
    """
    Find project root by looking for .project-ai/ directory.
    Searches current directory and up to 3 parent levels.
    """
    current = start_path.resolve()

    # Check current directory and up to 3 parents
    for _ in range(4):
        knowledge_base = current / ".project-ai"
        if knowledge_base.exists() and knowledge_base.is_dir():
            return current

        if current.parent == current:  # Reached filesystem root
            break
        current = current.parent

    return None


def check_knowledge_base(project_root: Path) -> dict:
    """
    Check knowledge base completeness and return status.
    """
    kb_path = project_root / ".project-ai"

    status = {
        "initialized": True,
        "project_root": str(project_root),
        "knowledge_base_path": str(kb_path),
        "core_files": {},
        "indexed_files": {},
        "history_dirs": {},
        "warnings": []
    }

    # Check core files
    core_files = ["profile.json", "tech-stack.json", "conventions.json"]
    for file in core_files:
        file_path = kb_path / "core" / file
        status["core_files"][file] = file_path.exists()
        if not file_path.exists():
            status["warnings"].append(f"Missing core file: {file}")

    # Check indexed files
    indexed_files = ["architecture.json", "modules.json", "tools.json", "structure.json"]
    for file in indexed_files:
        file_path = kb_path / "indexed" / file
        status["indexed_files"][file] = file_path.exists()

    # Check history directories
    history_dirs = ["bugs", "requirements", "decisions"]
    for dir_name in history_dirs:
        dir_path = kb_path / "history" / dir_name
        status["history_dirs"][dir_name] = dir_path.exists()

    return status


def is_likely_project(path: Path) -> bool:
    """
    Check if the directory looks like a code project.
    """
    project_indicators = [
        "package.json",      # Node.js
        "go.mod",            # Go
        "Cargo.toml",        # Rust
        "pyproject.toml",    # Python (modern)
        "setup.py",          # Python (legacy)
        "pom.xml",           # Java (Maven)
        "build.gradle",      # Java (Gradle)
        "composer.json",     # PHP
        "Gemfile",           # Ruby
        ".git",              # Git repository
    ]

    for indicator in project_indicators:
        if (path / indicator).exists():
            return True

    return False


def main():
    # Get target directory from args or use current directory
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])
    else:
        target_path = Path.cwd()

    if not target_path.exists():
        print(json.dumps({
            "initialized": False,
            "error": f"Path does not exist: {target_path}"
        }))
        sys.exit(1)

    # Find project root
    project_root = find_project_root(target_path)

    if project_root:
        # Project is initialized
        status = check_knowledge_base(project_root)
        print(json.dumps(status, indent=2))
        sys.exit(0)
    else:
        # Not initialized - check if it's a project
        is_project = is_likely_project(target_path)

        result = {
            "initialized": False,
            "current_path": str(target_path),
            "is_likely_project": is_project,
            "suggestion": (
                "This looks like a code project. Run 'python scripts/scan_project.py .' to initialize."
                if is_project
                else "This doesn't appear to be a code project directory."
            )
        }

        print(json.dumps(result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
