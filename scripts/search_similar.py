#!/usr/bin/env python3
"""
Project Guardian - Similarity Search

Search for similar bugs, requirements, or decisions in the knowledge base.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter
import re


class SimilaritySearcher:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"

        if not self.kb_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.kb_path}. "
                "Run scan_project.py first to initialize."
            )

    def search_bugs(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar bugs"""
        bugs_dir = self.kb_path / "history" / "bugs"

        if not bugs_dir.exists():
            return []

        # Load all bugs
        bugs = []
        for bug_file in bugs_dir.glob("*.json"):
            if bug_file.name == "_index.json":
                continue

            try:
                bug = json.loads(bug_file.read_text())
                bugs.append(bug)
            except:
                continue

        # Calculate similarity scores
        scored_bugs = []
        for bug in bugs:
            score = self._calculate_similarity(query, bug)
            if score > 0:
                scored_bugs.append((score, bug))

        # Sort by score and return top k
        scored_bugs.sort(reverse=True, key=lambda x: x[0])
        return [bug for score, bug in scored_bugs[:top_k]]

    def search_requirements(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar requirements"""
        reqs_dir = self.kb_path / "history" / "requirements"

        if not reqs_dir.exists():
            return []

        # Load all requirements
        requirements = []
        for req_file in reqs_dir.glob("*.json"):
            try:
                req = json.loads(req_file.read_text())
                requirements.append(req)
            except:
                continue

        # Calculate similarity scores
        scored_reqs = []
        for req in requirements:
            score = self._calculate_similarity(query, req)
            if score > 0:
                scored_reqs.append((score, req))

        # Sort by score and return top k
        scored_reqs.sort(reverse=True, key=lambda x: x[0])
        return [req for score, req in scored_reqs[:top_k]]

    def search_by_tags(self, tags: List[str], record_type: str = "bug") -> List[Dict[str, Any]]:
        """Search by tags"""
        if record_type == "bug":
            index_file = self.kb_path / "history" / "bugs" / "_index.json"
            records_dir = self.kb_path / "history" / "bugs"
        elif record_type == "requirement":
            records_dir = self.kb_path / "history" / "requirements"
        else:
            return []

        # Try to use index first
        if record_type == "bug" and index_file.exists():
            try:
                index = json.loads(index_file.read_text())
                tag_index = index.get("tags", {})

                # Find bugs matching any of the tags
                matching_ids = set()
                for tag in tags:
                    if tag in tag_index:
                        matching_ids.update(tag_index[tag])

                # Load matching bugs
                results = []
                for bug_id in matching_ids:
                    bug_file = records_dir / f"{bug_id}.json"
                    if bug_file.exists():
                        results.append(json.loads(bug_file.read_text()))

                return results
            except:
                pass

        # Fallback: scan all files
        results = []
        for record_file in records_dir.glob("*.json"):
            if record_file.name == "_index.json":
                continue

            try:
                record = json.loads(record_file.read_text())
                record_tags = record.get("tags", [])

                if any(tag in record_tags for tag in tags):
                    results.append(record)
            except:
                continue

        return results

    def _calculate_similarity(self, query: str, record: Dict[str, Any]) -> float:
        """Calculate similarity score between query and record"""
        # Extract text from record
        text_fields = []
        text_fields.append(record.get("title", ""))
        text_fields.append(record.get("description", ""))
        text_fields.append(record.get("root_cause", ""))
        text_fields.append(record.get("solution", ""))
        text_fields.extend(record.get("tags", []))

        record_text = " ".join(text_fields).lower()
        query_lower = query.lower()

        # Tokenize
        query_tokens = self._tokenize(query_lower)
        record_tokens = self._tokenize(record_text)

        if not query_tokens or not record_tokens:
            return 0.0

        # Calculate TF-IDF-like score
        query_counter = Counter(query_tokens)
        record_counter = Counter(record_tokens)

        # Intersection of tokens
        common_tokens = set(query_tokens) & set(record_tokens)

        if not common_tokens:
            return 0.0

        # Calculate score
        score = 0.0
        for token in common_tokens:
            # Weight by frequency in query
            query_weight = query_counter[token] / len(query_tokens)
            # Inverse document frequency (simplified)
            idf = 1.0 / (1.0 + record_counter[token])
            score += query_weight * idf

        # Boost for exact phrase matches
        if query_lower in record_text:
            score *= 2.0

        # Boost for title matches
        if query_lower in record.get("title", "").lower():
            score *= 1.5

        return score

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                     'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'should', 'could', 'may', 'might', 'must', 'can'}

        return [token for token in tokens if token not in stop_words and len(token) > 2]


def main():
    if len(sys.argv) < 3:
        print("Usage: python search_similar.py <project_path> <query>")
        print("   or: python search_similar.py <project_path> --tags <tag1,tag2,...>")
        sys.exit(1)

    project_path = sys.argv[1]
    searcher = SimilaritySearcher(project_path)

    if "--tags" in sys.argv:
        idx = sys.argv.index("--tags")
        tags = sys.argv[idx + 1].split(",")

        print(f"🔍 Searching for bugs with tags: {', '.join(tags)}\n")
        results = searcher.search_by_tags(tags, record_type="bug")

    else:
        query = " ".join(sys.argv[2:])
        print(f"🔍 Searching for: {query}\n")

        # Search bugs
        bug_results = searcher.search_bugs(query, top_k=3)
        results = bug_results

    # Display results
    if not results:
        print("❌ No similar issues found")
        return

    print(f"✅ Found {len(results)} similar issue(s):\n")
    print("="*60)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title', 'Untitled')}")
        print(f"   ID: {result.get('id', 'N/A')}")
        print(f"   Date: {result.get('recorded_at', 'N/A')[:10]}")

        if 'root_cause' in result and result['root_cause']:
            print(f"   Root Cause: {result['root_cause'][:100]}...")

        if 'solution' in result and result['solution']:
            print(f"   Solution: {result['solution'][:100]}...")

        if 'tags' in result and result['tags']:
            print(f"   Tags: {', '.join(result['tags'])}")

        print("-"*60)


if __name__ == "__main__":
    main()
