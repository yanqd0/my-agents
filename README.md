# my-agents

个人 agent 内容源：集中维护我各 agent 宿主使用的 skills、设置片段与扩展，并用一个安装器
一键装到位。当前主目标是 **pi**，未来扩展 **dsh / Codex / OpenCode**。

## 内容

| 目录 | 内容 | 安装去向 |
|------|------|----------|
| `skills/` | 通用 Agent Skills（`SKILL.md` + 参考资料） | `~/.agents/skills/` |
| `settings/pi/` | pi 设置片段 | `~/.pi/agent/settings.json` |
| `settings/pi/model/` | pi 模型定义与价格片段 | `~/.pi/agent/models.json` |
| `install.py` | 多目标安装器（当前 `--target pi`） | — |

## 安装

```bash
./install.py                      # 默认安装到 pi
./install.py --dry-run            # 预览，不落盘
./install.py --force              # 覆盖已有设置键，并启用 `_` 前缀的片段
./install.py uninstall            # 卸载

# 其它宿主（规划中）
./install.py --target dsh
```

模型定义/价格更新需 `--force`（模型 `models` 数组为既有键，默认不覆盖）。

### pi 扩展

pi 的**必要官方扩展**（plan-mode / subagent / question / permission-gate / todo）**不在本仓库收编**，
而是 install 时从**已装 pi 包**自带 examples 动态软链到 `~/.pi/agent/extensions/`。因扩展拥有完整
系统权限，分发默认需确认（交互 y/N；headless 用 `--yes`，或先 `--dry-run` 预览）。T2 第三方插件
（0.2.0）仅提示、不默认装。**升级 pi 后重跑 `./install.py` 即可刷新**到新版本源的扩展。

## 内置 Skills

| Skill | 用途 |
|-------|------|
| my-mermaid | 生成配色合理、分组清晰的 mermaid 图表 |
| my-code-io | 基于代码入口撰写多章节中文技术介绍文（含 mermaid 图） |
| my-image-vision | 图片预处理后调 Vision API 识图 / OCR |
| my-git-commit | 暂存提交，生成规范中文提交信息 |
| my-git-amend | 合并 / 整理 git 提交历史 |
| my-changelog | 维护 CHANGELOG.md 版本条目 |
| my-git-tag | 打语义化版本 tag 并同步 CHANGELOG |
