#!/usr/bin/env python3
"""
Project Guardian - Incremental Knowledge Base Updater

Performs incremental updates to the knowledge base when files change.
Faster than full scan, only analyzes changed files.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class IncrementalUpdater:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"

        if not self.kb_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.kb_path}. "
                "Run scan_project.py first to initialize."
            )

        self.checksums_file = self.kb_path / "indexed" / "_checksums.json"
        self.checksums = self._load_checksums()

    def _load_checksums(self) -> Dict[str, str]:
        """Load file checksums from last scan"""
        if self.checksums_file.exists():
            with open(self.checksums_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_checksums(self):
        """Save updated checksums"""
        self.checksums_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.checksums_file, 'w') as f:
            json.dump(self.checksums, f, indent=2)

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file we should track"""
        code_extensions = {
            '.js', '.jsx', '.ts', '.tsx',  # JavaScript/TypeScript
            '.py',  # Python
            '.go',  # Go
            '.rs',  # Rust
            '.java', '.kt',  # Java/Kotlin
            '.rb',  # Ruby
            '.php',  # PHP
            '.c', '.cpp', '.h', '.hpp',  # C/C++
            '.swift',  # Swift
            '.vue',  # Vue
        }

        config_files = {
            'package.json', 'tsconfig.json', 'vite.config.js', 'webpack.config.js',
            'go.mod', 'Cargo.toml', 'pyproject.toml', 'setup.py',
            '.eslintrc', '.prettierrc', 'tailwind.config.js'
        }

        return (
            file_path.suffix in code_extensions or
            file_path.name in config_files
        )

    def _is_config_file(self, file_path: Path) -> bool:
        """Check if file is a configuration file"""
        config_files = {
            'package.json', 'tsconfig.json', 'vite.config.js', 'webpack.config.js',
            'go.mod', 'Cargo.toml', 'pyproject.toml', 'setup.py',
            '.eslintrc', '.prettierrc', 'tailwind.config.js', '.editorconfig'
        }
        return file_path.name in config_files

    def detect_changes(self) -> Dict[str, List[str]]:
        """Detect which files have changed since last scan"""
        changes = {
            "added": [],
            "modified": [],
            "deleted": []
        }

        # Find all current code files
        current_files = set()
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file() and self._is_code_file(file_path):
                # Skip node_modules, .git, etc.
                if any(part.startswith('.') or part in ['node_modules', 'dist', 'build', '__pycache__']
                       for part in file_path.parts):
                    continue

                rel_path = str(file_path.relative_to(self.project_path))
                current_files.add(rel_path)

                # Calculate checksum
                checksum = self._calculate_checksum(file_path)

                if rel_path not in self.checksums:
                    changes["added"].append(rel_path)
                    self.checksums[rel_path] = checksum
                elif self.checksums[rel_path] != checksum:
                    changes["modified"].append(rel_path)
                    self.checksums[rel_path] = checksum

        # Find deleted files
        for rel_path in list(self.checksums.keys()):
            if rel_path not in current_files:
                changes["deleted"].append(rel_path)
                del self.checksums[rel_path]

        return changes

    def update_tech_stack(self, changed_files: List[str]):
        """Update tech stack if config files changed"""
        config_changed = any(
            self._is_config_file(Path(f)) for f in changed_files
        )

        if not config_changed:
            return

        print("📦 Updating tech stack...")

        tech_stack_file = self.kb_path / "core" / "tech-stack.json"
        tech_stack = {}

        # Re-detect tech stack from config files
        pkg_json_path = self.project_path / "package.json"
        if pkg_json_path.exists():
            with open(pkg_json_path, 'r') as f:
                pkg_json = json.load(f)
                deps = {**pkg_json.get("dependencies", {}), **pkg_json.get("devDependencies", {})}

                frameworks = []
                if "react" in deps:
                    frameworks.append(f"React {deps['react'].strip('^~')}")
                if "vue" in deps:
                    frameworks.append(f"Vue {deps['vue'].strip('^~')}")
                if "next" in deps:
                    frameworks.append(f"Next.js {deps['next'].strip('^~')}")

                tech_stack["frameworks"] = frameworks
                tech_stack["languages"] = ["TypeScript" if "typescript" in deps else "JavaScript"]

        # Save updated tech stack
        with open(tech_stack_file, 'w') as f:
            json.dump(tech_stack, f, indent=2)

        print(f"  ✓ Updated tech stack: {', '.join(tech_stack.get('frameworks', []))}")

    def update_structure(self, changes: Dict[str, List[str]]):
        """Update project structure if files added/deleted"""
        if not changes["added"] and not changes["deleted"]:
            return

        print("📂 Updating project structure...")

        structure_file = self.kb_path / "indexed" / "structure.json"

        # Analyze current structure
        structure = {
            "root_dirs": [],
            "entry_points": [],
            "test_dirs": []
        }

        # Find root directories
        root_items = set()
        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in ['node_modules', 'dist', 'build']:
                root_items.add(item.name)

        structure["root_dirs"] = sorted(root_items)

        # Find entry points
        entry_patterns = ['index.js', 'index.ts', 'main.js', 'main.ts', 'app.js', 'app.ts', 'server.js']
        for pattern in entry_patterns:
            for file_path in self.project_path.rglob(pattern):
                if 'node_modules' not in file_path.parts:
                    structure["entry_points"].append(str(file_path.relative_to(self.project_path)))

        # Save updated structure
        with open(structure_file, 'w') as f:
            json.dump(structure, f, indent=2)

        print(f"  ✓ Updated structure: {len(structure['root_dirs'])} root dirs, {len(structure['entry_points'])} entry points")

    def update_profile(self):
        """Update profile with last update timestamp"""
        profile_file = self.kb_path / "core" / "profile.json"

        if profile_file.exists():
            with open(profile_file, 'r') as f:
                profile = json.load(f)
        else:
            profile = {}

        profile["last_updated"] = datetime.now().isoformat()
        profile["update_type"] = "incremental"

        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)

    def run(self) -> Dict[str, Any]:
        """Run incremental update"""
        print(f"🔄 Running incremental update for: {self.project_path}")

        # Detect changes
        changes = self.detect_changes()

        total_changes = len(changes["added"]) + len(changes["modified"]) + len(changes["deleted"])

        if total_changes == 0:
            print("✅ No changes detected. Knowledge base is up to date.")
            return {"changes": changes, "updated": False}

        print(f"\n📊 Detected changes:")
        print(f"  + Added: {len(changes['added'])} files")
        print(f"  ~ Modified: {len(changes['modified'])} files")
        print(f"  - Deleted: {len(changes['deleted'])} files")
        print()

        # Update relevant parts of knowledge base
        all_changed = changes["added"] + changes["modified"]

        self.update_tech_stack(all_changed)
        self.update_structure(changes)
        self.update_profile()

        # Save checksums
        self._save_checksums()

        print("\n✅ Incremental update completed")

        return {
            "changes": changes,
            "updated": True,
            "timestamp": datetime.now().isoformat()
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python incremental_update.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]

    try:
        updater = IncrementalUpdater(project_path)
        result = updater.run()

        # Print summary
        if result["updated"]:
            print(f"\n📝 Summary:")
            print(f"  Total changes: {len(result['changes']['added']) + len(result['changes']['modified']) + len(result['changes']['deleted'])}")
            print(f"  Updated at: {result['timestamp']}")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
