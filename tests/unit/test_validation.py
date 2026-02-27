"""
测试输入验证模块
"""
import pytest
import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from validation import (
    validate_bug,
    validate_requirement,
    validate_decision,
    validate_json_file
)


class TestBugValidation:
    """测试 bug 验证"""
    
    def test_validate_bug_valid_data_returns_true(self, sample_bug):
        """测试验证 bug 在数据有效时返回 True"""
        valid, error = validate_bug(sample_bug)
        assert valid is True
        assert error is None
    
    def test_validate_bug_missing_id_returns_false(self, sample_bug):
        """测试验证 bug 在缺少 ID 时返回 False"""
        del sample_bug["id"]
        valid, error = validate_bug(sample_bug)
        assert valid is False
        assert "id" in error
    
    def test_validate_bug_missing_title_returns_false(self, sample_bug):
        """测试验证 bug 在缺少标题时返回 False"""
        del sample_bug["title"]
        valid, error = validate_bug(sample_bug)
        assert valid is False
        assert "title" in error
    
    def test_validate_bug_empty_title_returns_false(self, sample_bug):
        """测试验证 bug 在标题为空时返回 False"""
        sample_bug["title"] = ""
        valid, error = validate_bug(sample_bug)
        assert valid is False
        assert "长度" in error or "minLength" in error
    
    def test_validate_bug_invalid_severity_returns_false(self, sample_bug):
        """测试验证 bug 在严重程度无效时返回 False"""
        sample_bug["severity"] = "invalid"
        valid, error = validate_bug(sample_bug)
        assert valid is False
        assert "severity" in error
    
    def test_validate_bug_invalid_id_format_returns_false(self, sample_bug):
        """测试验证 bug 在 ID 格式无效时返回 False"""
        sample_bug["id"] = "INVALID-ID"
        valid, error = validate_bug(sample_bug)
        assert valid is False
        assert "id" in error or "格式" in error
    
    def test_validate_bug_title_too_long_returns_false(self, sample_bug):
        """测试验证 bug 在标题过长时返回 False"""
        sample_bug["title"] = "x" * 201
        valid, error = validate_bug(sample_bug)
        assert valid is False
        assert "title" in error
    
    def test_validate_bug_with_optional_fields_returns_true(self, sample_bug):
        """测试验证 bug 包含可选字段时返回 True"""
        sample_bug["status"] = "open"
        sample_bug["tags"] = ["test", "validation"]
        valid, error = validate_bug(sample_bug)
        assert valid is True


class TestRequirementValidation:
    """测试需求验证"""
    
    def test_validate_requirement_valid_data_returns_true(self, sample_requirement):
        """测试验证需求在数据有效时返回 True"""
        valid, error = validate_requirement(sample_requirement)
        assert valid is True
        assert error is None
    
    def test_validate_requirement_missing_priority_returns_false(self, sample_requirement):
        """测试验证需求在缺少优先级时返回 False"""
        del sample_requirement["priority"]
        valid, error = validate_requirement(sample_requirement)
        assert valid is False
        assert "priority" in error
    
    def test_validate_requirement_invalid_status_returns_false(self, sample_requirement):
        """测试验证需求在状态无效时返回 False"""
        sample_requirement["status"] = "invalid"
        valid, error = validate_requirement(sample_requirement)
        assert valid is False
        assert "status" in error


class TestDecisionValidation:
    """测试架构决策验证"""
    
    def test_validate_decision_valid_data_returns_true(self, sample_decision):
        """测试验证决策在数据有效时返回 True"""
        valid, error = validate_decision(sample_decision)
        assert valid is True
        assert error is None
    
    def test_validate_decision_missing_context_returns_false(self, sample_decision):
        """测试验证决策在缺少上下文时返回 False"""
        del sample_decision["context"]
        valid, error = validate_decision(sample_decision)
        assert valid is False
        assert "context" in error
    
    def test_validate_decision_empty_decision_returns_false(self, sample_decision):
        """测试验证决策在决策内容为空时返回 False"""
        sample_decision["decision"] = ""
        valid, error = validate_decision(sample_decision)
        assert valid is False


class TestJSONFileValidation:
    """测试 JSON 文件验证"""
    
    def test_validate_json_file_valid_file_returns_true(self, tmp_path):
        """测试验证有效的 JSON 文件返回 True"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}')
        
        valid, error = validate_json_file(str(json_file))
        assert valid is True
        assert error is None
    
    def test_validate_json_file_invalid_json_returns_false(self, tmp_path):
        """测试验证无效的 JSON 文件返回 False"""
        json_file = tmp_path / "invalid.json"
        json_file.write_text('{invalid json}')
        
        valid, error = validate_json_file(str(json_file))
        assert valid is False
        assert "JSON" in error or "格式" in error
    
    def test_validate_json_file_nonexistent_file_returns_false(self):
        """测试验证不存在的文件返回 False"""
        valid, error = validate_json_file("/nonexistent/file.json")
        assert valid is False
        assert "不存在" in error or "FileNotFoundError" in str(error)
