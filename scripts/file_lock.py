"""
文件锁模块
提供安全的并发文件访问控制
"""
import fcntl
import time
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Dict


class FileLockError(Exception):
    """文件锁相关错误"""
    pass


@contextmanager
def locked_file(path: Path, mode: str = 'r', timeout: float = 10.0):
    """
    文件锁上下文管理器
    
    使用文件锁确保并发安全访问。支持超时机制。
    
    Args:
        path: 文件路径
        mode: 打开模式 ('r', 'w', 'r+', 'a')
        timeout: 超时时间（秒），默认 10 秒
    
    Yields:
        打开的文件对象
    
    Raises:
        FileLockError: 无法获取锁或超时
    
    Example:
        >>> with locked_file(Path("data.json"), 'r+') as f:
        ...     data = json.load(f)
        ...     data['count'] += 1
        ...     f.seek(0)
        ...     json.dump(data, f)
        ...     f.truncate()
    """
    path = Path(path)
    
    # 确保父目录存在
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # 打开文件
    try:
        f = open(path, mode)
    except FileNotFoundError:
        if 'r' in mode:
            raise FileLockError(f"文件不存在: {path}")
        # 创建文件
        path.touch()
        f = open(path, mode)
    
    start_time = time.time()
    lock_acquired = False
    
    try:
        # 尝试获取锁
        while True:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                lock_acquired = True
                break
            except IOError:
                # 锁被占用
                if time.time() - start_time > timeout:
                    raise FileLockError(
                        f"无法获取文件锁: {path} (超时 {timeout}秒)\n"
                        f"可能有其他进程正在访问此文件"
                    )
                time.sleep(0.1)
        
        # 返回文件对象
        yield f
    
    finally:
        # 释放锁并关闭文件
        if lock_acquired:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except:
                pass
        try:
            f.close()
        except:
            pass


def safe_read_json(path: Path, default: Any = None) -> Any:
    """
    安全读取 JSON 文件（带文件锁）
    
    Args:
        path: JSON 文件路径
        default: 文件不存在或读取失败时的默认值
    
    Returns:
        解析后的 JSON 数据，或默认值
    
    Example:
        >>> data = safe_read_json(Path("bugs.json"), default=[])
    """
    try:
        with locked_file(path, 'r', timeout=5.0) as f:
            return json.load(f)
    except (FileNotFoundError, FileLockError, json.JSONDecodeError):
        return default


def safe_write_json(path: Path, data: Any, indent: int = 2) -> bool:
    """
    安全写入 JSON 文件（带文件锁）
    
    Args:
        path: JSON 文件路径
        data: 要写入的数据
        indent: JSON 缩进空格数
    
    Returns:
        是否成功写入
    
    Example:
        >>> success = safe_write_json(Path("bugs.json"), bugs_list)
    """
    try:
        with locked_file(path, 'w', timeout=5.0) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except (FileLockError, IOError) as e:
        print(f"❌ 写入文件失败: {e}")
        return False


def safe_update_json(path: Path, update_func, default: Any = None, timeout: float = 10.0) -> bool:
    """
    安全更新 JSON 文件（读取-修改-写入，原子操作）

    Args:
        path: JSON 文件路径
        update_func: 更新函数，接收当前数据，返回新数据
        default: 文件不存在时的默认值
        timeout: 超时时间（秒）

    Returns:
        是否成功更新

    Example:
        >>> def add_bug(bugs):
        ...     bugs.append(new_bug)
        ...     return bugs
        >>> safe_update_json(Path("bugs.json"), add_bug, default=[])
    """
    path = Path(path)

    try:
        # 如果文件不存在，先创建它
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(default if default is not None else {}, indent=2))

        with locked_file(path, 'r+', timeout=timeout) as f:
            # 读取当前数据
            try:
                data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                data = default

            # 应用更新函数
            updated_data = update_func(data)

            # 写回文件
            f.seek(0)
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
            f.truncate()

        return True

    except FileLockError as e:
        print(f"❌ 更新文件失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 更新文件时出错: {e}")
        return False


class TransactionLog:
    """
    事务日志
    记录所有文件操作，用于故障恢复
    """
    
    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_operation(self, operation: str, file_path: str, data: Dict = None):
        """
        记录操作到事务日志
        
        Args:
            operation: 操作类型 (create, update, delete)
            file_path: 操作的文件路径
            data: 操作相关的数据
        """
        entry = {
            "timestamp": time.time(),
            "operation": operation,
            "file_path": file_path,
            "data": data
        }
        
        try:
            with locked_file(self.log_path, 'a', timeout=5.0) as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except FileLockError:
            # 日志写入失败不应该阻塞主操作
            pass
    
    def get_recent_operations(self, count: int = 10) -> list:
        """
        获取最近的操作记录
        
        Args:
            count: 返回的记录数量
        
        Returns:
            操作记录列表
        """
        if not self.log_path.exists():
            return []
        
        try:
            with locked_file(self.log_path, 'r', timeout=5.0) as f:
                lines = f.readlines()
                recent_lines = lines[-count:] if len(lines) > count else lines
                return [json.loads(line) for line in recent_lines if line.strip()]
        except (FileLockError, json.JSONDecodeError):
            return []


if __name__ == "__main__":
    # 测试示例
    import tempfile
    
    test_file = Path(tempfile.gettempdir()) / "test_lock.json"
    
    # 测试安全写入
    print("测试安全写入...")
    success = safe_write_json(test_file, {"count": 0})
    print(f"写入结果: {success}")
    
    # 测试安全读取
    print("\n测试安全读取...")
    data = safe_read_json(test_file)
    print(f"读取数据: {data}")
    
    # 测试安全更新
    print("\n测试安全更新...")
    def increment(data):
        data["count"] += 1
        return data
    
    success = safe_update_json(test_file, increment)
    print(f"更新结果: {success}")
    
    data = safe_read_json(test_file)
    print(f"更新后数据: {data}")
    
    # 清理
    test_file.unlink()
    print("\n✓ 测试完成")
