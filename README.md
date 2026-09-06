# my-agents

个人 agent 内容源：集中维护我各 agent 宿主使用的 skills、设置片段与扩展，并用一个安装器
一键装到位。已支持 **pi**、**dsh**（skills），未来扩展 **Codex / OpenCode**。

## 内容

| 目录 | 内容 | 安装去向 |
|------|------|----------|
| `skills/` | pi/跨宿主 Agent Skills（`SKILL.md` + 参考资料；中性参考软链自 submodule） | `~/.agents/skills/` |
| `settings/pi/` | pi 设置片段 | `~/.pi/agent/settings.json` |
| `settings/pi/model/` | pi 模型定义与价格片段 | `~/.pi/agent/models.json` |
| `vendor/my-claude/` | my-claude git submodule（上游内容源，仅 Claude Code 用） | — |
| `install.py` | 多目标安装器（`--target pi` / `--target dsh`） | — |

> `skills/` 中与上游 my-claude 一致的中性参考资料/脚本为软链（指向 `vendor/my-claude`），
> 只维护一份；`SKILL.md` 与 pi 专属差异文件在本地维护。共享内容改到 my-claude 上游仓库即可。

## 安装

```bash
./install.py                      # 默认安装到 pi
./install.py --dry-run            # 预览，不落盘
./install.py --force              # 覆盖已有设置键，并启用 `_` 前缀的片段
./install.py --revert             # 卸载

# 其它宿主
./install.py --target dsh              # dsh：装 skills 到 ~/.agents/skills + web profile 插件
./install.py --target dsh --update     # 重复执行：补装缺失插件，并把已装插件升到上游最新
```

dsh 的 `--target dsh` **装 skills 到 `~/.agents/skills`**（与 pi 共用；dsh 自动发现），并按
`install.py` 中 `DSH_PLUGINS_BY_PROFILE` 的清单把 **dsh 第三方插件**经 `dsh plugin --profile web
add` 装入 **web profile**（当前 4 个：dshmarket / dsh-whale-widget / graph-memory /
dsh-calculator）。缺装项每次重跑自动补装（幂等），**安装源按序候选**：优先 npm registry 名，
其次 `github:`（https clone），git 不通时自动退到 codeload https tarball（保持 https，勿改
SSH）。已装项重跑时做**更新检查**（registry 与 GitHub HEAD 版本对比），发现新版本默认仅报告，
加 `--update` 才实际升级；`--revert` 一并卸载。
首次装 dsh-calculator 前需把 `~/.dsh/profiles/web/pnpm-workspace.yaml` 的 `autoInstallPeers`
改为 `false`（dsh initProfile 默认值；否则其 `@deepseek-ai/dsh-*@^0.0.1` peer 无正式版会卡住
安装）。
评估与逐插件说明见 `notes/dsh/plugin-selection-web.md`。dsh 的模型/cost 由 provider 插件管理、
设置是个人 `~/.dsh/settings.yaml`，无 pi 式 `settings/models` 片段可合并，故 dsh 不装
settings/models/extensions（机制见 `notes/dsh/skills-settings-loading.md`）。

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
