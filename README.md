# Project Guardian

> 智能项目知识管理系统 - 自动扫描、追踪、防重复

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Project Guardian 是一个轻量级的项目知识管理工具,帮助你:
- 🤖 **智能检测**自动识别未初始化项目并提示初始化
- 🔍 **自动扫描**项目结构、技术栈、开发工具
- 📝 **追踪记录** Bug、需求、架构决策
- 🔎 **智能搜索**历史问题,防止重复
- 💡 **Token 高效**,核心上下文 <2k tokens
- 🔒 **数据隔离**,多项目互不干扰

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/taokoplay/project-guardian.git
cd project-guardian

# 或者作为子模块添加到项目中
cd your-project
git submodule add https://github.com/taokoplay/project-guardian.git .project-guardian-tool
```

### 初始化项目

**方式一：手动初始化**

```bash
# 在项目根目录运行
python project-guardian/scripts/scan_project.py .
```

**方式二：智能检测（推荐）**

当你在 Claude Code 中使用 Project Guardian skill 时，它会自动检测项目是否已初始化：

```
你: 这个项目的认证流程是怎么工作的？

Claude: 🔍 我注意到这个项目还没有初始化知识库。

是否需要我扫描并初始化 Project Guardian？这将：
- 自动检测技术栈和工具
- 学习代码规范和架构
- 启用智能 bug 追踪
- 大约需要 10 秒

是否继续扫描？(yes/no)
```

**检查初始化状态**

```bash
# 快速检查项目是否已初始化
python project-guardian/scripts/check_initialized.py

# 输出示例（已初始化）
{
  "initialized": true,
  "project_root": "/Users/dev/my-app",
  "knowledge_base_path": "/Users/dev/my-app/.project-ai",
  "core_files": {
    "profile.json": true,
    "tech-stack.json": true,
    "conventions.json": true
  }
}

# 输出示例（未初始化）
{
  "initialized": false,
  "current_path": "/Users/dev/my-app",
  "is_likely_project": true,
  "suggestion": "This looks like a code project. Run 'python scripts/scan_project.py .' to initialize."
}
```

扫描器会自动检测:
- 项目类型 (web-frontend, web-backend, full-stack, mobile, etc.)
- 技术栈 (React, Vue, Express, Django, Go, Rust, etc.)
- 开发工具 (npm, Vite, ESLint, Prettier, etc.)
- 代码规范 (从配置文件提取)

确认后,会在项目根目录创建 `.project-ai/` 知识库。

## 核心功能

### 1. 记录 Bug

```bash
# 创建 bug 记录
cat > /tmp/bug.json << 'EOF'
{
  "title": "Payment API timeout",
  "description": "Stripe API calls timing out after 5 seconds",
  "root_cause": "Missing timeout configuration in axios",
  "solution": "Added 30s timeout to axios config",
  "files_changed": ["src/api/payment.ts"],
  "tags": ["api", "timeout", "payment"],
  "severity": "high"
}
EOF

# 记录到知识库
python project-guardian/scripts/update_knowledge.py . --type bug --data /tmp/bug.json
```

### 2. 搜索相似问题

```bash
# 关键词搜索
python project-guardian/scripts/search_similar.py . "timeout payment"

# 标签搜索
python project-guardian/scripts/search_similar.py . --tags api,timeout
```

### 3. 记录需求

```bash
cat > /tmp/req.json << 'EOF'
{
  "title": "WeChat login support",
  "description": "Users should be able to login with WeChat OAuth",
  "status": "planned",
  "priority": "high",
  "related_modules": ["auth", "user"],
  "acceptance_criteria": [
    "WeChat OAuth integration",
    "User profile sync",
    "Existing account linking"
  ],
  "tags": ["authentication", "oauth", "wechat"]
}
EOF

python project-guardian/scripts/update_knowledge.py . --type requirement --data /tmp/req.json
```

### 4. 记录架构决策

```bash
cat > /tmp/decision.json << 'EOF'
{
  "title": "Use PostgreSQL for primary database",
  "context": "Need to choose database for user data and transactions",
  "decision": "Use PostgreSQL as primary database",
  "rationale": "ACID compliance, JSON support, mature ecosystem",
  "consequences": [
    "Positive: Strong consistency guarantees",
    "Negative: More complex setup than SQLite"
  ],
  "alternatives": [
    "MongoDB: Rejected due to lack of transactions"
  ],
  "tags": ["database", "architecture", "postgresql"]
}
EOF

python project-guardian/scripts/update_knowledge.py . --type decision --data /tmp/decision.json
```

## 知识库结构

```
your-project/
├── .project-ai/
│   ├── core/                    # 始终加载 (<2k tokens)
│   │   ├── profile.json        # 项目元数据
│   │   ├── tech-stack.json     # 技术栈
│   │   └── conventions.json    # 代码规范
│   ├── indexed/                 # 按需加载
│   │   ├── architecture.json   # 架构信息
│   │   ├── modules.json        # 模块描述
│   │   ├── tools.json          # 开发工具
│   │   └── structure.json      # 目录结构
│   └── history/                 # 搜索加载
│       ├── bugs/               # Bug 记录
│       ├── requirements/       # 需求记录
│       └── decisions/          # 架构决策
└── [your project files...]
```

## 多项目使用

每个项目的知识库完全独立,互不干扰:

```bash
# 项目 A
cd ~/projects/ecommerce-frontend
python /path/to/project-guardian/scripts/scan_project.py .
# 创建 ~/projects/ecommerce-frontend/.project-ai/

# 项目 B
cd ~/projects/blog-backend
python /path/to/project-guardian/scripts/scan_project.py .
# 创建 ~/projects/blog-backend/.project-ai/
```

## 与 AI 助手集成

Project Guardian 设计用于与 AI 助手 (如 Claude) 配合使用:

```
你: "What's our tech stack?"
AI: [读取 .project-ai/core/tech-stack.json]
    "TypeScript, React 18.2.0, Express 4.18.2"

你: "Have we had timeout issues before?"
AI: [搜索 .project-ai/history/bugs/]
    "Yes, we had a payment API timeout (BUG-xxx).
     Root cause: Missing timeout config.
     Solution: Added 30s timeout to axios."
```

## 团队协作

### 方式 1: 共享核心知识 (推荐)

```bash
# 将核心知识纳入版本控制
git add .project-ai/core/ .project-ai/indexed/
git commit -m "Add project knowledge base"
git push
```

团队成员 clone 后自动获得项目知识。

### 方式 2: 个人知识库

```bash
# 每个人维护自己的知识库
echo ".project-ai/" >> .gitignore
```

## 配置文件模板

### Bug 模板 (`assets/bug-template.json`)

```json
{
  "title": "Brief description",
  "description": "Detailed description and reproduction steps",
  "root_cause": "Why it happened",
  "solution": "How it was fixed",
  "files_changed": ["file1.ts", "file2.ts"],
  "tags": ["category", "type"],
  "severity": "low | medium | high | critical"
}
```

### 需求模板 (`assets/requirement-template.json`)

```json
{
  "title": "Feature name",
  "description": "Detailed description",
  "status": "planned | in-progress | completed | cancelled",
  "priority": "low | medium | high | critical",
  "related_modules": ["module1", "module2"],
  "acceptance_criteria": ["criterion1", "criterion2"],
  "tags": ["category"]
}
```

### 决策模板 (`assets/decision-template.json`)

```json
{
  "title": "Decision title",
  "context": "What problem needs to be solved?",
  "decision": "What did we decide?",
  "rationale": "Why this approach?",
  "consequences": ["Positive: ...", "Negative: ..."],
  "alternatives": ["Alternative 1: why not chosen"],
  "tags": ["category"]
}
```

## 性能指标

- **扫描速度**: 中型项目 ~3 秒
- **搜索速度**: 100 个 bug ~0.5 秒
- **存储空间**: 100 个 bug ~110 KB
- **Token 使用**: 平均 <1.5k tokens/查询

## 支持的项目类型

- ✅ Web Frontend (React, Vue, Angular, etc.)
- ✅ Web Backend (Express, Django, FastAPI, Go, Rust, etc.)
- ✅ Full-stack (Next.js, Nuxt, etc.)
- ✅ Mobile (iOS, Android)
- ✅ Library/Package
- ✅ CLI Tool

## 支持的技术栈

**语言**: TypeScript, JavaScript, Python, Go, Rust, Java

**前端框架**: React, Vue, Angular, Svelte, Next.js, Nuxt

**后端框架**: Express, NestJS, Django, FastAPI, Flask, Spring Boot, Actix Web

**工具**: npm, pnpm, yarn, Vite, Webpack, ESLint, Prettier, Vitest, Jest, Playwright

## 最佳实践

1. ✅ 初始化后确认扫描结果
2. ✅ 修复 bug 后立即记录
3. ✅ 使用一致的标签
4. ✅ 包含根因和解决方案
5. ✅ 定期搜索避免重复
6. ✅ 保持知识库精简 (<50k tokens)

## 故障排除

**扫描器未检测到项目类型**:
```bash
# 手动编辑
vim .project-ai/core/profile.json
# 设置 "project_type": "web-frontend"
```

**搜索无结果**:
- 确保已记录过 bug/需求
- 使用更具体的关键词
- 尝试标签搜索

**知识库过大**:
- 归档旧 bug (>6 个月)
- 删除已完成的需求
- 压缩历史记录

## 文档

- [完整使用指南](SKILL.md)
- [知识库 Schema](references/knowledge-schema.md)
- [多项目数据隔离说明](docs/isolation.md)

## 系统要求

- Python 3.8+
- 无外部依赖 (仅使用标准库)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!

## 作者

Created with ❤️ for better project management

---

**让项目知识管理变得简单、高效、智能!** 🚀
