"""
集成测试：更新知识库工作流
"""
import pytest
import json
import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from file_lock import safe_read_json, safe_write_json, safe_update_json
from validation import validate_bug, validate_requirement


class TestBugWorkflow:
    """测试 bug 工作流"""
    
    def test_add_and_search_bug(self, tmp_knowledge_base, sample_bug):
        """测试添加并搜索 bug"""
        bugs_file = tmp_knowledge_base / "indexed" / "bugs.json"
        
        # 1. 验证 bug 数据
        valid, error = validate_bug(sample_bug)
        assert valid is True, f"Bug 验证失败: {error}"
        
        # 2. 添加 bug 到知识库
        def add_bug(bugs):
            bugs.append(sample_bug)
            return bugs
        
        success = safe_update_json(bugs_file, add_bug, default=[])
        assert success is True
        
        # 3. 读取并验证
        bugs = safe_read_json(bugs_file, default=[])
        assert len(bugs) == 1
        assert bugs[0]['id'] == sample_bug['id']
        assert bugs[0]['title'] == sample_bug['title']
    
    def test_update_bug_status(self, tmp_knowledge_base, sample_bug):
        """测试更新 bug 状态"""
        bugs_file = tmp_knowledge_base / "indexed" / "bugs.json"
        
        # 添加 bug
        safe_write_json(bugs_file, [sample_bug])
        
        # 更新状态
        def update_status(bugs):
            for bug in bugs:
                if bug['id'] == sample_bug['id']:
                    bug['status'] = 'resolved'
            return bugs
        
        success = safe_update_json(bugs_file, update_status)
        assert success is True
        
        # 验证更新
        bugs = safe_read_json(bugs_file)
        assert bugs[0]['status'] == 'resolved'


class TestRequirementWorkflow:
    """测试需求工作流"""
    
    def test_add_requirement(self, tmp_knowledge_base, sample_requirement):
        """测试添加需求"""
        req_file = tmp_knowledge_base / "indexed" / "requirements.json"
        
        # 验证需求数据
        valid, error = validate_requirement(sample_requirement)
        assert valid is True
        
        # 添加需求
        def add_req(reqs):
            reqs.append(sample_requirement)
            return reqs
        
        success = safe_update_json(req_file, add_req, default=[])
        assert success is True
        
        # 验证
        reqs = safe_read_json(req_file)
        assert len(reqs) == 1
        assert reqs[0]['id'] == sample_requirement['id']


class TestMultiProjectIsolation:
    """测试多项目隔离"""
    
    def test_different_projects_have_separate_knowledge_bases(self, tmp_path, sample_bug):
        """测试不同项目有独立的知识库"""
        # 创建两个项目的知识库
        project1_kb = tmp_path / "project1" / ".project-ai"
        project2_kb = tmp_path / "project2" / ".project-ai"
        
        for kb in [project1_kb, project2_kb]:
            kb.mkdir(parents=True)
            (kb / "indexed").mkdir()
            (kb / "indexed" / "bugs.json").write_text("[]")
        
        # 在项目 1 添加 bug
        bugs_file1 = project1_kb / "indexed" / "bugs.json"
        def add_bug(bugs):
            bugs.append(sample_bug)
            return bugs
        safe_update_json(bugs_file1, add_bug)
        
        # 验证项目 1 有 bug
        bugs1 = safe_read_json(bugs_file1)
        assert len(bugs1) == 1
        
        # 验证项目 2 没有 bug
        bugs_file2 = project2_kb / "indexed" / "bugs.json"
        bugs2 = safe_read_json(bugs_file2)
        assert len(bugs2) == 0


class TestErrorHandling:
    """测试错误处理"""
    
    def test_invalid_bug_is_rejected(self, tmp_knowledge_base):
        """测试无效 bug 被拒绝"""
        invalid_bug = {
            "title": "Missing required fields"
            # 缺少 id, description, severity
        }
        
        valid, error = validate_bug(invalid_bug)
        assert valid is False
        assert error is not None
    
    def test_corrupted_json_is_handled(self, tmp_knowledge_base):
        """测试处理损坏的 JSON"""
        bugs_file = tmp_knowledge_base / "indexed" / "bugs.json"
        bugs_file.write_text('{corrupted json}')
        
        # 应该返回默认值而不是崩溃
        bugs = safe_read_json(bugs_file, default=[])
        assert bugs == []
        
        # 应该能够修复文件
        def fix(data):
            return []
        success = safe_update_json(bugs_file, fix, default=[])
        assert success is True
