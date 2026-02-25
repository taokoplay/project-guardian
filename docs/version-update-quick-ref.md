# Project Guardian Skill - 版本更新快速参考

## 🚀 快速发布 (推荐)

```bash
# 1. 修改代码
vim scripts/scan_project.py

# 2. 更新 CHANGELOG.md
vim CHANGELOG.md

# 3. 提交
git add .
git commit -m "feat: add new feature"

# 4. 运行发布脚本
./release.sh 1.1.0 ghp_YOUR_TOKEN

# 5. 创建 GitHub Release (手动)
# 访问: https://github.com/taokoplay/project-guardian-skill/releases/new
```

## 📋 版本号规则

| 类型 | 版本变化 | 示例 | 场景 |
|------|---------|------|------|
| **MAJOR** | 不兼容变更 | 1.0.0 → 2.0.0 | 破坏性变更 |
| **MINOR** | 新功能 | 1.0.0 → 1.1.0 | 添加新特性 |
| **PATCH** | Bug 修复 | 1.0.0 → 1.0.1 | 修复问题 |

## 📝 提交信息模板

```bash
# 新功能
git commit -m "feat(scope): add feature description"

# Bug 修复
git commit -m "fix(scope): resolve bug description"

# 文档
git commit -m "docs: update documentation"

# 重构
git commit -m "refactor(scope): improve code structure"

# 性能
git commit -m "perf(scope): optimize performance"

# 测试
git commit -m "test: add test cases"

# 构建
git commit -m "chore: update build process"
```

## 🔄 用户更新方式

### 全局安装
```bash
cd ~/tools/project-guardian
git pull origin main
```

### Git Submodule
```bash
cd ~/projects/my-project
git submodule update --remote .guardian
```

### 重新克隆
```bash
git clone https://github.com/taokoplay/project-guardian-skill.git
```

## 📊 CHANGELOG.md 模板

```markdown
# Changelog

## [Unreleased]

### Added
- 新功能 (未发布)

### Changed
- 修改内容

### Fixed
- Bug 修复

## [1.1.0] - 2026-02-27

### Added
- 新功能描述
- 另一个新功能

### Changed
- 修改的内容

### Fixed
- 修复的 bug

### Deprecated
- 即将废弃的功能

### Removed
- 已移除的功能

### Security
- 安全相关更新
```

## 🎯 发布检查清单

发布前确认:

- [ ] 代码已测试
- [ ] CHANGELOG.md 已更新
- [ ] 版本号正确
- [ ] 提交信息规范
- [ ] 所有文件已提交
- [ ] 工作目录干净

发布后确认:

- [ ] 代码已推送
- [ ] 标签已推送
- [ ] GitHub Release 已创建
- [ ] 本地 skill 已更新

## 🛠️ 常用命令

```bash
# 查看当前版本
git describe --tags --abbrev=0

# 查看所有版本
git tag -l

# 查看版本详情
git show v1.0.0

# 比较版本
git diff v1.0.0 v1.1.0

# 查看版本间提交
git log v1.0.0..v1.1.0 --oneline

# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0
```

## 🔧 release.sh 使用

```bash
# 基本用法
./release.sh 1.1.0

# 使用 token (避免手动认证)
./release.sh 1.1.0 ghp_YOUR_TOKEN

# 脚本会自动:
# 1. 检查工作目录
# 2. 验证 CHANGELOG
# 3. 创建标签
# 4. 推送到 GitHub
# 5. 更新本地 skill
# 6. 显示后续步骤
```

## 📚 相关文档

- [完整版本更新指南](skill-version-update-guide.md)
- [CHANGELOG.md](../project-guardian/CHANGELOG.md)
- [GitHub Releases](https://github.com/taokoplay/project-guardian-skill/releases)

---

**记住**: 保持版本号语义化,CHANGELOG 清晰,提交信息规范! 📝
