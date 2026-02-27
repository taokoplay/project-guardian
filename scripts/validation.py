"""
输入验证模块
使用 JSON Schema 验证数据格式
"""
import json
from typing import Dict, Any, Tuple, Optional
from datetime import datetime


# JSON Schema 定义
BUG_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "description", "severity"],
    "properties": {
        "id": {
            "type": "string",
            "pattern": "^BUG-\\d{14}-[a-f0-9]{4}$"
        },
        "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "description": {
            "type": "string",
            "minLength": 1
        },
        "severity": {
            "type": "string",
            "enum": ["low", "medium", "high", "critical"]
        },
        "status": {
            "type": "string",
            "enum": ["open", "in-progress", "resolved", "closed"]
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "timestamp": {"type": "string"},
        "file_path": {"type": "string"},
        "line_number": {"type": "integer", "minimum": 1}
    }
}

REQUIREMENT_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "description", "priority"],
    "properties": {
        "id": {
            "type": "string",
            "pattern": "^REQ-\\d{14}-[a-f0-9]{4}$"
        },
        "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "description": {
            "type": "string",
            "minLength": 1
        },
        "priority": {
            "type": "string",
            "enum": ["low", "medium", "high", "critical"]
        },
        "status": {
            "type": "string",
            "enum": ["planned", "in-progress", "completed", "cancelled"]
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "timestamp": {"type": "string"}
    }
}

DECISION_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "context", "decision"],
    "properties": {
        "id": {
            "type": "string",
            "pattern": "^DEC-\\d{14}-[a-f0-9]{4}$"
        },
        "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "context": {"type": "string", "minLength": 1},
        "decision": {"type": "string", "minLength": 1},
        "rationale": {"type": "string"},
        "consequences": {"type": "string"},
        "alternatives": {
            "type": "array",
            "items": {"type": "string"}
        },
        "status": {
            "type": "string",
            "enum": ["proposed", "accepted", "rejected", "deprecated"]
        },
        "timestamp": {"type": "string"}
    }
}


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证数据是否符合 schema
    
    Args:
        data: 要验证的数据
        schema: JSON Schema
    
    Returns:
        (是否有效, 错误消息)
    """
    try:
        # 检查必需字段
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                return False, f"缺少必需字段: {field}"
        
        # 检查字段类型和约束
        properties = schema.get("properties", {})
        for field, value in data.items():
            if field not in properties:
                continue
            
            field_schema = properties[field]
            field_type = field_schema.get("type")
            
            # 类型检查
            if field_type == "string" and not isinstance(value, str):
                return False, f"字段 {field} 必须是字符串"
            elif field_type == "integer" and not isinstance(value, int):
                return False, f"字段 {field} 必须是整数"
            elif field_type == "array" and not isinstance(value, list):
                return False, f"字段 {field} 必须是数组"
            
            # 字符串约束
            if field_type == "string" and isinstance(value, str):
                min_len = field_schema.get("minLength")
                max_len = field_schema.get("maxLength")
                if min_len and len(value) < min_len:
                    return False, f"字段 {field} 长度不能小于 {min_len}"
                if max_len and len(value) > max_len:
                    return False, f"字段 {field} 长度不能大于 {max_len}"
                
                # 枚举检查
                enum = field_schema.get("enum")
                if enum and value not in enum:
                    return False, f"字段 {field} 必须是以下值之一: {', '.join(enum)}"
                
                # 正则检查
                pattern = field_schema.get("pattern")
                if pattern:
                    import re
                    if not re.match(pattern, value):
                        return False, f"字段 {field} 格式不正确"
            
            # 整数约束
            if field_type == "integer" and isinstance(value, int):
                minimum = field_schema.get("minimum")
                if minimum is not None and value < minimum:
                    return False, f"字段 {field} 不能小于 {minimum}"
        
        return True, None
    
    except Exception as e:
        return False, f"验证失败: {str(e)}"


def validate_bug(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证 bug 数据
    
    Args:
        data: bug 数据字典
    
    Returns:
        (是否有效, 错误消息)
    
    Example:
        >>> bug = {"id": "BUG-20260226150000-a1b2", "title": "Test", ...}
        >>> valid, error = validate_bug(bug)
        >>> assert valid is True
    """
    return validate_schema(data, BUG_SCHEMA)


def validate_requirement(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证需求数据
    
    Args:
        data: 需求数据字典
    
    Returns:
        (是否有效, 错误消息)
    """
    return validate_schema(data, REQUIREMENT_SCHEMA)


def validate_decision(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证架构决策数据
    
    Args:
        data: 决策数据字典
    
    Returns:
        (是否有效, 错误消息)
    """
    return validate_schema(data, DECISION_SCHEMA)


def validate_json_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    验证 JSON 文件格式
    
    Args:
        file_path: JSON 文件路径
    
    Returns:
        (是否有效, 错误消息)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON 格式错误: {e.msg} (行 {e.lineno}, 列 {e.colno})"
    except FileNotFoundError:
        return False, f"文件不存在: {file_path}"
    except Exception as e:
        return False, f"读取文件失败: {str(e)}"


if __name__ == "__main__":
    # 测试示例
    test_bug = {
        "id": "BUG-20260226150000-a1b2",
        "title": "Test bug",
        "description": "This is a test",
        "severity": "high"
    }
    
    valid, error = validate_bug(test_bug)
    print(f"验证结果: {valid}")
    if error:
        print(f"错误: {error}")
