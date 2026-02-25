# Project Guardian Skill - 版本更新指南

## 📋 版本更新流程

### 完整流程概览

```
1. 修改代码/文档
2. 更新 CHANGELOG.md
3. 提交到 Git
4. 创建版本标签
5. 推送到 GitHub
6. 创建 GitHub Release
7. 更新本地 Skill
8. 重新打包 Skill
```

---

## 🔄 详细步骤

### 步骤 1: 修改代码或文档

```bash
cd /path/to/project-guardian

# 修改文件
vim scripts/scan_project.py
vim SKILL.md
# ... 进行你的修改
```

### 步骤 2: 更新 CHANGELOG.md

```bash
vim CHANGELOG.md
```

添加新版本信息:

```markdown
## [1.1.0] - 2026-02-25

### Added
- 新功能描述
- 另一个新功能

### Changed
- 修改的内容

### Fixed
- 修复的 bug

### Deprecated
- 即将废弃的功能
```

### 步骤 3: 提交到 Git

```bash
# 查看修改
git status
git diff

# 添加文件
git add .

# 提交 (使用语义化提交信息)
git commit -m "feat: add new feature

- Detailed description of changes
- Another change
- Breaking changes if any"

# 或者
git commit -m "fix: resolve bug in scanner"
git commit -m "docs: update installation guide"
git commit -m "refactor: improve search algorithm"
```

### 步骤 4: 创建版本标签

```bash
# 创建标签 (使用语义化版本号)
git tag -a v1.1.0 -m "Release version 1.1.0

New Features:
- Feature 1
- Feature 2

Bug Fixes:
- Fix 1
- Fix 2"

# 查看标签
git tag -l
```

### 步骤 5: 推送到 GitHub

```bash
# 推送代码
git push origin main

# 推送标签
git push origin v1.1.0

# 或一次性推送所有标签
git push origin --tags
```

### 步骤 6: 创建 GitHub Release

**方式 1: 通过 GitHub 网页**

1. 访问 https://github.com/taokoplay/project-guardian-skill/releases/new
2. 选择标签: `v1.1.0`
3. Release title: `Project Guardian v1.1.0`
4. 描述: 复制 CHANGELOG.md 中的内容
5. 点击 "Publish release"

**方式 2: 使用 GitHub CLI**

```bash
gh release create v1.1.0 \
  --title "Project Guardian v1.1.0" \
  --notes "$(cat CHANGELOG.md | sed -n '/## \[1.1.0\]/,/## \[/p' | head -n -1)"
```

### 步骤 7: 更新本地 Skill

如果你在 Claude Code 的 workspace 中使用这个 skill:

```bash
# 复制更新后的文件到 skills 目录
cp -r /path/to/project-guardian/* \
  /Users/xutaoyu/.craft-agent/workspaces/my-workspace/skills/project-guardian/
```

### 步骤 8: 重新打包 Skill

```bash
cd /Users/xutaoyu/.craft-agent/workspaces/my-workspace/skills

# 重新打包
python skill-creator/scripts/package_skill.py project-guardian

# 验证
ls -lh project-guardian.skill
```

---

## 📦 快速更新脚本

创建一个自动化脚本 `release.sh`:

```bash
#!/bin/bash
# Project Guardian Release Script

set -e

# 检查参数
if [ -z "$1" ]; then
    echo "Usage: ./release.sh <version>"
    echo "Example: ./release.sh 1.1.0"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo "🚀 Releasing Project Guardian $TAG"
echo ""

# 1. 检查工作目录是否干净
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Working directory is not clean. Commit or stash changes first."
    exit 1
fi

# 2. 确认 CHANGELOG 已更新
echo "📝 Have you updated CHANGELOG.md? (y/n)"
read -r response
if [ "$response" != "y" ]; then
    echo "❌ Please update CHANGELOG.md first"
    exit 1
fi

# 3. 创建标签
echo "🏷️  Creating tag $TAG..."
git tag -a "$TAG" -m "Release version $VERSION"

# 4. 推送
echo "📤 Pushing to GitHub..."
git push origin main
git push origin "$TAG"

# 5. 更新本地 skill
echo "📦 Updating local skill..."
SKILL_DIR="/Users/xutaoyu/.craft-agent/workspaces/my-workspace/skills/project-guardian"
if [ -d "$SKILL_DIR" ]; then
    cp -r ./* "$SKILL_DIR/"
    cd /Users/xutaoyu/.craft-agent/workspaces/my-workspace/skills
    python skill-creator/scripts/package_skill.py project-guardian
fi

echo ""
echo "✅ Release $TAG completed!"
echo ""
echo "📋 Next steps:"
echo "1. Create GitHub Release: https://github.com/taokoplay/project-guardian-skill/releases/new"
echo "2. Select tag: $TAG"
echo "3. Copy CHANGELOG content"
echo "4. Publish release"
```

使用方法:

```bash
chmod +x release.sh
./release.sh 1.1.0
```

---

## 🔢 语义化版本号规则

遵循 [Semantic Versioning 2.0.0](https://semver.org/):

**格式**: `MAJOR.MINOR.PATCH`

- **MAJOR** (主版本号): 不兼容的 API 修改
  - 例: `1.0.0` → `2.0.0`
  - 场景: 重大重构、破坏性变更

- **MINOR** (次版本号): 向后兼容的功能新增
  - 例: `1.0.0` → `1.1.0`
  - 场景: 新功能、新特性

- **PATCH** (修订号): 向后兼容的 bug 修复
  - 例: `1.0.0` → `1.0.1`
  - 场景: bug 修复、小改进

### 示例

```bash
# Bug 修复
v1.0.0 → v1.0.1

# 新功能
v1.0.1 → v1.1.0

# 破坏性变更
v1.1.0 → v2.0.0
```

---

## 📝 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/):

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式 (不影响功能)
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```bash
# 新功能
git commit -m "feat(scanner): add support for Rust projects"

# Bug 修复
git commit -m "fix(search): resolve similarity calculation error"

# 文档
git commit -m "docs: update installation guide with troubleshooting"

# 破坏性变更
git commit -m "feat(api): change knowledge base structure

BREAKING CHANGE: Knowledge base format has changed.
Users need to re-scan their projects."
```

---

## 🔄 用户如何更新

### 方式 1: Git Pull (全局安装)

```bash
cd ~/tools/project-guardian
git pull origin main
```

### 方式 2: Git Submodule Update (项目内安装)

```bash
cd ~/projects/my-project
git submodule update --remote .guardian
git add .guardian
git commit -m "Update Project Guardian to v1.1.0"
```

### 方式 3: 重新克隆

```bash
cd ~/tools
rm -rf project-guardian
git clone https://github.com/taokoplay/project-guardian-skill.git
```

### 方式 4: 下载特定版本

```bash
curl -L https://github.com/taokoplay/project-guardian-skill/archive/refs/tags/v1.1.0.tar.gz -o pg-1.1.0.tar.gz
tar -xzf pg-1.1.0.tar.gz
```

---

## 📊 版本管理最佳实践

### 1. 保持 CHANGELOG 更新

每次修改都要更新 CHANGELOG.md:

```markdown
## [Unreleased]

### Added
- 新功能 (还未发布)

### Changed
- 修改的内容

## [1.1.0] - 2026-02-25

### Added
- 已发布的功能
```

### 2. 使用分支管理

```bash
# 开发新功能
git checkout -b feature/new-scanner
# ... 开发
git commit -m "feat: add new scanner"

# 合并到 main
git checkout main
git merge feature/new-scanner

# 发布
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin main --tags
```

### 3. 测试后再发布

```bash
# 在测试项目上验证
cd /tmp/test-project
python /path/to/project-guardian/scripts/scan_project.py .

# 确认无误后再打标签
```

### 4. 保持向后兼容

- 尽量避免破坏性变更
- 如果必须破坏兼容性,增加 MAJOR 版本号
- 在 CHANGELOG 中明确标注 `BREAKING CHANGE`

### 5. 文档同步更新

- README.md
- SKILL.md
- docs/ 目录下的文档
- 代码注释

---

## 🎯 实际示例

### 示例 1: 修复 Bug (v1.0.0 → v1.0.1)

```bash
# 1. 修复 bug
vim scripts/scan_project.py

# 2. 更新 CHANGELOG
vim CHANGELOG.md
# 添加:
# ## [1.0.1] - 2026-02-26
# ### Fixed
# - Fix scanner crash on empty package.json

# 3. 提交
git add .
git commit -m "fix(scanner): handle empty package.json gracefully"

# 4. 创建标签
git tag -a v1.0.1 -m "Release v1.0.1: Bug fixes"

# 5. 推送
git push origin main
git push origin v1.0.1

# 6. 更新本地 skill
cp -r . /Users/xutaoyu/.craft-agent/workspaces/my-workspace/skills/project-guardian/
cd /Users/xutaoyu/.craft-agent/workspaces/my-workspace/skills
python skill-creator/scripts/package_skill.py project-guardian
```

### 示例 2: 添加新功能 (v1.0.1 → v1.1.0)

```bash
# 1. 开发新功能
git checkout -b feature/compression
vim scripts/compress_history.py
# ... 实现压缩功能

# 2. 更新文档
vim SKILL.md
vim README.md

# 3. 更新 CHANGELOG
vim CHANGELOG.md
# 添加:
# ## [1.1.0] - 2026-02-27
# ### Added
# - History compression script to reduce knowledge base size

# 4. 提交
git add .
git commit -m "feat(compression): add history compression script

- Compress old bug records
- Merge similar issues
- Reduce token usage by 60%"

# 5. 合并到 main
git checkout main
git merge feature/compression

# 6. 创建标签
git tag -a v1.1.0 -m "Release v1.1.0: History compression"

# 7. 推送
git push origin main
git push origin v1.1.0

# 8. 创建 GitHub Release
gh release create v1.1.0 --title "v1.1.0: History Compression" --notes "See CHANGELOG.md"

# 9. 更新本地 skill
./release.sh 1.1.0
```

---

## 🔍 版本检查

### 查看当前版本

```bash
# 查看最新标签
git describe --tags --abbrev=0

# 查看所有版本
git tag -l

# 查看版本详情
git show v1.0.0
```

### 比较版本差异

```bash
# 比较两个版本
git diff v1.0.0 v1.1.0

# 查看版本间的提交
git log v1.0.0..v1.1.0 --oneline
```

---

## 📢 通知用户更新

### 在 README.md 中添加版本信息

```markdown
## Latest Version

**Current**: v1.1.0 (2026-02-27)

### What's New
- History compression
- Performance improvements
- Bug fixes

[View Changelog](CHANGELOG.md) | [Download](https://github.com/taokoplay/project-guardian-skill/releases/latest)
```

### 在 GitHub Release 中说明

```markdown
## 🎉 What's New in v1.1.0

### ✨ New Features
- **History Compression**: Reduce knowledge base size by 60%
- **Performance**: Faster search with improved indexing

### 🐛 Bug Fixes
- Fixed scanner crash on empty files
- Resolved encoding issues

### 📚 Documentation
- Updated installation guide
- Added troubleshooting section

## 📥 Installation

\`\`\`bash
git clone https://github.com/taokoplay/project-guardian-skill.git
cd project-guardian
./install.sh /path/to/your/project
\`\`\`

## 🔄 Upgrading

\`\`\`bash
cd ~/tools/project-guardian
git pull origin main
\`\`\`

Full Changelog: [v1.0.0...v1.1.0](https://github.com/taokoplay/project-guardian-skill/compare/v1.0.0...v1.1.0)
```

---

## ✅ 版本更新检查清单

发布前确认:

- [ ] 代码已测试
- [ ] CHANGELOG.md 已更新
- [ ] README.md 版本号已更新
- [ ] 文档已同步
- [ ] 所有测试通过
- [ ] 提交信息规范
- [ ] 版本号符合语义化规范
- [ ] 标签已创建
- [ ] 代码已推送到 GitHub
- [ ] 标签已推送到 GitHub
- [ ] GitHub Release 已创建
- [ ] 本地 skill 已更新
- [ ] Skill 包已重新打包

---

## 🎓 总结

**简化版流程** (日常使用):

```bash
# 1. 修改代码
vim scripts/scan_project.py

# 2. 提交
git add .
git commit -m "feat: add new feature"

# 3. 发布
./release.sh 1.1.0

# 4. 创建 GitHub Release (手动)
```

**完整版流程** (重要版本):

1. 创建功能分支
2. 开发和测试
3. 更新文档
4. 更新 CHANGELOG
5. 合并到 main
6. 创建标签
7. 推送到 GitHub
8. 创建 GitHub Release
9. 更新本地 skill
10. 通知用户

---

**记住**: 版本管理的核心是**清晰的沟通**和**可追溯的历史**! 📝
