#!/usr/bin/env python3
"""
Project Guardian - Version Tracker

Tracks Git commits and associates knowledge base updates with code versions.
Enables historical analysis and understanding of how the project evolved.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class VersionTracker:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"

        if not self.kb_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.kb_path}. "
                "Run scan_project.py first to initialize."
            )

        self.version_file = self.kb_path / "core" / "version-history.json"
        self.version_history = self._load_version_history()

    def _load_version_history(self) -> List[Dict[str, Any]]:
        """Load version history from file"""
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                return json.load(f)
        return []

    def _save_version_history(self):
        """Save version history to file"""
        self.version_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.version_file, 'w') as f:
            json.dump(self.version_history, f, indent=2)

    def _run_git_command(self, *args) -> Optional[str]:
        """Run a git command and return output"""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.project_path)] + list(args),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def _is_git_repo(self) -> bool:
        """Check if project is a git repository"""
        return (self.project_path / ".git").exists()

    def get_current_commit(self) -> Optional[Dict[str, str]]:
        """Get current Git commit information"""
        if not self._is_git_repo():
            return None

        commit_hash = self._run_git_command('rev-parse', 'HEAD')
        if not commit_hash:
            return None

        commit_message = self._run_git_command('log', '-1', '--pretty=%B')
        commit_author = self._run_git_command('log', '-1', '--pretty=%an')
        commit_date = self._run_git_command('log', '-1', '--pretty=%ai')
        branch = self._run_git_command('rev-parse', '--abbrev-ref', 'HEAD')

        return {
            "hash": commit_hash,
            "short_hash": commit_hash[:7],
            "message": commit_message or "",
            "author": commit_author or "",
            "date": commit_date or "",
            "branch": branch or "unknown"
        }

    def get_commit_stats(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific commit"""
        if not self._is_git_repo():
            return None

        # Get files changed
        files_changed = self._run_git_command('diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash)
        if files_changed:
            files_list = files_changed.split('\n')
        else:
            files_list = []

        # Get stats
        stats = self._run_git_command('show', '--stat', '--oneline', commit_hash)

        return {
            "files_changed": files_list,
            "total_files": len(files_list),
            "stats": stats or ""
        }

    def record_version(self, update_type: str, changes: Optional[Dict[str, Any]] = None) -> str:
        """Record a new version entry"""
        commit_info = self.get_current_commit()

        version_entry = {
            "timestamp": datetime.now().isoformat(),
            "update_type": update_type,  # "initial_scan", "incremental_update", "manual_update"
            "changes": changes or {},
        }

        if commit_info:
            version_entry["git"] = commit_info
            commit_stats = self.get_commit_stats(commit_info["hash"])
            if commit_stats:
                version_entry["git"]["stats"] = commit_stats

        self.version_history.append(version_entry)
        self._save_version_history()

        if commit_info:
            return f"v{len(self.version_history)} @ {commit_info['short_hash']}"
        else:
            return f"v{len(self.version_history)} (no git)"

    def get_version_at_commit(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Find knowledge base version at a specific commit"""
        for entry in reversed(self.version_history):
            if entry.get("git", {}).get("hash", "").startswith(commit_hash):
                return entry
        return None

    def get_recent_versions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent version entries"""
        return self.version_history[-limit:]

    def associate_bug_with_commit(self, bug_id: str, fixed_in_commit: Optional[str] = None,
                                   introduced_in_commit: Optional[str] = None):
        """Associate a bug with Git commits"""
        bugs_dir = self.kb_path / "history" / "bugs"
        bug_file = bugs_dir / f"{bug_id}.json"

        if not bug_file.exists():
            print(f"❌ Bug {bug_id} not found")
            return

        with open(bug_file, 'r') as f:
            bug = json.load(f)

        # Add commit associations
        if fixed_in_commit:
            bug["fixed_in_commit"] = fixed_in_commit
            commit_info = self.get_current_commit()
            if commit_info and commit_info["hash"].startswith(fixed_in_commit):
                bug["fixed_at"] = commit_info["date"]

        if introduced_in_commit:
            bug["introduced_in_commit"] = introduced_in_commit

        with open(bug_file, 'w') as f:
            json.dump(bug, f, indent=2)

        print(f"✅ Updated {bug_id} with commit associations")

    def find_bugs_in_commit_range(self, start_commit: str, end_commit: str = "HEAD") -> List[str]:
        """Find bugs fixed in a commit range"""
        if not self._is_git_repo():
            return []

        # Get commit messages in range
        log = self._run_git_command('log', f'{start_commit}..{end_commit}', '--pretty=%H %s')
        if not log:
            return []

        # Look for bug references in commit messages
        bug_ids = []
        for line in log.split('\n'):
            # Match patterns like "fix BUG-20240225-001" or "fixes #BUG-001"
            import re
            matches = re.findall(r'BUG-\d{8}-\d{3}', line)
            bug_ids.extend(matches)

        return list(set(bug_ids))

    def generate_changelog(self, since_version: Optional[int] = None) -> str:
        """Generate changelog from version history"""
        if since_version is None:
            entries = self.version_history
        else:
            entries = self.version_history[since_version:]

        changelog = []
        changelog.append("# Knowledge Base Changelog\n")

        for i, entry in enumerate(entries, start=1):
            timestamp = entry["timestamp"][:10]  # Just the date
            update_type = entry["update_type"]

            git_info = entry.get("git", {})
            if git_info:
                commit_hash = git_info.get("short_hash", "")
                commit_msg = git_info.get("message", "").split('\n')[0]  # First line only
                changelog.append(f"## Version {i} - {timestamp} ({commit_hash})")
                changelog.append(f"**Commit**: {commit_msg}")
            else:
                changelog.append(f"## Version {i} - {timestamp}")

            changelog.append(f"**Update Type**: {update_type}\n")

            # Add changes summary
            changes = entry.get("changes", {})
            if changes:
                if "added" in changes and changes["added"]:
                    changelog.append(f"- Added {len(changes['added'])} files")
                if "modified" in changes and changes["modified"]:
                    changelog.append(f"- Modified {len(changes['modified'])} files")
                if "deleted" in changes and changes["deleted"]:
                    changelog.append(f"- Deleted {len(changes['deleted'])} files")

            changelog.append("")  # Empty line

        return "\n".join(changelog)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Record version:        python version_tracker.py <project_path> --record <update_type>")
        print("  Get current commit:    python version_tracker.py <project_path> --current")
        print("  Get recent versions:   python version_tracker.py <project_path> --recent [limit]")
        print("  Associate bug:         python version_tracker.py <project_path> --bug <bug_id> --fixed <commit> [--introduced <commit>]")
        print("  Generate changelog:    python version_tracker.py <project_path> --changelog [since_version]")
        print("  Find bugs in range:    python version_tracker.py <project_path> --bugs-in-range <start_commit> [end_commit]")
        sys.exit(1)

    project_path = sys.argv[1]

    try:
        tracker = VersionTracker(project_path)

        if "--record" in sys.argv:
            idx = sys.argv.index("--record")
            update_type = sys.argv[idx + 1]
            version = tracker.record_version(update_type)
            print(f"✅ Recorded version: {version}")

        elif "--current" in sys.argv:
            commit = tracker.get_current_commit()
            if commit:
                print(json.dumps(commit, indent=2))
            else:
                print("❌ Not a git repository or no commits")

        elif "--recent" in sys.argv:
            limit = 10
            if len(sys.argv) > sys.argv.index("--recent") + 1:
                try:
                    limit = int(sys.argv[sys.argv.index("--recent") + 1])
                except ValueError:
                    pass

            versions = tracker.get_recent_versions(limit)
            print(json.dumps(versions, indent=2))

        elif "--bug" in sys.argv:
            bug_idx = sys.argv.index("--bug")
            bug_id = sys.argv[bug_idx + 1]

            fixed_commit = None
            introduced_commit = None

            if "--fixed" in sys.argv:
                fixed_idx = sys.argv.index("--fixed")
                fixed_commit = sys.argv[fixed_idx + 1]

            if "--introduced" in sys.argv:
                intro_idx = sys.argv.index("--introduced")
                introduced_commit = sys.argv[intro_idx + 1]

            tracker.associate_bug_with_commit(bug_id, fixed_commit, introduced_commit)

        elif "--changelog" in sys.argv:
            since_version = None
            if len(sys.argv) > sys.argv.index("--changelog") + 1:
                try:
                    since_version = int(sys.argv[sys.argv.index("--changelog") + 1])
                except ValueError:
                    pass

            changelog = tracker.generate_changelog(since_version)
            print(changelog)

        elif "--bugs-in-range" in sys.argv:
            range_idx = sys.argv.index("--bugs-in-range")
            start_commit = sys.argv[range_idx + 1]
            end_commit = "HEAD"

            if len(sys.argv) > range_idx + 2:
                end_commit = sys.argv[range_idx + 2]

            bugs = tracker.find_bugs_in_commit_range(start_commit, end_commit)
            print(f"Found {len(bugs)} bugs in commit range:")
            for bug_id in bugs:
                print(f"  - {bug_id}")

        else:
            print("❌ Invalid arguments")
            sys.exit(1)

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
