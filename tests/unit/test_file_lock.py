"""
测试文件锁模块
"""
import pytest
import json
import time
import sys
from pathlib import Path
from threading import Thread

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from file_lock import (
    locked_file,
    safe_read_json,
    safe_write_json,
    safe_update_json,
    FileLockError,
    TransactionLog
)


class TestLockedFile:
    """测试文件锁上下文管理器"""
    
    def test_locked_file_read_mode(self, tmp_path):
        """测试读模式文件锁"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with locked_file(test_file, 'r') as f:
            content = f.read()
            assert content == "test content"
    
    def test_locked_file_write_mode(self, tmp_path):
        """测试写模式文件锁"""
        test_file = tmp_path / "test.txt"
        
        with locked_file(test_file, 'w') as f:
            f.write("new content")
        
        assert test_file.read_text() == "new content"
    
    def test_locked_file_read_plus_mode(self, tmp_path):
        """测试读写模式文件锁"""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"count": 0}')
        
        with locked_file(test_file, 'r+') as f:
            data = json.load(f)
            data['count'] += 1
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
        data = json.loads(test_file.read_text())
        assert data['count'] == 1
    
    def test_locked_file_nonexistent_read_raises_error(self, tmp_path):
        """测试读取不存在的文件抛出错误"""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(FileLockError):
            with locked_file(test_file, 'r') as f:
                pass
    
    def test_locked_file_creates_parent_dirs(self, tmp_path):
        """测试自动创建父目录"""
        test_file = tmp_path / "subdir" / "test.txt"
        
        with locked_file(test_file, 'w') as f:
            f.write("test")
        
        assert test_file.exists()
        assert test_file.parent.exists()


class TestSafeReadJson:
    """测试安全读取 JSON"""
    
    def test_safe_read_json_valid_file(self, tmp_path):
        """测试读取有效的 JSON 文件"""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')
        
        data = safe_read_json(test_file)
        assert data == {"key": "value"}
    
    def test_safe_read_json_nonexistent_returns_default(self, tmp_path):
        """测试读取不存在的文件返回默认值"""
        test_file = tmp_path / "nonexistent.json"
        
        data = safe_read_json(test_file, default=[])
        assert data == []
    
    def test_safe_read_json_invalid_json_returns_default(self, tmp_path):
        """测试读取无效 JSON 返回默认值"""
        test_file = tmp_path / "invalid.json"
        test_file.write_text('{invalid json}')
        
        data = safe_read_json(test_file, default={})
        assert data == {}


class TestSafeWriteJson:
    """测试安全写入 JSON"""
    
    def test_safe_write_json_creates_file(self, tmp_path):
        """测试写入创建文件"""
        test_file = tmp_path / "test.json"
        
        success = safe_write_json(test_file, {"key": "value"})
        assert success is True
        assert test_file.exists()
        
        data = json.loads(test_file.read_text())
        assert data == {"key": "value"}
    
    def test_safe_write_json_overwrites_existing(self, tmp_path):
        """测试写入覆盖现有文件"""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"old": "data"}')
        
        success = safe_write_json(test_file, {"new": "data"})
        assert success is True
        
        data = json.loads(test_file.read_text())
        assert data == {"new": "data"}


class TestSafeUpdateJson:
    """测试安全更新 JSON"""
    
    def test_safe_update_json_updates_existing_file(self, tmp_path):
        """测试更新现有文件"""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"count": 0}')
        
        def increment(data):
            data['count'] += 1
            return data
        
        success = safe_update_json(test_file, increment)
        assert success is True
        
        data = json.loads(test_file.read_text())
        assert data['count'] == 1
    
    def test_safe_update_json_creates_file_with_default(self, tmp_path):
        """测试使用默认值创建文件"""
        test_file = tmp_path / "test.json"
        
        def add_item(data):
            data.append("item")
            return data
        
        success = safe_update_json(test_file, add_item, default=[])
        assert success is True
        
        data = json.loads(test_file.read_text())
        assert data == ["item"]
    
    def test_safe_update_json_handles_invalid_json(self, tmp_path):
        """测试处理无效 JSON"""
        test_file = tmp_path / "test.json"
        test_file.write_text('{invalid}')
        
        def set_value(data):
            return {"fixed": True}
        
        success = safe_update_json(test_file, set_value, default={})
        assert success is True
        
        data = json.loads(test_file.read_text())
        assert data == {"fixed": True}


class TestTransactionLog:
    """测试事务日志"""
    
    def test_transaction_log_records_operation(self, tmp_path):
        """测试记录操作"""
        log_file = tmp_path / "transaction.log"
        log = TransactionLog(log_file)
        
        log.log_operation("create", "/path/to/file.json", {"id": "123"})
        
        assert log_file.exists()
        operations = log.get_recent_operations()
        assert len(operations) == 1
        assert operations[0]['operation'] == "create"
        assert operations[0]['file_path'] == "/path/to/file.json"
    
    def test_transaction_log_get_recent_operations(self, tmp_path):
        """测试获取最近操作"""
        log_file = tmp_path / "transaction.log"
        log = TransactionLog(log_file)
        
        # 记录多个操作
        for i in range(5):
            log.log_operation("update", f"/file{i}.json")
        
        # 获取最近 3 个
        operations = log.get_recent_operations(count=3)
        assert len(operations) == 3
    
    def test_transaction_log_empty_log_returns_empty_list(self, tmp_path):
        """测试空日志返回空列表"""
        log_file = tmp_path / "nonexistent.log"
        log = TransactionLog(log_file)
        
        operations = log.get_recent_operations()
        assert operations == []


class TestConcurrency:
    """测试并发场景"""
    
    def test_concurrent_writes_are_safe(self, tmp_path):
        """测试并发写入是安全的"""
        test_file = tmp_path / "concurrent.json"
        test_file.write_text('{"count": 0}')
        
        def increment_count():
            for _ in range(10):
                def inc(data):
                    data['count'] += 1
                    return data
                safe_update_json(test_file, inc)
        
        # 创建多个线程同时写入
        threads = [Thread(target=increment_count) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 验证最终计数正确
        data = json.loads(test_file.read_text())
        assert data['count'] == 30  # 3 threads × 10 increments
