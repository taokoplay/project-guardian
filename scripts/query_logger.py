#!/usr/bin/env python3
"""
Project Guardian - Query Logger

Records user queries to learn usage patterns and identify knowledge gaps.
Helps optimize knowledge base structure based on actual usage.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class QueryLogger:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"

        if not self.kb_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.kb_path}. "
                "Run scan_project.py first to initialize."
            )

        self.queries_dir = self.kb_path / "history" / "queries"
        self.queries_dir.mkdir(parents=True, exist_ok=True)

        self.queries_index = self.kb_path / "indexed" / "queries-index.json"

    def _generate_query_id(self) -> str:
        """Generate unique query ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:4]
        return f"QUERY-{timestamp}-{random_suffix}"

    def _load_json(self, file_path: Path) -> Any:
        """Load JSON file safely"""
        if not file_path.exists():
            return {}
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_json(self, file_path: Path, data: Any):
        """Save JSON file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def log_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Log a user query"""
        query_id = self._generate_query_id()

        query_record = {
            "id": query_id,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "context": context or {},
            "results": {
                "loaded_modules": [],
                "found_bugs": [],
                "found_requirements": [],
                "found_decisions": []
            },
            "metadata": {
                "query_length": len(query),
                "has_context": bool(context)
            }
        }

        # Save query record
        query_file = self.queries_dir / f"{query_id}.json"
        self._save_json(query_file, query_record)

        # Update index
        self._update_index(query_record)

        return query_id

    def update_query_results(self, query_id: str, results: Dict[str, Any]):
        """Update query with results after execution"""
        query_file = self.queries_dir / f"{query_id}.json"
        if not query_file.exists():
            print(f"❌ Query {query_id} not found")
            return

        query_record = self._load_json(query_file)
        query_record["results"] = results
        query_record["completed_at"] = datetime.now().isoformat()

        self._save_json(query_file, query_record)

        # Update index
        self._update_index(query_record)

    def _update_index(self, query_record: Dict[str, Any]):
        """Update queries index for fast lookup"""
        index = self._load_json(self.queries_index)

        if "queries" not in index:
            index["queries"] = []

        # Add or update query in index
        query_summary = {
            "id": query_record["id"],
            "timestamp": query_record["timestamp"],
            "query": query_record["query"][:100],  # First 100 chars
            "has_results": bool(query_record.get("results", {}).get("found_bugs") or
                               query_record.get("results", {}).get("found_requirements"))
        }

        # Remove old entry if exists
        index["queries"] = [q for q in index["queries"] if q["id"] != query_record["id"]]

        # Add new entry
        index["queries"].append(query_summary)

        # Keep only last 1000 queries in index
        if len(index["queries"]) > 1000:
            index["queries"] = index["queries"][-1000:]

        self._save_json(self.queries_index, index)

    def get_recent_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent queries"""
        query_files = sorted(self.queries_dir.glob("QUERY-*.json"), reverse=True)
        queries = []

        for query_file in query_files[:limit]:
            query = self._load_json(query_file)
            if query:
                queries.append(query)

        return queries

    def search_queries(self, keyword: str) -> List[Dict[str, Any]]:
        """Search queries by keyword"""
        query_files = self.queries_dir.glob("QUERY-*.json")
        matching_queries = []

        keyword_lower = keyword.lower()

        for query_file in query_files:
            query = self._load_json(query_file)
            if not query:
                continue

            query_text = query.get("query", "").lower()
            if keyword_lower in query_text:
                matching_queries.append(query)

        # Sort by timestamp (most recent first)
        matching_queries.sort(key=lambda q: q.get("timestamp", ""), reverse=True)

        return matching_queries

    def get_query_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        query_files = list(self.queries_dir.glob("QUERY-*.json"))

        total_queries = len(query_files)
        queries_with_results = 0
        queries_without_results = 0

        for query_file in query_files:
            query = self._load_json(query_file)
            if not query:
                continue

            results = query.get("results", {})
            has_results = bool(
                results.get("found_bugs") or
                results.get("found_requirements") or
                results.get("found_decisions")
            )

            if has_results:
                queries_with_results += 1
            else:
                queries_without_results += 1

        return {
            "total_queries": total_queries,
            "queries_with_results": queries_with_results,
            "queries_without_results": queries_without_results,
            "success_rate": (queries_with_results / total_queries * 100) if total_queries > 0 else 0
        }


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Log query:         python query_logger.py <project_path> --log '<query>' [--context <context.json>]")
        print("  Update results:    python query_logger.py <project_path> --update <query_id> --results <results.json>")
        print("  Recent queries:    python query_logger.py <project_path> --recent [limit]")
        print("  Search queries:    python query_logger.py <project_path> --search '<keyword>'")
        print("  Query stats:       python query_logger.py <project_path> --stats")
        sys.exit(1)

    project_path = sys.argv[1]

    try:
        logger = QueryLogger(project_path)

        if "--log" in sys.argv:
            log_idx = sys.argv.index("--log")
            query = sys.argv[log_idx + 1]

            context = None
            if "--context" in sys.argv:
                context_idx = sys.argv.index("--context")
                context_file = sys.argv[context_idx + 1]
                with open(context_file, 'r') as f:
                    context = json.load(f)

            query_id = logger.log_query(query, context)
            print(f"✅ Query logged: {query_id}")

        elif "--update" in sys.argv:
            update_idx = sys.argv.index("--update")
            query_id = sys.argv[update_idx + 1]

            results_idx = sys.argv.index("--results")
            results_file = sys.argv[results_idx + 1]

            with open(results_file, 'r') as f:
                results = json.load(f)

            logger.update_query_results(query_id, results)
            print(f"✅ Query {query_id} updated with results")

        elif "--recent" in sys.argv:
            limit = 20
            if len(sys.argv) > sys.argv.index("--recent") + 1:
                try:
                    limit = int(sys.argv[sys.argv.index("--recent") + 1])
                except ValueError:
                    pass

            queries = logger.get_recent_queries(limit)
            print(json.dumps(queries, indent=2, ensure_ascii=False))

        elif "--search" in sys.argv:
            search_idx = sys.argv.index("--search")
            keyword = sys.argv[search_idx + 1]

            queries = logger.search_queries(keyword)
            print(f"Found {len(queries)} matching queries:")
            print(json.dumps(queries, indent=2, ensure_ascii=False))

        elif "--stats" in sys.argv:
            stats = logger.get_query_stats()
            print("📊 Query Statistics:")
            print(f"  Total queries: {stats['total_queries']}")
            print(f"  Queries with results: {stats['queries_with_results']}")
            print(f"  Queries without results: {stats['queries_without_results']}")
            print(f"  Success rate: {stats['success_rate']:.1f}%")

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
