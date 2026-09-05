# my-agents

面向 `~/.agents`（以及各 host 专属位置）的个人 agent 内容源项目，参照
[`../my-claude/`](../my-claude/)（目标 `~/.claude`）建设，但服务对象是 **跨多个 agent
宿主**：当前以 **pi**（主）、**dsh** 为安装目标，未来扩展 **Codex / OpenCode**。

> 与 my-claude 的差异：内容不写死在某一宿主目录语义下，而是以「通用 Agent Skills +
> 每宿主专属片段 + 多目标安装器」组织；`AGENTS.md` 说明本项目结构，配合 `install.py`
> 把内容安装到目标 host 的 `~/.agents/skills` 等位置。

## 目录结构

- `AGENTS.md` — 本项目规范（本文件），安装/开发前必读
- `install.py` — 多目标安装器：`--target pi|dsh`，负责软链 skills、deep-merge settings 等
- `skills/<name>/` — **通用** skill 源（含 `SKILL.md` + 可选 `references/`/`scripts/`），
  统一按 Agent Skills 规范组织，作为 pi / dsh / codex 共享的 `~/.agents/skills` 来源
- `settings/<host>/` — 每宿主专属 settings 片段（如 `settings/pi/*.json` → 合并进
  `~/.pi/agent/settings.json`）
- `README.md` — 对外说明（新增/删除/改名/功能变更后同步更新）

## 安装机制（install.py）

- **skills**：`skills/*`（目录）软链到目标 host 的 skills 目录
  - pi 读 `~/.agents/skills/`（含 `SKILL.md` 的目录被递归发现）；`~/.agents` 是宿主无关的
    共享位置，dsh/codex 未来亦从此读取（按 Agent Skills 标准）
  - 目标 skills 目录：`~/.agents/skills/`
- **settings**：`settings/<host>/*.json` deep-merge 到该 host 的 settings 文件
  - pi → `~/.pi/agent/settings.json`；dsh → （0.2.0 调研后确定）
- 提供 install / uninstall / dry-run / `_` 前缀默认跳过等能力，语义对齐 my-claude 的
  `install.py`，但去掉 Claude Code 专属的 commands/hooks/agents/mcp 部分（pi 无对应结构）。

## 迁移原则（来自 my-claude 内容时）

1. **择取（不是全搬）**：逐项评估「该 host 是否真的需要」。pi 无 Claude Code 的
   `commands`/`hooks`/`agents`/`AskUserQuestion`/`mem-lite`/`CLAUDE.md` 等结构，凡深度绑定
   这些的片段必须**裁剪或重写**而非照搬。my-claude 的 `my-new-agent`（产出 `.claude/agents/`）、
   code-reviewer/security-auditor 自动派出等 0.1.0 不迁移。
2. **通用规范**：skill 一律用 Agent Skills 标准（`SKILL.md` + frontmatter），宿主差异
   尽量下沉到内容里避免。跨 host 才保留；单 host 专才放 `settings/<host>`。
3. **最小 token / 最准确语言**：只留能让该宿主完成任务的最短步骤；references 仅在
   「条件触发 / 冷启动 / 大体积」时拆分；删掉宿主专属样板（host 识别表、交互引导、
   AskUserQuestion 规范等在本项目无必要或需替换）。
4. **针对 pi 重写点**：识别宿主（不再需要 Claude 的多宿主表）→ 删除；`references/agent/*`
   （claude/codex/opencode/dsh）不迁移；交互（如需）换成 pi 能力或纯文本澄清；
   版本/提交/skill 创建类流程泛化到「当前宿主」，不写死某一宿主命令。
5. **README 同步**：任何目录增删改后，先更新本项目 `README.md` 相关表格/说明，再提交，
   合并为一次 commit。
6. **反问(AskUserQuestion)跨宿主适配**：宿主不一定把反问暴露成模型 tool（pi 需装
   `question`/`ask_user_question` 这类 extension 才有）。凡依赖交互的 skill：
   - frontmatter `allowed-tools` 的宿主问询 tool 名，按目标宿主改写（pi=`question`/
     `ask_user_question`，且要求该 extension 已装）；不写死某宿主独有 tool。
   - skill 正文把交互点写成**统一动作名**（如"反问 ask 用户二选一…"），由各宿主 adapter
     层映射到本宿主 tool；正文不依赖某一宿主 UI 原语。
   - 无 UI/headless（pi `-p`/rpc 等）下问询原语为 no-op：交互点必须写明"退化为纯文本
     陈述等用户文字回答"，避免卡死。
   - 实现参考：`notes/pi-extension-plugin-selection.md` 的「反问的跨宿主适配」。

## 路线图

- **0.1.0（当前）— pi 主目标，迁移 skills + settings**
  - 结构搭建：`skills/`、`settings/pi/`、`install.py`（pi 目标）
  - skills 迁移（择取 + 针对 pi 重写）与 settings（首版基于 pi）
  - 完成后：重指 `~/.agents/skills` 软链到本项目的 `skills/`，清掉对 my-claude 的重复引用
- **0.2.0 — 支持 dsh + 更复杂内容**
  - 调研 dsh 的 profile/plugin（cordis/dsh-agent-instructions 等）加载 skills 的机制，
    确定 skills/settings 落到何处
  - 迁移/重写需更复杂适配的内容（hooks 等价物、更深 skill）
- **未来 — Codex / OpenCode**：复用 `~/.agents` + Agent Skills 标准，仅补各自 settings 片段

## 开发流程（mint）

本项目 issue/计划/里程碑用 mint 管理（见 `~/.agents/skills/mint`）。跨宿主需求、计划以
`0.1.0` / `0.2.0` 里程碑组织；每个安装目标、每类内容（skills/settings/installer）拆独立
issue 跟踪。
