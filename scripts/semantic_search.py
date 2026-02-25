#!/usr/bin/env python3
"""
Project Guardian - Semantic Search (Optional)

Enhanced search using semantic similarity instead of just keyword matching.
This is an OPTIONAL feature that requires sentence-transformers library.

Installation:
    pip install sentence-transformers

If not installed, the system will fall back to TF-IDF search.
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Check if sentence-transformers is available
try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False
    print("⚠️  sentence-transformers not installed. Semantic search unavailable.")
    print("   Install with: pip install sentence-transformers")


class SemanticSearcher:
    def __init__(self, project_path: str, model_name: str = "all-MiniLM-L6-v2"):
        if not SEMANTIC_SEARCH_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for semantic search. "
                "Install with: pip install sentence-transformers"
            )

        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"

        if not self.kb_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.kb_path}. "
                "Run scan_project.py first to initialize."
            )

        # Load model (lightweight, ~80MB)
        print(f"📦 Loading semantic search model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("✅ Model loaded")

        self.embeddings_file = self.kb_path / "indexed" / "_embeddings.npz"
        self.embeddings_index = self.kb_path / "indexed" / "_embeddings_index.json"

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

    def _load_all_records(self, record_type: str) -> List[Dict[str, Any]]:
        """Load all records of a specific type"""
        records_dir = self.kb_path / "history" / record_type
        if not records_dir.exists():
            return []

        records = []
        for record_file in records_dir.glob("*.json"):
            record = self._load_json(record_file)
            if record:
                records.append(record)

        return records

    def build_embeddings(self):
        """Build and cache embeddings for all records"""
        print("🔨 Building embeddings...")

        # Load all records
        bugs = self._load_all_records("bugs")
        requirements = self._load_all_records("requirements")
        decisions = self._load_all_records("decisions")

        all_records = []
        all_texts = []

        # Process bugs
        for bug in bugs:
            text = f"{bug.get('title', '')} {bug.get('description', '')} {bug.get('root_cause', '')}"
            all_records.append({"type": "bug", "id": bug.get("id"), "record": bug})
            all_texts.append(text)

        # Process requirements
        for req in requirements:
            text = f"{req.get('title', '')} {req.get('description', '')} {req.get('rationale', '')}"
            all_records.append({"type": "requirement", "id": req.get("id"), "record": req})
            all_texts.append(text)

        # Process decisions
        for decision in decisions:
            text = f"{decision.get('title', '')} {decision.get('context', '')} {decision.get('decision', '')}"
            all_records.append({"type": "decision", "id": decision.get("id"), "record": decision})
            all_texts.append(text)

        if not all_texts:
            print("⚠️  No records found to build embeddings")
            return

        print(f"  Processing {len(all_texts)} records...")

        # Generate embeddings
        embeddings = self.model.encode(all_texts, show_progress_bar=True)

        # Save embeddings
        np.savez_compressed(self.embeddings_file, embeddings=embeddings)

        # Save index
        self._save_json(self.embeddings_index, {
            "records": all_records,
            "count": len(all_records),
            "model": self.model.get_sentence_embedding_dimension(),
            "built_at": str(Path(self.embeddings_file).stat().st_mtime)
        })

        print(f"✅ Built embeddings for {len(all_records)} records")

    def _load_embeddings(self) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Load cached embeddings"""
        if not self.embeddings_file.exists():
            raise FileNotFoundError(
                "Embeddings not found. Run with --build first to create embeddings."
            )

        # Load embeddings
        data = np.load(self.embeddings_file)
        embeddings = data["embeddings"]

        # Load index
        index = self._load_json(self.embeddings_index)
        records = index.get("records", [])

        return embeddings, records

    def search(self, query: str, top_k: int = 5, record_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for similar records using semantic similarity"""
        print(f"🔍 Searching for: {query}")

        # Load embeddings
        embeddings, records = self._load_embeddings()

        # Encode query
        query_embedding = self.model.encode([query])[0]

        # Calculate cosine similarity
        similarities = np.dot(embeddings, query_embedding) / (
            np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        # Filter by record type if specified
        if record_type:
            filtered_indices = [i for i, r in enumerate(records) if r["type"] == record_type]
            filtered_similarities = similarities[filtered_indices]
            filtered_records = [records[i] for i in filtered_indices]
        else:
            filtered_similarities = similarities
            filtered_records = records

        # Get top-k results
        top_indices = np.argsort(filtered_similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            record = filtered_records[idx]
            similarity = float(filtered_similarities[idx])

            results.append({
                "type": record["type"],
                "id": record["id"],
                "similarity": similarity,
                "record": record["record"]
            })

        return results


def main():
    if not SEMANTIC_SEARCH_AVAILABLE:
        print("\n❌ Semantic search is not available.")
        print("   Install sentence-transformers: pip install sentence-transformers")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Build embeddings:  python semantic_search.py <project_path> --build")
        print("  Search:            python semantic_search.py <project_path> --search '<query>' [--type bug|requirement|decision] [--top 5]")
        print("  Check status:      python semantic_search.py <project_path> --status")
        sys.exit(1)

    project_path = sys.argv[1]

    try:
        searcher = SemanticSearcher(project_path)

        if "--build" in sys.argv:
            searcher.build_embeddings()

        elif "--search" in sys.argv:
            search_idx = sys.argv.index("--search")
            query = sys.argv[search_idx + 1]

            record_type = None
            if "--type" in sys.argv:
                type_idx = sys.argv.index("--type")
                record_type = sys.argv[type_idx + 1]

            top_k = 5
            if "--top" in sys.argv:
                top_idx = sys.argv.index("--top")
                top_k = int(sys.argv[top_idx + 1])

            results = searcher.search(query, top_k, record_type)

            print(f"\n📊 Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. [{result['type'].upper()}] {result['id']}")
                print(f"   Similarity: {result['similarity']:.3f}")
                print(f"   Title: {result['record'].get('title', 'N/A')}")
                print(f"   Description: {result['record'].get('description', 'N/A')[:100]}...")
                print()

        elif "--status" in sys.argv:
            if searcher.embeddings_file.exists():
                index = searcher._load_json(searcher.embeddings_index)
                print("✅ Semantic search is ready")
                print(f"   Records indexed: {index.get('count', 0)}")
                print(f"   Model dimension: {index.get('model', 'unknown')}")
            else:
                print("⚠️  Embeddings not built yet")
                print("   Run with --build to create embeddings")

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
