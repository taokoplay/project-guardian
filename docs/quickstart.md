# 快速开始指南

## 5 分钟上手 Project Guardian

### 1. 安装

```bash
# 方式 1: 克隆到本地
git clone https://github.com/taokoplay/project-guardian.git
cd project-guardian

# 方式 2: 作为子模块添加
cd your-project
git submodule add https://github.com/taokoplay/project-guardian.git .guardian
```

### 2. 初始化项目

```bash
# 使用安装脚本 (推荐)
./install.sh /path/to/your/project

# 或手动运行扫描
python scripts/scan_project.py /path/to/your/project
```

### 3. 查看结果

扫描完成后,检查创建的知识库:

```bash
cd /path/to/your/project
ls -la .project-ai/

# 查看项目信息
cat .project-ai/core/profile.json
cat .project-ai/core/tech-stack.json
```

### 4. 记录第一个 Bug

```bash
# 创建 bug 记录
cat > bug.json << 'EOF'
{
  "title": "Login button not responding",
  "description": "Click event not firing on login button",
  "root_cause": "Missing event listener binding",
  "solution": "Added onClick handler to button component",
  "files_changed": ["src/components/LoginButton.tsx"],
  "tags": ["ui", "bug", "login"],
  "severity": "high"
}
EOF

# 记录到知识库
python /path/to/project-guardian/scripts/update_knowledge.py . --type bug --data bug.json
```

### 5. 搜索问题

```bash
# 搜索相关问题
python /path/to/project-guardian/scripts/search_similar.py . "login button"

# 按标签搜索
python /path/to/project-guardian/scripts/search_similar.py . --tags login,ui
```

## 常见使用场景

### 场景 1: 新项目初始化

```bash
cd new-project
python /path/to/project-guardian/scripts/scan_project.py .
# 确认扫描结果,创建知识库
```

### 场景 2: 修复 Bug 后记录

```bash
# 1. 修复 bug
# 2. 创建 bug 记录
# 3. 记录到知识库
python /path/to/project-guardian/scripts/update_knowledge.py . --type bug --data bug.json
```

### 场景 3: 开发新功能前检查

```bash
# 搜索是否有类似功能或问题
python /path/to/project-guardian/scripts/search_similar.py . "authentication"
```

### 场景 4: 团队协作

```bash
# 将知识库纳入版本控制
git add .project-ai/core/ .project-ai/indexed/
git commit -m "Add project knowledge base"
git push

# 团队成员 pull 后自动获得知识库
```

## 下一步

- 阅读 [完整文档](../SKILL.md)
- 查看 [知识库 Schema](../references/knowledge-schema.md)
- 了解 [多项目使用](isolation.md)

## 需要帮助?

- 查看 [故障排除](../README.md#故障排除)
- 创建 [Issue](https://github.com/taokoplay/project-guardian/issues)
