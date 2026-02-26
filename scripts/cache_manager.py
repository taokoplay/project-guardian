#!/usr/bin/env python3
"""
Project Guardian - Intelligent Cache Manager

Smart caching system with:
- Content-based cache invalidation (MD5 hash)
- Adaptive TTL based on file change frequency
- Memory-efficient LRU eviction
- Automatic cache warming
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict


class IntelligentCache:
    def __init__(self, kb_path: Path, max_size: int = 100):
        self.kb_path = kb_path
        self.max_size = max_size

        # LRU cache: {file_path: (data, timestamp, content_hash, access_count)}
        self.cache: OrderedDict[str, Tuple[Any, float, str, int]] = OrderedDict()

        # File change tracking: {file_path: [change_timestamps]}
        self.change_history: Dict[str, list] = {}

        # Adaptive TTL based on change frequency
        self.base_ttl = {
            "core": 3600,        # 1 hour (rarely changes)
            "indexed": 1800,     # 30 minutes (occasionally changes)
            "history": 0,        # No cache (real-time data)
        }

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "evictions": 0
        }

    def _calculate_content_hash(self, file_path: Path) -> str:
        """Calculate file content hash for change detection"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _calculate_adaptive_ttl(self, file_path: str, category: str) -> float:
        """Calculate adaptive TTL based on file change frequency"""
        base = self.base_ttl.get(category, 0)

        if base == 0:
            return 0  # No cache for history files

        # Get change history
        changes = self.change_history.get(file_path, [])

        if len(changes) < 2:
            return base  # Not enough data, use base TTL

        # Calculate average time between changes
        time_diffs = [changes[i] - changes[i-1] for i in range(1, len(changes))]
        avg_change_interval = sum(time_diffs) / len(time_diffs)

        # Adaptive TTL: 50% of average change interval, capped at base TTL
        adaptive_ttl = min(avg_change_interval * 0.5, base)

        return max(adaptive_ttl, 60)  # Minimum 1 minute

    def _record_change(self, file_path: str):
        """Record file change for adaptive TTL calculation"""
        if file_path not in self.change_history:
            self.change_history[file_path] = []

        self.change_history[file_path].append(time.time())

        # Keep only last 10 changes
        if len(self.change_history[file_path]) > 10:
            self.change_history[file_path] = self.change_history[file_path][-10:]

    def _evict_lru(self):
        """Evict least recently used item"""
        if len(self.cache) >= self.max_size:
            # Remove oldest item (first in OrderedDict)
            evicted_key = next(iter(self.cache))
            del self.cache[evicted_key]
            self.stats["evictions"] += 1

    def get(self, file_path: Path, category: str = "core") -> Optional[Any]:
        """Get from cache with intelligent validation"""
        file_str = str(file_path)

        if file_str not in self.cache:
            self.stats["misses"] += 1
            return None

        data, timestamp, cached_hash, access_count = self.cache[file_str]

        # Check if file still exists
        if not file_path.exists():
            del self.cache[file_str]
            self.stats["invalidations"] += 1
            return None

        # Content-based validation: check if file changed
        current_hash = self._calculate_content_hash(file_path)
        if current_hash != cached_hash:
            # File changed, invalidate cache
            del self.cache[file_str]
            self.stats["invalidations"] += 1
            self._record_change(file_str)
            return None

        # TTL-based validation
        ttl = self._calculate_adaptive_ttl(file_str, category)
        if ttl > 0 and time.time() - timestamp > ttl:
            # TTL expired
            del self.cache[file_str]
            self.stats["invalidations"] += 1
            return None

        # Cache hit! Move to end (most recently used)
        self.cache.move_to_end(file_str)

        # Update access count
        self.cache[file_str] = (data, timestamp, cached_hash, access_count + 1)

        self.stats["hits"] += 1
        return data

    def set(self, file_path: Path, data: Any, category: str = "core"):
        """Set cache with content hash"""
        file_str = str(file_path)

        # Evict if necessary
        self._evict_lru()

        # Calculate content hash
        content_hash = self._calculate_content_hash(file_path)

        # Store in cache
        self.cache[file_str] = (data, time.time(), content_hash, 1)

        # Move to end (most recently used)
        self.cache.move_to_end(file_str)

    def invalidate(self, pattern: str = "*"):
        """Invalidate cache by pattern"""
        if pattern == "*":
            count = len(self.cache)
            self.cache.clear()
            self.stats["invalidations"] += count
        else:
            keys_to_remove = [k for k in self.cache if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
                self.stats["invalidations"] += 1

    def load_with_cache(self, file_path: Path, category: str = "core") -> Any:
        """Load file with intelligent caching"""
        # Try cache first
        cached = self.get(file_path, category)
        if cached is not None:
            return cached

        # Cache miss, load from file
        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Store in cache (only if category allows caching)
            if self.base_ttl.get(category, 0) > 0:
                self.set(file_path, data, category)

            return data
        except Exception as e:
            print(f"⚠️  Error loading {file_path}: {e}")
            return {}

    def warm_cache(self):
        """Pre-load frequently accessed files"""
        print("🔥 Warming cache...")

        # Pre-load core files
        core_files = [
            "profile.json",
            "tech-stack.json",
            "conventions.json"
        ]

        for file in core_files:
            file_path = self.kb_path / "core" / file
            if file_path.exists():
                self.load_with_cache(file_path, "core")

        print(f"✅ Cache warmed with {len(self.cache)} files")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "invalidations": self.stats["invalidations"],
            "evictions": self.stats["evictions"],
            "total_requests": total_requests
        }

    def print_stats(self):
        """Print cache statistics"""
        stats = self.get_stats()

        print("\n📊 Cache Statistics:")
        print(f"  Size: {stats['size']}/{stats['max_size']}")
        print(f"  Hit Rate: {stats['hit_rate']}")
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Invalidations: {stats['invalidations']}")
        print(f"  Evictions: {stats['evictions']}")
        print(f"  Total Requests: {stats['total_requests']}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Warm cache:    python cache_manager.py <project_path> --warm")
        print("  Get stats:     python cache_manager.py <project_path> --stats")
        print("  Clear cache:   python cache_manager.py <project_path> --clear")
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()
    kb_path = project_path / ".project-ai"

    if not kb_path.exists():
        print(f"❌ Knowledge base not found at {kb_path}")
        sys.exit(1)

    cache = IntelligentCache(kb_path)

    if "--warm" in sys.argv:
        cache.warm_cache()

    elif "--stats" in sys.argv:
        cache.print_stats()

    elif "--clear" in sys.argv:
        cache.invalidate("*")
        print("✅ Cache cleared")

    else:
        print("❌ Invalid arguments")
        sys.exit(1)


if __name__ == "__main__":
    main()
