# my-agents

面向 `~/.agents`（及各宿主专属位置）的个人 agent 内容源项目，参照
[`my-claude/`](../my-claude/)（目标 `~/.claude`）建设。当前以 **pi** 为主目标，
未来扩展 **dsh / Codex / OpenCode**。开发与迁移规范见 `AGENTS.md`。

## 内容目录

| 目录 | 内容 | 安装去向 |
|------|------|----------|
| `skills/` | 通用 Agent Skills（`SKILL.md` + `references/`），按 Agent Skills 标准组织 | `~/.agents/skills/`（软链） |
| `settings/pi/` | pi 设置片段（`.json`），deep-merge 到宿主 settings | `~/.pi/agent/settings.json` |
| `install.py` | 多目标安装器（`--target pi`，dsh 待补） | — |
| `notes/` | 技术选型/设计记录 | — |

## 安装

```bash
# 安装到 pi（软链 skills 到 ~/.agents/skills，merge settings 到 ~/.pi/agent/settings.json）
./install.py                      # 默认 --target pi install
./install.py --dry-run            # 预览不落盘
./install.py --force              # 覆盖已有 settings 键 + 启用 `_` 前缀文件

# 卸载
./install.py uninstall

# 其他宿主（0.2.0+）
./install.py --target dsh
```

`settings/*/_xxx.json` 这类 `_` 前缀片段默认跳过，用 `--force` 显式安装。

## Skills（0.1.0，pi 首版迁移中）

| Skill | 用途 | 状态 |
|-------|------|------|
| my-mermaid | 生成色彩合理、分组清晰的 mermaid 图 | 迁移中 |
| my-git-commit | 暂存提交，规范中文提交信息 | 迁移中 |
| my-git-amend | 合并/整理提交 | 迁移中 |
| my-changelog | 维护 CHANGELOG.md | 迁移中 |
| my-git-tag | 打语义化版本 tag | 迁移中 |
| my-code-io | 基于代码生成中文技术介绍文 | 迁移中 |
| my-image-vision | 图片预处理 + Vision API 识图 | 迁移中 |
| my-new-agent | 项目级 agent 定义 | 待评估(0.2.0) |

新增/删除/改动内容后，需同步更新本表后再提交。
