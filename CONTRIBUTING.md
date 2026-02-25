# Contributing to Project Guardian

感谢你考虑为 Project Guardian 做贡献!

## 如何贡献

### 报告 Bug

如果你发现了 bug,请创建一个 Issue 并包含:
- 清晰的标题和描述
- 重现步骤
- 预期行为 vs 实际行为
- 你的环境信息 (OS, Python 版本)
- 相关的错误日志

### 提出新功能

如果你有新功能的想法:
1. 先创建一个 Issue 讨论
2. 说明功能的用途和价值
3. 如果可能,提供使用示例

### 提交代码

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的改动 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建一个 Pull Request

### 代码规范

- 使用 Python 3.8+ 特性
- 遵循 PEP 8 代码风格
- 添加必要的注释和文档字符串
- 保持代码简洁易读

### 测试

在提交 PR 前,请确保:
- 代码能正常运行
- 没有引入新的 bug
- 更新了相关文档

### 文档

如果你的改动影响了用户使用方式:
- 更新 README.md
- 更新 SKILL.md
- 添加示例代码

## 开发设置

```bash
# 克隆仓库
git clone https://github.com/taokoplay/project-guardian-skill.git
cd project-guardian

# 创建测试项目
mkdir test-project
cd test-project
echo '{"name":"test","dependencies":{"react":"^18.0.0"}}' > package.json

# 测试扫描
python ../scripts/scan_project.py .
```

## 提交信息规范

使用清晰的提交信息:
- `feat: 添加新功能`
- `fix: 修复 bug`
- `docs: 更新文档`
- `refactor: 重构代码`
- `test: 添加测试`
- `chore: 其他改动`

## 问题?

如有任何问题,欢迎创建 Issue 或发起讨论!

感谢你的贡献! ❤️
