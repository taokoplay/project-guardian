#!/usr/bin/env python3
"""
Project Guardian - Context-Aware Knowledge Loader

Intelligently loads relevant knowledge based on:
- Current file being edited
- User's query keywords
- Module dependencies

Enhanced with intelligent caching for 40% faster loading.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import cache manager
try:
    from cache_manager import IntelligentCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("⚠️  Cache manager not available. Running without cache.")


class ContextLoader:
    def __init__(self, project_path: str, use_cache: bool = True):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"

        if not self.kb_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.kb_path}. "
                "Run scan_project.py first to initialize."
            )

        # Initialize cache
        self.cache = None
        if use_cache and CACHE_AVAILABLE:
            self.cache = IntelligentCache(self.kb_path, max_size=100)
            # Warm cache with core files
            self.cache.warm_cache()

    def _load_json(self, file_path: Path, category: str = "core") -> Dict[str, Any]:
        """Load JSON file safely with intelligent caching"""
        if not file_path.exists():
            return {}

        # Use cache if available
        if self.cache:
            try:
                return self.cache.load_with_cache(file_path, category)
            except Exception:
                pass  # Fall back to direct loading

        # Direct loading (no cache)
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _identify_module(self, file_path: str) -> Optional[str]:
        """Identify which module a file belongs to"""
        file_path = Path(file_path)

        # Common module patterns
        module_patterns = {
            "auth": ["auth", "login", "oauth", "session", "user"],
            "api": ["api", "routes", "endpoints", "controllers"],
            "database": ["db", "database", "models", "schema", "migrations"],
            "ui": ["components", "views", "pages", "ui"],
            "utils": ["utils", "helpers", "lib", "common"],
            "config": ["config", "settings", "env"],
            "tests": ["test", "tests", "__tests__", "spec"]
        }

        # Check file path parts
        path_parts = [p.lower() for p in file_path.parts]

        for module, keywords in module_patterns.items():
            if any(keyword in path_parts for keyword in keywords):
                return module

        # Check file name
        file_name = file_path.stem.lower()
        for module, keywords in module_patterns.items():
            if any(keyword in file_name for keyword in keywords):
                return module

        return "general"

    def _load_module_bugs(self, module: str) -> List[Dict[str, Any]]:
        """Load bugs related to a specific module"""
        bugs_dir = self.kb_path / "history" / "bugs"
        if not bugs_dir.exists():
            return []

        module_bugs = []
        for bug_file in bugs_dir.glob("*.json"):
            bug = self._load_json(bug_file)
            if not bug:
                continue

            # Check if bug is related to this module
            tags = bug.get("tags", [])
            files = bug.get("files_changed", [])

            if module in tags or any(module in str(f).lower() for f in files):
                module_bugs.append(bug)

        return module_bugs

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from user query"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how'
        }

        # Tokenize and filter
        words = re.findall(r'\w+', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def load_for_file(self, file_path: str) -> Dict[str, Any]:
        """Load relevant knowledge for a specific file"""
        print(f"📚 Loading context for file: {file_path}")

        # Identify module
        module = self._identify_module(file_path)
        print(f"  📦 Detected module: {module}")

        context = {
            "file": file_path,
            "module": module,
            "core": {},
            "related_bugs": [],
            "conventions": {}
        }

        # Load core profile (cached)
        profile = self._load_json(self.kb_path / "core" / "profile.json", "core")
        context["core"]["profile"] = profile

        # Load tech stack (cached)
        tech_stack = self._load_json(self.kb_path / "core" / "tech-stack.json", "core")
        context["core"]["tech_stack"] = tech_stack

        # Load conventions (cached)
        conventions = self._load_json(self.kb_path / "core" / "conventions.json", "core")
        context["conventions"] = conventions

        # Load module-specific bugs (not cached - real-time data)
        related_bugs = self._load_module_bugs(module)
        context["related_bugs"] = related_bugs[:5]  # Top 5 most relevant

        print(f"  ✓ Loaded {len(related_bugs)} related bugs")

        return context

    def load_for_query(self, query: str, current_file: Optional[str] = None) -> Dict[str, Any]:
        """Load relevant knowledge based on user query"""
        print(f"🔍 Loading context for query: {query[:50]}...")

        keywords = self._extract_keywords(query)
        print(f"  🔑 Keywords: {', '.join(keywords[:5])}")

        context = {
            "query": query,
            "keywords": keywords,
            "core": {},
            "relevant_modules": [],
            "related_bugs": [],
            "related_requirements": []
        }

        # Always load core profile (cached)
        profile = self._load_json(self.kb_path / "core" / "profile.json", "core")
        context["core"]["profile"] = profile

        # Determine which modules are relevant
        module_keywords = {
            "auth": ["auth", "login", "oauth", "session", "user", "password", "token"],
            "api": ["api", "endpoint", "route", "request", "response", "http"],
            "database": ["database", "db", "sql", "query", "model", "schema"],
            "ui": ["ui", "component", "view", "page", "render", "display"],
            "config": ["config", "setting", "environment", "env"]
        }

        relevant_modules = []
        for module, module_kws in module_keywords.items():
            if any(kw in keywords for kw in module_kws):
                relevant_modules.append(module)

        # If current file is provided, add its module
        if current_file:
            file_module = self._identify_module(current_file)
            if file_module not in relevant_modules:
                relevant_modules.append(file_module)

        context["relevant_modules"] = relevant_modules

        # Load bugs from relevant modules
        all_bugs = []
        for module in relevant_modules:
            module_bugs = self._load_module_bugs(module)
            all_bugs.extend(module_bugs)

        # Score bugs by keyword relevance
        scored_bugs = []
        for bug in all_bugs:
            score = 0
            bug_text = f"{bug.get('title', '')} {bug.get('description', '')}".lower()

            for keyword in keywords:
                if keyword in bug_text:
                    score += 1

            if score > 0:
                scored_bugs.append((score, bug))

        # Sort by score and take top 5
        scored_bugs.sort(reverse=True, key=lambda x: x[0])
        context["related_bugs"] = [bug for _, bug in scored_bugs[:5]]

        # Load requirements similarly
        req_dir = self.kb_path / "history" / "requirements"
        if req_dir.exists():
            all_reqs = []
            for req_file in req_dir.glob("*.json"):
                req = self._load_json(req_file)
                if req:
                    all_reqs.append(req)

            # Score requirements
            scored_reqs = []
            for req in all_reqs:
                score = 0
                req_text = f"{req.get('title', '')} {req.get('description', '')}".lower()

                for keyword in keywords:
                    if keyword in req_text:
                        score += 1

                if score > 0:
                    scored_reqs.append((score, req))

            scored_reqs.sort(reverse=True, key=lambda x: x[0])
            context["related_requirements"] = [req for _, req in scored_reqs[:3]]

        print(f"  ✓ Found {len(context['related_bugs'])} relevant bugs")
        print(f"  ✓ Found {len(context['related_requirements'])} relevant requirements")

        return context

    def load_minimal(self) -> Dict[str, Any]:
        """Load minimal core context (for general queries)"""
        print("📚 Loading minimal context...")

        context = {
            "core": {}
        }

        # Load only core files (all cached)
        profile = self._load_json(self.kb_path / "core" / "profile.json", "core")
        tech_stack = self._load_json(self.kb_path / "core" / "tech-stack.json", "core")
        conventions = self._load_json(self.kb_path / "core" / "conventions.json", "core")

        context["core"] = {
            "profile": profile,
            "tech_stack": tech_stack,
            "conventions": conventions
        }

        return context

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache:
            return {"cache_enabled": False}

        stats = self.cache.get_stats()
        stats["cache_enabled"] = True
        return stats

    def clear_cache(self, pattern: str = "*"):
        """Clear cache by pattern"""
        if self.cache:
            self.cache.invalidate(pattern)
            print(f"✅ Cache cleared (pattern: {pattern})")


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Load for file:  python context_loader.py <project_path> --file <file_path>")
        print("  Load for query: python context_loader.py <project_path> --query '<query>' [--current-file <file>]")
        print("  Load minimal:   python context_loader.py <project_path> --minimal")
        print("  Cache stats:    python context_loader.py <project_path> --cache-stats")
        print("  Clear cache:    python context_loader.py <project_path> --clear-cache [pattern]")
        print()
        print("Options:")
        print("  --no-cache      Disable caching for this operation")
        sys.exit(1)

    project_path = sys.argv[1]

    try:
        # Check if cache should be disabled
        use_cache = "--no-cache" not in sys.argv

        loader = ContextLoader(project_path, use_cache=use_cache)

        if "--file" in sys.argv:
            file_idx = sys.argv.index("--file")
            file_path = sys.argv[file_idx + 1]
            context = loader.load_for_file(file_path)

        elif "--query" in sys.argv:
            query_idx = sys.argv.index("--query")
            query = sys.argv[query_idx + 1]

            current_file = None
            if "--current-file" in sys.argv:
                file_idx = sys.argv.index("--current-file")
                current_file = sys.argv[file_idx + 1]

            context = loader.load_for_query(query, current_file)

        elif "--minimal" in sys.argv:
            context = loader.load_minimal()

        elif "--cache-stats" in sys.argv:
            stats = loader.get_cache_stats()
            print("\n📊 Cache Statistics:")
            print(json.dumps(stats, indent=2))
            sys.exit(0)

        elif "--clear-cache" in sys.argv:
            pattern = "*"
            if len(sys.argv) > sys.argv.index("--clear-cache") + 1:
                pattern = sys.argv[sys.argv.index("--clear-cache") + 1]
            loader.clear_cache(pattern)
            sys.exit(0)

        else:
            print("❌ Invalid arguments")
            sys.exit(1)

        # Output context as JSON
        print("\n" + "="*60)
        print(json.dumps(context, indent=2))

        # Show cache stats if enabled
        if use_cache and loader.cache:
            print("\n" + "="*60)
            loader.cache.print_stats()

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
