#!/usr/bin/env python3
"""
Project Guardian - Git Hooks Automation

Automatically updates knowledge base on Git events:
- post-commit: Record version and update checksums
- pre-push: Validate knowledge base health
- post-merge: Incremental update after merge
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional


class GitHooksManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"
        self.git_dir = self.project_path / ".git"
        self.hooks_dir = self.git_dir / "hooks"

        if not self.git_dir.exists():
            raise FileNotFoundError(
                f"Git repository not found at {self.project_path}. "
                "Initialize git first: git init"
            )

    def _get_script_path(self, script_name: str) -> Path:
        """Get absolute path to a Project Guardian script"""
        # Assume scripts are in the same directory as this file
        scripts_dir = Path(__file__).parent
        return scripts_dir / script_name

    def _create_hook(self, hook_name: str, hook_content: str):
        """Create a Git hook file"""
        hook_file = self.hooks_dir / hook_name

        # Create hooks directory if it doesn't exist
        self.hooks_dir.mkdir(parents=True, exist_ok=True)

        # Write hook content
        with open(hook_file, 'w') as f:
            f.write(hook_content)

        # Make executable
        hook_file.chmod(0o755)

        print(f"✅ Created hook: {hook_name}")

    def install_post_commit_hook(self):
        """Install post-commit hook for version tracking"""
        version_tracker = self._get_script_path("version_tracker.py")

        hook_content = f"""#!/bin/bash
# Project Guardian - Post-Commit Hook
# Automatically records Git commit in knowledge base

PROJECT_PATH="{self.project_path}"
KB_PATH="$PROJECT_PATH/.project-ai"

# Check if knowledge base exists
if [ ! -d "$KB_PATH" ]; then
    echo "⚠️  Project Guardian: Knowledge base not initialized"
    exit 0
fi

# Record version
echo "📌 Project Guardian: Recording commit version..."
python3 "{version_tracker}" "$PROJECT_PATH" --record-current

# Update checksums for incremental updates
CHECKSUMS_FILE="$KB_PATH/indexed/checksums.json"
if [ -f "$CHECKSUMS_FILE" ]; then
    echo "🔄 Project Guardian: Updating checksums..."
    python3 "{self._get_script_path('incremental_update.py')}" "$PROJECT_PATH" --update-checksums-only
fi

exit 0
"""

        self._create_hook("post-commit", hook_content)

    def install_pre_push_hook(self):
        """Install pre-push hook for health validation"""
        health_checker = self._get_script_path("health_checker.py")

        hook_content = f"""#!/bin/bash
# Project Guardian - Pre-Push Hook
# Validates knowledge base health before push

PROJECT_PATH="{self.project_path}"
KB_PATH="$PROJECT_PATH/.project-ai"

# Check if knowledge base exists
if [ ! -d "$KB_PATH" ]; then
    echo "⚠️  Project Guardian: Knowledge base not initialized"
    exit 0
fi

# Check health
echo "🏥 Project Guardian: Checking knowledge base health..."
python3 "{health_checker}" "$PROJECT_PATH" --quick

# Get health score
HEALTH_OUTPUT=$(python3 "{health_checker}" "$PROJECT_PATH" --score-only)
HEALTH_SCORE=$(echo "$HEALTH_OUTPUT" | grep -oE '[0-9]+')

# Warn if health is poor (< 60)
if [ "$HEALTH_SCORE" -lt 60 ]; then
    echo "⚠️  Project Guardian: Knowledge base health is poor (score: $HEALTH_SCORE)"
    echo "   Consider running: python3 {health_checker} $PROJECT_PATH"
    echo ""
    read -p "Continue with push? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Push cancelled"
        exit 1
    fi
fi

echo "✅ Project Guardian: Health check passed (score: $HEALTH_SCORE)"
exit 0
"""

        self._create_hook("pre-push", hook_content)

    def install_post_merge_hook(self):
        """Install post-merge hook for incremental updates"""
        incremental_update = self._get_script_path("incremental_update.py")

        hook_content = f"""#!/bin/bash
# Project Guardian - Post-Merge Hook
# Automatically updates knowledge base after merge

PROJECT_PATH="{self.project_path}"
KB_PATH="$PROJECT_PATH/.project-ai"

# Check if knowledge base exists
if [ ! -d "$KB_PATH" ]; then
    echo "⚠️  Project Guardian: Knowledge base not initialized"
    exit 0
fi

# Run incremental update
echo "🔄 Project Guardian: Running incremental update after merge..."
python3 "{incremental_update}" "$PROJECT_PATH" --auto

# Record merge commit
echo "📌 Project Guardian: Recording merge commit..."
python3 "{self._get_script_path('version_tracker.py')}" "$PROJECT_PATH" --record-current

exit 0
"""

        self._create_hook("post-merge", hook_content)

    def install_commit_msg_hook(self):
        """Install commit-msg hook for bug extraction"""
        hook_content = f"""#!/bin/bash
# Project Guardian - Commit-Msg Hook
# Extracts bug fixes from commit messages

PROJECT_PATH="{self.project_path}"
KB_PATH="$PROJECT_PATH/.project-ai"
COMMIT_MSG_FILE="$1"

# Check if knowledge base exists
if [ ! -d "$KB_PATH" ]; then
    exit 0
fi

# Read commit message
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Check for bug fix patterns
if echo "$COMMIT_MSG" | grep -qiE "(fix|fixed|fixes|resolve|resolved|resolves|close|closed|closes).*#[0-9]+"; then
    echo "🐛 Project Guardian: Bug fix detected in commit message"

    # Extract bug ID
    BUG_ID=$(echo "$COMMIT_MSG" | grep -oiE "#[0-9]+" | head -1 | tr -d '#')

    if [ ! -z "$BUG_ID" ]; then
        # Try to mark bug as resolved
        BUG_FILE="$KB_PATH/history/bugs/BUG-$BUG_ID.json"
        if [ -f "$BUG_FILE" ]; then
            echo "   Marking BUG-$BUG_ID as resolved..."
            python3 "{self._get_script_path('update_knowledge.py')}" "$PROJECT_PATH" \\
                --update-bug "BUG-$BUG_ID" --status resolved \\
                --solution "Fixed in commit $(git rev-parse --short HEAD)" \\
                2>/dev/null || true
        fi
    fi
fi

exit 0
"""

        self._create_hook("commit-msg", hook_content)

    def install_all_hooks(self):
        """Install all recommended hooks"""
        print("🔧 Installing Project Guardian Git hooks...")
        print()

        self.install_post_commit_hook()
        self.install_pre_push_hook()
        self.install_post_merge_hook()
        self.install_commit_msg_hook()

        print()
        print("✅ All hooks installed successfully!")
        print()
        print("Installed hooks:")
        print("  • post-commit:  Records Git commit in knowledge base")
        print("  • pre-push:     Validates knowledge base health")
        print("  • post-merge:   Updates knowledge base after merge")
        print("  • commit-msg:   Extracts bug fixes from commit messages")

    def uninstall_hooks(self):
        """Remove all Project Guardian hooks"""
        hooks = ["post-commit", "pre-push", "post-merge", "commit-msg"]

        removed = 0
        for hook in hooks:
            hook_file = self.hooks_dir / hook
            if hook_file.exists():
                # Check if it's a Project Guardian hook
                with open(hook_file, 'r') as f:
                    content = f.read()
                    if "Project Guardian" in content:
                        hook_file.unlink()
                        print(f"✅ Removed hook: {hook}")
                        removed += 1

        if removed > 0:
            print(f"\n✅ Removed {removed} Project Guardian hooks")
        else:
            print("⚠️  No Project Guardian hooks found")

    def list_hooks(self):
        """List installed hooks"""
        if not self.hooks_dir.exists():
            print("⚠️  No hooks directory found")
            return

        hooks = ["post-commit", "pre-push", "post-merge", "commit-msg"]

        print("📋 Git Hooks Status:")
        print()

        for hook in hooks:
            hook_file = self.hooks_dir / hook
            if hook_file.exists():
                with open(hook_file, 'r') as f:
                    content = f.read()
                    if "Project Guardian" in content:
                        print(f"  ✅ {hook:15} (Project Guardian)")
                    else:
                        print(f"  ⚠️  {hook:15} (Custom - not Project Guardian)")
            else:
                print(f"  ❌ {hook:15} (Not installed)")

    def test_hooks(self):
        """Test if hooks are working"""
        print("🧪 Testing Project Guardian hooks...")
        print()

        hooks = ["post-commit", "pre-push", "post-merge", "commit-msg"]

        for hook in hooks:
            hook_file = self.hooks_dir / hook
            if hook_file.exists() and hook_file.stat().st_mode & 0o111:
                print(f"  ✅ {hook:15} (Installed and executable)")
            elif hook_file.exists():
                print(f"  ⚠️  {hook:15} (Installed but not executable)")
            else:
                print(f"  ❌ {hook:15} (Not installed)")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Install all hooks:    python auto_hooks.py <project_path> --install")
        print("  Install specific:     python auto_hooks.py <project_path> --install-<hook>")
        print("                        (post-commit, pre-push, post-merge, commit-msg)")
        print("  Uninstall hooks:      python auto_hooks.py <project_path> --uninstall")
        print("  List hooks:           python auto_hooks.py <project_path> --list")
        print("  Test hooks:           python auto_hooks.py <project_path> --test")
        print()
        print("Examples:")
        print("  python auto_hooks.py /path/to/project --install")
        print("  python auto_hooks.py /path/to/project --install-post-commit")
        print("  python auto_hooks.py /path/to/project --list")
        sys.exit(1)

    project_path = sys.argv[1]

    try:
        manager = GitHooksManager(project_path)

        if "--install" in sys.argv:
            manager.install_all_hooks()

        elif "--install-post-commit" in sys.argv:
            manager.install_post_commit_hook()

        elif "--install-pre-push" in sys.argv:
            manager.install_pre_push_hook()

        elif "--install-post-merge" in sys.argv:
            manager.install_post_merge_hook()

        elif "--install-commit-msg" in sys.argv:
            manager.install_commit_msg_hook()

        elif "--uninstall" in sys.argv:
            manager.uninstall_hooks()

        elif "--list" in sys.argv:
            manager.list_hooks()

        elif "--test" in sys.argv:
            manager.test_hooks()

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
