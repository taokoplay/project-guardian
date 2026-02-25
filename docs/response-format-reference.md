# 响应格式快速参考

## 基本格式

```
[图标] [Project Guardian] <动作描述>

[主要内容]

[可选：完成总结]
```

## 图标含义

| 图标 | 含义 | 使用场景 |
|------|------|----------|
| 🔍 | 检测/扫描 | 检查初始化状态、扫描项目 |
| ✓ | 成功完成 | 操作成功、记录完成 |
| 📚 | 加载数据 | 加载知识库、读取上下文 |
| ⚠️ | 警告/提示 | 发现相似问题、需要注意 |
| 🔎 | 搜索 | 搜索历史记录、查找相似问题 |
| 📝 | 记录 | 记录 bug、需求、决策 |
| ❌ | 错误 | 操作失败、找不到文件 |

## 常用响应模板

### 1. 检查初始化状态

```
🔍 [Project Guardian] 检查项目初始化状态...

项目未初始化。是否扫描并创建知识库？(yes/no)
```

### 2. 扫描项目

```
✓ [Project Guardian] 扫描项目并创建知识库

检测到：
- 项目类型: full-stack
- 技术栈: React 18.2.0, Express 4.18.2
- 工具: pnpm, Vite, ESLint

知识库已创建在 .project-ai/
```

### 3. 记录 Bug

```
✓ [Project Guardian] 记录 bug #BUG-20260225-001

标题: 支付接口超时
严重程度: high
标签: api, timeout, payment

Bug 已保存到知识库，将帮助防止类似问题。
```

### 4. 搜索相似问题

```
🔎 [Project Guardian] 在历史记录中搜索相似问题...

找到 3 个相似问题：

1. #BUG-20260215-001 - Payment API timeout (相似度: 95%)
   解决方案: 添加 30s 超时配置

2. #BUG-20260210-003 - Stripe webhook timeout (相似度: 78%)
   解决方案: 使用异步处理

3. #BUG-20260201-005 - API rate limiting (相似度: 65%)
   解决方案: 添加重试机制
```

### 5. 加载项目上下文

```
📚 [Project Guardian] 加载项目知识库...

项目: my-awesome-app
类型: full-stack
技术栈: React + Express
上次更新: 2026-02-25

[继续回答用户问题...]
```

### 6. 发现相似问题（警告）

```
⚠️ [Project Guardian] 发现相似的历史问题

Bug: Payment API timeout (2024-02-15)
根本原因: 缺少超时配置
解决方案: 在 axios 配置中添加 30s 超时

建议应用相同的修复方案以避免此问题。
```

### 7. 记录需求

```
✓ [Project Guardian] 记录需求 #REQ-20260225-001

标题: 微信登录支持
优先级: high
状态: planned
相关模块: auth, user

需求已保存到知识库。
```

### 8. 记录架构决策

```
✓ [Project Guardian] 记录架构决策 #ADR-20260225-001

标题: 使用 PostgreSQL 替代 MongoDB
状态: accepted
影响: database, api, models

决策已记录到知识库。
```

### 9. 未找到相似问题

```
🔎 [Project Guardian] 搜索历史记录...

未找到相似问题。这可能是一个新问题。

建议在解决后记录到知识库，以便将来参考。
```

### 10. 错误情况

```
❌ [Project Guardian] 操作失败

错误: 找不到 .project-ai/ 目录
建议: 请先运行项目扫描初始化知识库

运行: python scripts/scan_project.py .
```

## 多步骤操作

对于需要多个步骤的操作，使用进度指示：

```
🔍 [Project Guardian] 扫描项目...

✓ 检测项目类型: full-stack
✓ 分析技术栈: React, Express, TypeScript
✓ 扫描开发工具: pnpm, Vite, ESLint
✓ 提取代码规范: ESLint, Prettier 配置
✓ 创建知识库结构

扫描完成！知识库已创建在 .project-ai/
```

## 简洁模式

对于简单操作，可以使用更简洁的格式：

```
✓ [Project Guardian] Bug #BUG-20260225-001 已记录
```

```
📚 [Project Guardian] 已加载项目上下文
```

```
🔎 [Project Guardian] 找到 3 个相似问题
```

## 注意事项

1. **始终包含 skill 名称**：让用户知道是哪个 skill 在工作
2. **使用合适的图标**：快速传达操作类型
3. **保持简洁**：状态指示应该简短明了
4. **提供上下文**：包含关键信息（ID、标题、状态等）
5. **给出建议**：在适当时候提供下一步操作建议

## 中英文对照

| 中文 | English |
|------|---------|
| 检查项目初始化状态 | Checking project initialization status |
| 扫描项目并创建知识库 | Scanning project and creating knowledge base |
| 记录 bug | Recording bug |
| 搜索相似问题 | Searching for similar issues |
| 加载项目知识库 | Loading project knowledge base |
| 发现相似的历史问题 | Found similar historical issue |
| 记录需求 | Recording requirement |
| 记录架构决策 | Recording architecture decision |
| 未找到相似问题 | No similar issues found |
| 操作失败 | Operation failed |
