# Project Guardian Skill - 多项目数据隔离说明

## ✅ 数据隔离保证

Project Guardian **完全隔离**每个项目的数据,确保多个项目之间互不干扰。

## 隔离机制

### 1. 独立存储位置

每个项目的知识库存储在**项目自己的根目录**下:

```
/Users/you/projects/
├── project-a/
│   ├── .project-ai/          ← project-a 的知识库
│   │   ├── core/
│   │   │   ├── profile.json
│   │   │   ├── tech-stack.json
│   │   │   └── conventions.json
│   │   ├── indexed/
│   │   └── history/
│   │       ├── bugs/
│   │       ├── requirements/
│   │       └── decisions/
│   └── [project files...]
│
├── project-b/
│   ├── .project-ai/          ← project-b 的知识库
│   │   ├── core/
│   │   ├── indexed/
│   │   └── history/
│   └── [project files...]
│
└── project-c/
    ├── .project-ai/          ← project-c 的知识库
    │   ├── core/
    │   ├── indexed/
    │   └── history/
    └── [project files...]
```

### 2. 绝对路径解析

代码实现 (scan_project.py):
```python
def __init__(self, project_path: str):
    self.project_path = Path(project_path).resolve()  # 解析为绝对路径
    self.knowledge_base_path = self.project_path / ".project-ai"
```

**关键点**:
- 使用 `Path.resolve()` 获取绝对路径
- 避免相对路径导致的混淆
- 每个项目的知识库路径唯一确定

### 3. 实测验证

我们创建了两个测试项目并验证:

**Project A** (React 项目):
```json
{
  "frameworks": ["React 18.0.0"],
  "runtime": ["Node.js"]
}
```

**Project B** (Vue 项目):
```json
{
  "frameworks": ["Vue 3.0.0"],
  "runtime": ["Node.js"]
}
```

**结果**: 两个项目的数据完全独立,互不影响 ✅

## 使用场景示例

### 场景 1: 同时维护多个项目

```bash
# 初始化项目 A
cd ~/projects/ecommerce-frontend
python /path/to/scripts/scan_project.py .
# 创建 ~/projects/ecommerce-frontend/.project-ai/

# 初始化项目 B
cd ~/projects/blog-backend
python /path/to/scripts/scan_project.py .
# 创建 ~/projects/blog-backend/.project-ai/

# 初始化项目 C
cd ~/projects/mobile-app
python /path/to/scripts/scan_project.py .
# 创建 ~/projects/mobile-app/.project-ai/
```

**结果**: 三个项目各自有独立的知识库,互不干扰。

### 场景 2: 在不同项目间切换

```bash
# 在项目 A 中工作
cd ~/projects/ecommerce-frontend
python scripts/update_knowledge.py . --type bug --data bug.json
# 只更新 ecommerce-frontend/.project-ai/

# 切换到项目 B
cd ~/projects/blog-backend
python scripts/search_similar.py . "database timeout"
# 只搜索 blog-backend/.project-ai/
```

**结果**: 每个操作只影响当前项目的知识库。

### 场景 3: 与 Claude 对话

**在项目 A 中**:
```
你: "What's our tech stack?"
Claude: [读取 ecommerce-frontend/.project-ai/core/tech-stack.json]
       "React 18.2.0, TypeScript, Tailwind CSS"
```

**切换到项目 B**:
```
你: "What's our tech stack?"
Claude: [读取 blog-backend/.project-ai/core/tech-stack.json]
       "Express 4.18.2, PostgreSQL, Node.js"
```

**结果**: Claude 自动识别当前工作目录,加载对应项目的知识库。

## 工作目录识别

### Claude 如何知道当前项目?

1. **通过工作目录**: Claude 会检查当前工作目录
2. **通过显式路径**: 脚本需要传入项目路径参数
3. **通过上下文**: 对话中提到的文件路径

### 最佳实践

#### ✅ 推荐做法

```bash
# 方式 1: 切换到项目目录
cd /path/to/project-a
python scripts/scan_project.py .

# 方式 2: 使用绝对路径
python scripts/scan_project.py /path/to/project-a

# 方式 3: 在对话中明确指定
"Scan the project at /path/to/project-a"
```

#### ❌ 避免的做法

```bash
# 不要在错误的目录运行
cd /path/to/project-a
python scripts/scan_project.py /path/to/project-b  # 混淆!

# 不要使用相对路径跨项目
cd /path/to/project-a
python scripts/scan_project.py ../project-b  # 可能混淆
```

## 数据隔离的好处

### 1. 避免数据污染
- 项目 A 的 bug 不会出现在项目 B 的搜索结果中
- 每个项目的技术栈、规范独立维护
- 不会因为项目间的差异导致混淆

### 2. 便于项目迁移
```bash
# 移动项目时,知识库一起移动
mv ~/projects/project-a ~/archive/project-a
# .project-ai/ 自动跟随项目移动
```

### 3. 支持版本控制
```bash
# 可以选择将知识库纳入 Git
cd ~/projects/project-a
git add .project-ai/
git commit -m "Add project knowledge base"

# 团队成员 clone 后自动获得知识库
git clone repo-url
# .project-ai/ 已包含在仓库中
```

### 4. 便于清理
```bash
# 删除项目时,知识库一起删除
rm -rf ~/projects/old-project
# .project-ai/ 自动删除,不留残留
```

## 团队协作场景

### 场景: 多人共享知识库

**方式 1: 通过 Git 共享**
```bash
# 开发者 A
cd project
python scripts/scan_project.py .
git add .project-ai/
git commit -m "Initialize project knowledge base"
git push

# 开发者 B
git pull
# 自动获得 .project-ai/
```

**方式 2: 独立维护**
```bash
# 每个开发者维护自己的知识库
echo ".project-ai/" >> .gitignore
# 各自运行 scan_project.py 初始化
```

### 推荐策略

**共享内容** (建议纳入 Git):
- `core/profile.json` - 项目元数据
- `core/tech-stack.json` - 技术栈
- `core/conventions.json` - 代码规范
- `indexed/architecture.json` - 架构设计
- `history/decisions/` - 架构决策

**个人内容** (建议 .gitignore):
- `history/bugs/` - 个人遇到的 bug
- `history/requirements/` - 个人任务

**配置示例** (.gitignore):
```
# 共享核心知识
!.project-ai/core/
!.project-ai/indexed/
!.project-ai/history/decisions/

# 忽略个人记录
.project-ai/history/bugs/
.project-ai/history/requirements/
```

## 常见问题

### Q1: 如果我在错误的目录运行脚本会怎样?

**A**: 脚本会在**你指定的目录**创建 `.project-ai/`,不会影响其他项目。

示例:
```bash
cd /tmp
python scripts/scan_project.py ~/projects/project-a
# 在 ~/projects/project-a/.project-ai/ 创建知识库
# /tmp 不受影响
```

### Q2: 可以为同一个项目创建多个知识库吗?

**A**: 不建议。每个项目应该只有一个 `.project-ai/` 目录。如果需要备份:
```bash
cp -r .project-ai .project-ai.backup
```

### Q3: 如何在多个项目间共享某些知识?

**A**: 有几种方式:

**方式 1: 符号链接** (不推荐,可能导致混淆)
```bash
ln -s ~/shared-knowledge/conventions.json .project-ai/core/conventions.json
```

**方式 2: 手动复制**
```bash
cp project-a/.project-ai/core/conventions.json project-b/.project-ai/core/
```

**方式 3: 创建组织级别的规范文档** (推荐)
```bash
# 在组织级别维护规范
~/company-standards/
├── coding-conventions.md
├── architecture-patterns.md
└── tech-stack-guidelines.md

# 各项目引用,而不是复制
```

### Q4: 知识库会占用多少空间?

**A**: 非常小!

- **初始扫描**: ~10 KB
- **100 个 bug 记录**: ~110 KB
- **1000 个 bug 记录**: ~1.1 MB

即使长期使用,也不会占用太多空间。

### Q5: 如何迁移知识库到新项目?

**A**: 直接复制 `.project-ai/` 目录:
```bash
cp -r old-project/.project-ai new-project/
cd new-project
# 更新项目信息
python scripts/scan_project.py .  # 重新扫描
```

## 安全性考虑

### 1. 敏感信息

**不要在知识库中存储**:
- API 密钥
- 密码
- 个人身份信息
- 商业机密

**如果需要记录敏感信息**:
```bash
# 加密知识库
tar -czf .project-ai.tar.gz .project-ai/
gpg -c .project-ai.tar.gz
rm -rf .project-ai/

# 使用时解密
gpg -d .project-ai.tar.gz.gpg | tar -xz
```

### 2. 权限控制

```bash
# 限制知识库访问权限
chmod 700 .project-ai/
chmod 600 .project-ai/core/*.json
```

## 总结

✅ **完全隔离**: 每个项目的知识库独立存储在项目根目录
✅ **绝对路径**: 使用绝对路径避免混淆
✅ **易于管理**: 随项目移动、删除、版本控制
✅ **团队友好**: 支持共享或独立维护
✅ **安全可靠**: 不会跨项目污染数据

**你可以放心地在多个项目中使用 Project Guardian,数据绝对不会互串!**
