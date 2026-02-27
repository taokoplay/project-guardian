"""
pytest 配置文件
提供测试 fixtures 和配置
"""
import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def tmp_project_root(tmp_path):
    """创建临时项目根目录"""
    return tmp_path


@pytest.fixture
def tmp_knowledge_base(tmp_path):
    """创建临时知识库结构"""
    kb_path = tmp_path / ".project-ai"
    kb_path.mkdir()
    
    # 创建核心目录
    (kb_path / "core").mkdir()
    (kb_path / "indexed").mkdir()
    (kb_path / "history").mkdir()
    
    # 创建空的索引文件
    (kb_path / "indexed" / "bugs.json").write_text("[]")
    (kb_path / "indexed" / "requirements.json").write_text("[]")
    (kb_path / "indexed" / "decisions.json").write_text("[]")
    (kb_path / "indexed" / "bug-index.json").write_text("{}")
    
    return kb_path


@pytest.fixture
def sample_bug() -> Dict[str, Any]:
    """创建示例 bug 数据"""
    return {
        "id": "BUG-20260226150000-a1b2",
        "title": "Memory leak in parser",
        "description": "Parser leaks memory when processing large files",
        "severity": "high",
        "status": "open",
        "tags": ["parser", "memory", "performance"],
        "timestamp": "2026-02-26T15:00:00",
        "file_path": "src/parser.py",
        "line_number": 42
    }


@pytest.fixture
def sample_requirement() -> Dict[str, Any]:
    """创建示例需求数据"""
    return {
        "id": "REQ-20260226150000-c3d4",
        "title": "Add input validation",
        "description": "Validate all user inputs before processing",
        "priority": "high",
        "status": "planned",
        "tags": ["validation", "security"],
        "timestamp": "2026-02-26T15:00:00"
    }


@pytest.fixture
def sample_decision() -> Dict[str, Any]:
    """创建示例架构决策数据"""
    return {
        "id": "DEC-20260226150000-e5f6",
        "title": "Use JSON for configuration",
        "context": "Need a human-readable configuration format",
        "decision": "Use JSON instead of binary format",
        "rationale": "JSON is widely supported and easy to edit",
        "consequences": "Slightly larger file size but better maintainability",
        "alternatives": ["YAML", "TOML", "INI"],
        "status": "accepted",
        "timestamp": "2026-02-26T15:00:00"
    }


@pytest.fixture
def sample_project_info() -> Dict[str, Any]:
    """创建示例项目信息"""
    return {
        "project_type": "web-frontend",
        "tech_stack": {
            "languages": ["JavaScript", "TypeScript"],
            "frameworks": ["React", "Next.js"],
            "libraries": ["axios", "lodash"],
            "runtime": "Node.js 18.x"
        },
        "dev_tools": {
            "package_manager": "npm",
            "build_tool": "webpack",
            "linter": "eslint",
            "formatter": "prettier",
            "testing_framework": "jest"
        },
        "directory_structure": {
            "src": "Source code",
            "public": "Static assets",
            "tests": "Test files"
        },
        "entry_points": ["src/index.js", "src/App.js"],
        "conventions": {
            "indent_style": "space",
            "indent_size": 2,
            "quote_style": "single"
        }
    }
