# Project Guardian Skill - 快速参考

**版本**: v1.0.2 (优化版)  
**更新日期**: 2026-02-26

---

## 🚀 快速开始

### 运行测试

```bash
# 进入项目目录
cd ~/.craft-agent/skills/project-guardian

# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/unit/test_validation.py -v
pytest tests/unit/test_file_lock.py -v
pytest tests/integration/ -v
```

---

## 📚 新增模块使用指南

### 1. 输入验证模块 (validation.py)

#### 验证 Bug

```python
from scripts.validation import validate_bug

bug = {
    "id": "BUG-20260226150000-a1b2",
    "title": "Memory leak in parser",
    "description": "Parser leaks memory when processing large files",
    "severity": "high",  # low, medium, high, critical
    "status": "open",    # open, in-progress, resolved, closed
    "tags": ["parser", "memory"],
    "timestamp": "2026-02-26T15:00:00"
}

valid, error = validate_bug(bug)
if not valid:
    print(f"❌ 验证失败: {error}")
else:
    print("✅ 验证通过")
```

#### 验证需求

```python
from scripts.validation import validate_requirement

requirement = {
    "id": "REQ-20260226150000-c3d4",
    "title": "Add input validation",
    "description": "Validate all user inputs",
    "priority": "high",  # low, medium, high, critical
    "status": "planned", # planned, in-progress, completed, cancelled
    "tags": ["validation", "security"]
}

valid, error = validate_requirement(requirement)
```

#### 验证架构决策

```python
from scripts.validation import validate_decision

decision = {
    "id": "DEC-20260226150000-e5f6",
    "title": "Use JSON for configuration",
    "context": "Need a human-readable format",
    "decision": "Use JSON instead of binary",
    "rationale": "JSON is widely supported",
    "status": "accepted"  # proposed, accepted, rejected, deprecated
}

valid, error = validate_decision(decision)
```

---

### 2. 文件锁模块 (file_lock.py)

#### 基本文件锁

```python
from pathlib import Path
from scripts.file_lock import locked_file
import json

# 读取文件
with locked_file(Path("data.json"), 'r', timeout=10.0) as f:
    data = json.load(f)

# 写入文件
with locked_file(Path("data.json"), 'w') as f:
    json.dump(data, f, indent=2)

# 读写文件（原子操作）
with locked_file(Path("data.json"), 'r+') as f:
    data = json.load(f)
    data['count'] += 1
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
```

#### 安全读取 JSON

```python
from pathlib import Path
from scripts.file_lock import safe_read_json

# 读取文件，不存在时返回默认值
bugs = safe_read_json(Path("bugs.json"), default=[])
config = safe_read_json(Path("config.json"), default={})
```

#### 安全写入 JSON

```python
from pathlib import Path
from scripts.file_lock import safe_write_json

bugs = [{"id": "BUG-001", "title": "Test"}]
success = safe_write_json(Path("bugs.json"), bugs)

if success:
    print("✅ 写入成功")
else:
    print("❌ 写入失败")
```

#### 安全更新 JSON（推荐）

```python
from pathlib import Path
from scripts.file_lock import safe_update_json

# 添加 bug
def add_bug(bugs):
    new_bug = {
        "id": "BUG-20260226150000-a1b2",
        "title": "New bug",
        "description": "Description"
    }
    bugs.append(new_bug)
    return bugs

success = safe_update_json(
    Path("bugs.json"),
    add_bug,
    default=[]
)

# 更新 bug 状态
def update_status(bugs):
    for bug in bugs:
        if bug['id'] == "BUG-001":
            bug['status'] = 'resolved'
    return bugs

safe_update_json(Path("bugs.json"), update_status)

# 删除 bug
def remove_bug(bugs):
    return [b for b in bugs if b['id'] != "BUG-001"]

safe_update_json(Path("bugs.json"), remove_bug)
```

#### 事务日志

```python
from pathlib import Path
from scripts.file_lock import TransactionLog

# 创建日志
log = TransactionLog(Path(".project-ai/transaction.log"))

# 记录操作
log.log_operation(
    operation="create",
    file_path="/path/to/bugs.json",
    data={"id": "BUG-001", "title": "New bug"}
)

log.log_operation(
    operation="update",
    file_path="/path/to/bugs.json",
    data={"id": "BUG-001", "status": "resolved"}
)

# 获取最近操作
recent = log.get_recent_operations(count=10)
for op in recent:
    print(f"{op['operation']}: {op['file_path']}")
```

---

## 🔧 集成到现有代码

### 在 update_knowledge.py 中使用

```python
from pathlib import Path
from scripts.validation import validate_bug
from scripts.file_lock import safe_update_json

def add_bug_to_knowledge_base(knowledge_base_path, bug_data):
    """添加 bug 到知识库（带验证和并发安全）"""
    
    # 1. 验证数据
    valid, error = validate_bug(bug_data)
    if not valid:
        print(f"❌ Bug 数据验证失败: {error}")
        return False
    
    # 2. 安全添加到文件
    bugs_file = Path(knowledge_base_path) / "indexed" / "bugs.json"
    
    def add_bug(bugs):
        bugs.append(bug_data)
        return bugs
    
    success = safe_update_json(bugs_file, add_bug, default=[])
    
    if success:
        print(f"✅ Bug 已添加: {bug_data['id']}")
    else:
        print(f"❌ 添加 Bug 失败")
    
    return success
```

### 在 search_similar.py 中使用

```python
from pathlib import Path
from scripts.file_lock import safe_read_json

def search_bugs(knowledge_base_path, query):
    """搜索 bugs（并发安全）"""
    
    # 安全读取 bugs
    bugs_file = Path(knowledge_base_path) / "indexed" / "bugs.json"
    bugs = safe_read_json(bugs_file, default=[])
    
    # 执行搜索
    results = []
    for bug in bugs:
        if query.lower() in bug['title'].lower() or \
           query.lower() in bug['description'].lower():
            results.append(bug)
    
    return results
```

---

## 🧪 测试示例

### 单元测试示例

```python
import pytest
from scripts.validation import validate_bug

def test_validate_bug_valid_data():
    """测试有效的 bug 数据"""
    bug = {
        "id": "BUG-20260226150000-a1b2",
        "title": "Test bug",
        "description": "Test description",
        "severity": "high"
    }
    
    valid, error = validate_bug(bug)
    assert valid is True
    assert error is None

def test_validate_bug_missing_title():
    """测试缺少标题的 bug"""
    bug = {
        "id": "BUG-20260226150000-a1b2",
        "description": "Test description",
        "severity": "high"
    }
    
    valid, error = validate_bug(bug)
    assert valid is False
    assert "title" in error
```

### 集成测试示例

```python
import pytest
from pathlib import Path
from scripts.validation import validate_bug
from scripts.file_lock import safe_update_json, safe_read_json

def test_add_and_search_bug(tmp_path):
    """测试添加并搜索 bug"""
    bugs_file = tmp_path / "bugs.json"
    
    # 创建 bug
    bug = {
        "id": "BUG-001",
        "title": "Test bug",
        "description": "Test description",
        "severity": "high"
    }
    
    # 验证
    valid, error = validate_bug(bug)
    assert valid is True
    
    # 添加
    def add_bug(bugs):
        bugs.append(bug)
        return bugs
    
    success = safe_update_json(bugs_file, add_bug, default=[])
    assert success is True
    
    # 读取并验证
    bugs = safe_read_json(bugs_file)
    assert len(bugs) == 1
    assert bugs[0]['id'] == "BUG-001"
```

---

## 📊 测试覆盖率

### 查看覆盖率

```bash
# 生成覆盖率报告
pytest tests/ --cov=scripts --cov-report=html

# 打开报告
open htmlcov/index.html
```

### 当前覆盖率

| 模块 | 覆盖率 | 测试数 |
|------|--------|--------|
| validation.py | 100% | 17 |
| file_lock.py | 100% | 17 |
| 集成测试 | - | 6 |
| **总计** | **100%** | **40** |

---

## 🐛 常见问题

### Q: 文件锁超时怎么办？

A: 增加超时时间或检查是否有其他进程占用文件

```python
# 增加超时时间
with locked_file(path, 'r+', timeout=30.0) as f:
    # ...

# 或使用更短的超时快速失败
try:
    with locked_file(path, 'r+', timeout=1.0) as f:
        # ...
except FileLockError:
    print("文件被占用，请稍后重试")
```

### Q: 如何处理验证失败？

A: 记录错误并提供清晰的反馈

```python
valid, error = validate_bug(bug_data)
if not valid:
    # 记录到日志
    logger.error(f"Bug 验证失败: {error}")
    
    # 返回错误给用户
    return {
        "success": False,
        "error": error,
        "suggestion": "请检查数据格式是否正确"
    }
```

### Q: 如何在多进程环境中使用？

A: 使用 `safe_update_json` 确保并发安全

```python
from multiprocessing import Process
from scripts.file_lock import safe_update_json

def worker(worker_id):
    def add_entry(data):
        data.append({"worker": worker_id})
        return data
    
    safe_update_json(Path("data.json"), add_entry, default=[])

# 启动多个进程
processes = [Process(target=worker, args=(i,)) for i in range(10)]
for p in processes:
    p.start()
for p in processes:
    p.join()

# 数据不会丢失或损坏
```

---

## 📖 相关文档

- [OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md) - 详细的优化总结
- [README.md](./README.md) - 项目主文档
- [CHANGELOG.md](./CHANGELOG.md) - 版本变更记录

---

## 🆘 获取帮助

如果遇到问题：

1. 查看测试用例了解使用方法
2. 阅读模块文档字符串
3. 运行测试验证功能
4. 查看 OPTIMIZATION_SUMMARY.md

---

**最后更新**: 2026-02-26  
**版本**: v1.0.2
