# 智能初始化示例

## 场景一：自动检测并提示初始化

**用户在未初始化的项目中提问：**

```
用户: 这个项目的认证流程是怎么工作的？
```

**Claude 的智能响应：**

```
🔍 我注意到这个项目还没有初始化知识库。

是否需要我扫描并初始化 Project Guardian？这将：
- 自动检测你的技术栈和工具
- 学习代码规范和架构
- 启用智能 bug 追踪和防重复
- 大约需要 10 秒钟

是否继续扫描？(yes/no)
```

**用户确认后：**

```
用户: yes

Claude:
✓ 正在扫描项目...
✓ 检测到 React + TypeScript + Express 全栈项目
✓ 发现 ESLint, Prettier, Vitest 配置
✓ 知识库已创建在 .project-ai/

现在让我回答你的问题：

根据扫描结果，这个项目使用 JWT 认证...
```

---

## 场景二：询问项目结构

**用户：**
```
这个项目的目录结构是怎样的？
```

**Claude（自动检测）：**
```
🔍 检测到这是一个代码项目，但还没有知识库。

我可以先扫描项目来了解结构，这样能给你更准确的答案。是否初始化？(yes/no)
```

---

## 场景三：记录 Bug 时自动初始化

**用户：**
```
记录一个 bug：支付接口超时
```

**Claude：**
```
🔍 要记录 bug 需要先初始化项目知识库。

是否扫描项目并创建知识库？(yes/no)
```

---

## 场景四：已初始化项目（无提示）

**用户：**
```
认证流程是怎么工作的？
```

**Claude（直接回答，无初始化提示）：**
```
✓ 加载项目知识库...

根据项目配置，认证流程如下：

1. 用户登录 → POST /api/auth/login
2. 服务器验证凭证 → 生成 JWT token
3. Token 存储在 localStorage
4. 后续请求携带 Authorization header
...
```

---

## 触发智能检测的问题类型

### ✅ 会触发检测的问题：

1. **架构相关**
   - "这个项目的认证流程是怎么工作的？"
   - "数据库连接在哪里配置？"
   - "API 路由是如何组织的？"

2. **规范相关**
   - "这个项目的命名规范是什么？"
   - "我应该怎么组织组件结构？"
   - "代码风格有什么要求？"

3. **Bug/需求追踪**
   - "记录这个 bug"
   - "保存这个需求"
   - "之前遇到过类似问题吗？"

4. **项目探索**
   - "这个项目用了什么技术栈？"
   - "有哪些开发工具？"
   - "项目结构是怎样的？"

### ❌ 不会触发检测的问题：

1. **通用编程问题**
   - "如何在 React 中使用 useState？"
   - "Python 的装饰器怎么用？"
   - "什么是闭包？"

2. **非项目上下文**
   - "帮我写一个排序算法"
   - "解释一下 SOLID 原则"
   - "推荐一些学习资源"

---

## 手动检查初始化状态

```bash
# 检查当前项目是否已初始化
python scripts/check_initialized.py

# 检查指定项目
python scripts/check_initialized.py /path/to/project
```

**输出示例（已初始化）：**
```json
{
  "initialized": true,
  "project_root": "/Users/dev/my-app",
  "knowledge_base_path": "/Users/dev/my-app/.project-ai",
  "core_files": {
    "profile.json": true,
    "tech-stack.json": true,
    "conventions.json": true
  },
  "indexed_files": {
    "architecture.json": true,
    "modules.json": true,
    "tools.json": true,
    "structure.json": true
  },
  "history_dirs": {
    "bugs": true,
    "requirements": true,
    "decisions": true
  },
  "warnings": []
}
```

**输出示例（未初始化）：**
```json
{
  "initialized": false,
  "current_path": "/Users/dev/my-app",
  "is_likely_project": true,
  "suggestion": "This looks like a code project. Run 'python scripts/scan_project.py .' to initialize."
}
```

---

## 优势

### 传统方式（手动初始化）
```
用户: 扫描项目
Claude: ✓ 扫描完成

用户: 认证流程是怎么工作的？
Claude: [回答问题]
```
**需要 2 步**

### 智能方式（自动检测）
```
用户: 认证流程是怎么工作的？
Claude: 🔍 需要初始化，是否继续？
用户: yes
Claude: ✓ 扫描完成，[回答问题]
```
**只需 1 步，更自然**

---

## 配置

智能检测默认启用，无需配置。

如果你想禁用自动提示，可以在 SKILL.md 中修改 `description` 字段，移除自动检测相关的触发词。
