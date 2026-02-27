#!/usr/bin/env python3
"""
Version Information Tool for Project Guardian Skill

Displays version information, changelog, and system details.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess

def get_skill_root():
    """Get the skill root directory."""
    return Path(__file__).parent.parent

def read_skill_metadata():
    """Read version and metadata from SKILL.md."""
    skill_md = get_skill_root() / "SKILL.md"

    if not skill_md.exists():
        return None

    metadata = {}
    with open(skill_md, 'r', encoding='utf-8') as f:
        in_frontmatter = False
        for line in f:
            line = line.strip()
            if line == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break
            elif in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()

    return metadata

def get_git_info():
    """Get Git repository information."""
    skill_root = get_skill_root()
    git_info = {}

    try:
        # Get current commit hash
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=skill_root,
            capture_output=True,
            text=True,
            check=True
        )
        git_info['commit'] = result.stdout.strip()[:8]

        # Get commit date
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ci'],
            cwd=skill_root,
            capture_output=True,
            text=True,
            check=True
        )
        git_info['commit_date'] = result.stdout.strip()

        # Get branch
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=skill_root,
            capture_output=True,
            text=True,
            check=True
        )
        git_info['branch'] = result.stdout.strip()

        # Check for uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=skill_root,
            capture_output=True,
            text=True,
            check=True
        )
        git_info['dirty'] = bool(result.stdout.strip())

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return git_info

def get_installation_info():
    """Get installation information."""
    skill_root = get_skill_root()

    info = {
        'install_path': str(skill_root),
        'install_date': None
    }

    # Try to get installation date from .git directory
    git_dir = skill_root / '.git'
    if git_dir.exists():
        info['install_date'] = datetime.fromtimestamp(
            git_dir.stat().st_ctime
        ).strftime('%Y-%m-%d %H:%M:%S')

    return info

def get_feature_summary(version):
    """Get feature summary for the version."""
    features = {
        '1.4.0': [
            '🧠 Intelligent trigger detection (multi-language)',
            '⚡ Smart caching (40% faster, adaptive TTL)',
            '🔗 Git hooks automation (auto-update on commit/merge)',
            '📊 Cache statistics and monitoring'
        ],
        '1.3.1': [
            '✅ Complete test suite (40 tests, 100% pass rate)',
            '🔒 Input validation with JSON Schema',
            '🔐 File locking for concurrent access',
            '🛠️ Production-ready optimizations'
        ],
        '1.3.0': [
            '🧠 Query pattern learning',
            '🎯 Semantic search (optional)',
            '📊 Pattern analysis and recommendations'
        ],
        '1.2.0': [
            '📌 Version tracking & Git integration',
            '🏥 Health monitoring',
            '📈 Knowledge base changelog'
        ],
        '1.1.0': [
            '⚡ Quick recording (no JSON files needed)',
            '🔄 Incremental updates',
            '🎯 Context-aware loading'
        ]
    }

    return features.get(version, [])

def display_version_info(format='text'):
    """Display version information."""
    metadata = read_skill_metadata()
    git_info = get_git_info()
    install_info = get_installation_info()

    if not metadata:
        print("❌ Error: Could not read skill metadata", file=sys.stderr)
        return 1

    version = metadata.get('version', 'unknown')

    if format == 'json':
        output = {
            'version': version,
            'name': metadata.get('name', 'unknown'),
            'author': metadata.get('author', 'unknown'),
            'description': metadata.get('description', ''),
            'git': git_info,
            'installation': install_info,
            'features': get_feature_summary(version)
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        # Text format
        print("=" * 60)
        print("🛡️  PROJECT GUARDIAN SKILL - VERSION INFORMATION")
        print("=" * 60)
        print()

        print(f"📦 Version:        {version}")
        print(f"👤 Author:         {metadata.get('author', 'unknown')}")
        print(f"📝 Name:           {metadata.get('name', 'unknown')}")
        print()

        print("📍 Installation:")
        print(f"   Path:           {install_info['install_path']}")
        if install_info['install_date']:
            print(f"   Date:           {install_info['install_date']}")
        print()

        if git_info:
            print("🔧 Git Information:")
            print(f"   Branch:         {git_info.get('branch', 'unknown')}")
            print(f"   Commit:         {git_info.get('commit', 'unknown')}")
            if git_info.get('commit_date'):
                print(f"   Commit Date:    {git_info['commit_date']}")
            if git_info.get('dirty'):
                print(f"   Status:         ⚠️  Uncommitted changes")
            else:
                print(f"   Status:         ✅ Clean")
            print()

        features = get_feature_summary(version)
        if features:
            print(f"✨ Key Features (v{version}):")
            for feature in features:
                print(f"   {feature}")
            print()

        print("📚 Description:")
        desc = metadata.get('description', '')
        # Wrap description at 60 characters
        words = desc.split()
        line = "   "
        for word in words:
            if len(line) + len(word) + 1 > 60:
                print(line)
                line = "   " + word
            else:
                line += " " + word if line != "   " else word
        if line.strip():
            print(line)
        print()

        print("=" * 60)

    return 0

def display_changelog():
    """Display version changelog."""
    print("=" * 60)
    print("📋 PROJECT GUARDIAN SKILL - CHANGELOG")
    print("=" * 60)
    print()

    changelog = [
        {
            'version': '1.4.0',
            'date': '2026-02-26',
            'changes': [
                'Added intelligent trigger detection with multi-language support',
                'Implemented smart caching system (40% performance improvement)',
                'Added Git hooks automation for auto-updates',
                'Added cache statistics and monitoring tools',
                'Improved context awareness and intent classification'
            ]
        },
        {
            'version': '1.3.1',
            'date': '2026-02-27',
            'changes': [
                'Added comprehensive test suite (40 tests)',
                'Implemented input validation with JSON Schema',
                'Added file locking mechanism for concurrent access',
                'Fixed hardcoded paths in scripts',
                'Production-ready optimizations and bug fixes'
            ]
        },
        {
            'version': '1.3.0',
            'date': '2026-02-25',
            'changes': [
                'Added query pattern learning and analysis',
                'Implemented optional semantic search with AI embeddings',
                'Added pattern analyzer with recommendations',
                'Added query logger for usage tracking'
            ]
        },
        {
            'version': '1.2.0',
            'date': '2026-02-25',
            'changes': [
                'Added version tracking with Git integration',
                'Implemented health monitoring system',
                'Added knowledge base changelog generation',
                'Bug-commit association tracking'
            ]
        },
        {
            'version': '1.1.0',
            'date': '2026-02-25',
            'changes': [
                'Added quick recording without JSON files',
                'Implemented incremental update system',
                'Added context-aware loading for token optimization',
                'Improved module detection and loading'
            ]
        },
        {
            'version': '1.0.0',
            'date': '2026-02-24',
            'changes': [
                'Initial release',
                'Zero-configuration project scanning',
                'Bug/requirement/decision tracking',
                'Architecture decision records (ADR)',
                'Similarity search for issues'
            ]
        }
    ]

    for entry in changelog:
        print(f"## v{entry['version']} ({entry['date']})")
        print()
        for change in entry['changes']:
            print(f"  • {change}")
        print()

    print("=" * 60)

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Display Project Guardian Skill version information'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--changelog',
        action='store_true',
        help='Display version changelog'
    )
    parser.add_argument(
        '--check-update',
        action='store_true',
        help='Check for available updates (requires internet)'
    )

    args = parser.parse_args()

    if args.changelog:
        display_changelog()
        return 0

    if args.check_update:
        print("🔍 Checking for updates...")
        print("ℹ️  Update check not yet implemented")
        print("   Please check: https://github.com/taokoplay/project-guardian-skill")
        return 0

    return display_version_info(args.format)

if __name__ == '__main__':
    sys.exit(main())
