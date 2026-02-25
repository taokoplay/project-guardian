#!/usr/bin/env python3
"""
Project Guardian - Knowledge Base Updater

Incrementally updates the knowledge base with new bugs, requirements, and decisions.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class KnowledgeUpdater:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.kb_path = self.project_path / ".project-ai"

        if not self.kb_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.kb_path}. "
                "Run scan_project.py first to initialize."
            )

    def record_bug(self, bug_data: Dict[str, Any]) -> str:
        """Record a bug in the knowledge base"""
        bug_id = self._generate_id("BUG")

        bug_record = {
            "id": bug_id,
            "recorded_at": datetime.now().isoformat(),
            "title": bug_data.get("title", "Untitled Bug"),
            "description": bug_data.get("description", ""),
            "root_cause": bug_data.get("root_cause", ""),
            "solution": bug_data.get("solution", ""),
            "files_changed": bug_data.get("files_changed", []),
            "tags": bug_data.get("tags", []),
            "severity": bug_data.get("severity", "medium"),
            "status": "resolved"
        }

        # Save to history
        bug_file = self.kb_path / "history" / "bugs" / f"{bug_id}.json"
        self._write_json(bug_file, bug_record)

        # Update index
        self._update_bug_index(bug_record)

        print(f"✅ Bug recorded: {bug_id} - {bug_record['title']}")
        return bug_id

    def record_requirement(self, req_data: Dict[str, Any]) -> str:
        """Record a requirement in the knowledge base"""
        req_id = self._generate_id("REQ")

        req_record = {
            "id": req_id,
            "recorded_at": datetime.now().isoformat(),
            "title": req_data.get("title", "Untitled Requirement"),
            "description": req_data.get("description", ""),
            "status": req_data.get("status", "planned"),
            "priority": req_data.get("priority", "medium"),
            "related_modules": req_data.get("related_modules", []),
            "acceptance_criteria": req_data.get("acceptance_criteria", []),
            "tags": req_data.get("tags", [])
        }

        # Save to history
        req_file = self.kb_path / "history" / "requirements" / f"{req_id}.json"
        self._write_json(req_file, req_record)

        print(f"✅ Requirement recorded: {req_id} - {req_record['title']}")
        return req_id

    def record_decision(self, decision_data: Dict[str, Any]) -> str:
        """Record an architecture decision"""
        decision_id = self._generate_id("DEC")

        decision_record = {
            "id": decision_id,
            "recorded_at": datetime.now().isoformat(),
            "title": decision_data.get("title", "Untitled Decision"),
            "context": decision_data.get("context", ""),
            "decision": decision_data.get("decision", ""),
            "rationale": decision_data.get("rationale", ""),
            "consequences": decision_data.get("consequences", []),
            "alternatives": decision_data.get("alternatives", []),
            "tags": decision_data.get("tags", [])
        }

        # Save to history
        decision_file = self.kb_path / "history" / "decisions" / f"{decision_id}.json"
        self._write_json(decision_file, decision_record)

        print(f"✅ Decision recorded: {decision_id} - {decision_record['title']}")
        return decision_id

    def update_module_info(self, module_name: str, info: Dict[str, Any]) -> None:
        """Update information about a specific module"""
        modules_file = self.kb_path / "indexed" / "modules.json"

        modules = self._read_json(modules_file) or {}
        modules[module_name] = {
            **modules.get(module_name, {}),
            **info,
            "last_updated": datetime.now().isoformat()
        }

        self._write_json(modules_file, modules)
        print(f"✅ Module info updated: {module_name}")

    def update_architecture(self, arch_data: Dict[str, Any]) -> None:
        """Update architecture information"""
        arch_file = self.kb_path / "indexed" / "architecture.json"

        current_arch = self._read_json(arch_file) or {}
        updated_arch = {
            **current_arch,
            **arch_data,
            "last_updated": datetime.now().isoformat()
        }

        self._write_json(arch_file, updated_arch)
        print(f"✅ Architecture info updated")

    def _update_bug_index(self, bug_record: Dict[str, Any]) -> None:
        """Update the bug search index"""
        index_file = self.kb_path / "history" / "bugs" / "_index.json"

        index = self._read_json(index_file) or {"bugs": [], "tags": {}}

        # Add to bug list
        index["bugs"].append({
            "id": bug_record["id"],
            "title": bug_record["title"],
            "tags": bug_record["tags"],
            "recorded_at": bug_record["recorded_at"]
        })

        # Update tag index
        for tag in bug_record["tags"]:
            if tag not in index["tags"]:
                index["tags"][tag] = []
            index["tags"][tag].append(bug_record["id"])

        self._write_json(index_file, index)

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(os.urandom(8)).hexdigest()[:4]
        return f"{prefix}-{timestamp}-{random_suffix}"

    def _read_json(self, path: Path) -> Optional[Dict]:
        try:
            return json.loads(path.read_text())
        except:
            return None

    def _write_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))


def main():
    if len(sys.argv) < 3:
        print("Usage: python update_knowledge.py <project_path> --type <bug|requirement|decision> --data <json_file>")
        print("   or: python update_knowledge.py <project_path> --module <name> --info <json_file>")
        sys.exit(1)

    project_path = sys.argv[1]
    updater = KnowledgeUpdater(project_path)

    # Parse arguments
    args = sys.argv[2:]
    if "--type" in args:
        idx = args.index("--type")
        record_type = args[idx + 1]
        data_idx = args.index("--data")
        data_file = args[data_idx + 1]

        with open(data_file, 'r') as f:
            data = json.load(f)

        if record_type == "bug":
            updater.record_bug(data)
        elif record_type == "requirement":
            updater.record_requirement(data)
        elif record_type == "decision":
            updater.record_decision(data)
        else:
            print(f"❌ Unknown type: {record_type}")
            sys.exit(1)

    elif "--module" in args:
        idx = args.index("--module")
        module_name = args[idx + 1]
        info_idx = args.index("--info")
        info_file = args[info_idx + 1]

        with open(info_file, 'r') as f:
            info = json.load(f)

        updater.update_module_info(module_name, info)

    else:
        print("❌ Invalid arguments")
        sys.exit(1)


if __name__ == "__main__":
    main()
