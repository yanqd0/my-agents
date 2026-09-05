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
- `settings/<host>/` — 每宿主专属片段：顶层 `settings/pi/*.json` → 合并进
  `~/.pi/agent/settings.json`；`settings/pi/model/*.json` → 合并进
  `~/.pi/agent/models.json`（模型定义 + 价格）
- `tools/pi-examples.sh` — 定位**已装 pi 包**自带官方 example extensions 目录（供 install.py 扩展步使用）
- 注：pi 的 **官方 example extensions 不在本仓库收编**，由 install.py 安装时从已装 pi 包动态软链（见下）
- `notes/` — **特殊项目文档**（给 AI/内部开发）：技术选型/设计/现状等决策记录，非交付内容，
  不写入 `README.md`。全部经 `notes/MEMORY.md` 索引（见下），新增/改动任一 notes 文件须同步更新索引
- `notes/MEMORY.md` — **notes 内容索引（项目记忆）**：登记 notes 下每份文档的主题与定位，便于检索
- `README.md` — **给人看的**对外说明（面向用户，不介绍 AGENTS.md/notes 等 AI 内部内容；
  未来若需人看的深文档再另建 `docs/`）

## 安装机制（install.py）

- **skills**：`skills/*`（目录）软链到目标 host 的 skills 目录
  - pi 读 `~/.agents/skills/`（含 `SKILL.md` 的目录被递归发现）；`~/.agents` 是宿主无关的
    共享位置，dsh/codex 未来亦从此读取（按 Agent Skills 标准）
  - 目标 skills 目录：`~/.agents/skills/`
- **settings**：`settings/<host>/*.json` deep-merge 到该 host 的 settings 文件
  - pi → `~/.pi/agent/settings.json`；dsh → （0.2.0 调研后确定）
- **models**：`settings/<host>/model/*.json` deep-merge 到该 host 的模型定义文件
  - pi → `~/.pi/agent/models.json`（模型定义 + cost；apiKey 不入库）；既有模型更新需 `--force`
- **extensions (pi)**：T1 必要官方 example <不收编进仓库>，经 `tools/pi-examples.sh` 定位**已装 pi 包**
  自带 examples/extensions，把白名单项（plan-mode/subagent/question/permission-gate/todo）软链到
  `~/.pi/agent/extensions/`（pi 自动发现）。扩展含完整系统权限 → 需 `--yes`/交互确认；**升级 pi 后
  重跑 install.py 即刷新**到新版本源。卸载移除这些软链。
- 提供 install / uninstall / dry-run / `--yes` / `_` 前缀默认跳过等能力，语义对齐 my-claude 的
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
5. **文档同步**：目录/内容增删改后同步对应文档——涉及**交付内容**（skills/settings）→
   更新给人看的 `README.md`；涉及 AI/内部内容（notes 新增/改动）→ 更新 `notes/MEMORY.md` 索引。
   一次 commit。（pi 官方 example 扩展不经本仓库、由 install.py 从已装 pi 包动态软链，见安装机制。）
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

### 宿主作用域标签（新 issue 必打）

每个 issue 都要打且只打一个「宿主作用域」标签，表达该内容属于哪个宿主；追加其它标签时
总标签数仍 ≤5：

| 标签 | 含义 | 适用示例 |
|---|---|---|
| `pi` | 仅 pi 用 | settings/pi、pi 的 extension/plugin 适配与安装、pi 机制调研 |
| `dsh` | 仅 dsh 用 | dsh 调研、`install.py --target dsh`、dsh 设置/插件 |
| `shared` | 跨宿主通用 | 通用 Agent Skills（`skills/`，走 `~/.agents`）、多目标 `install.py`、跨宿主原则/决策 |

判定：能下沉到 `~/.agents`/Agent Skills 供多宿主复用的 → `shared`；锁死某宿主结构/位置的 →
该宿主标签（`pi`/`dsh`；未来 `codex`/`opencode` 同理新增）。范围跨 pi 与 shared 的，按
「是否仅该宿主能消费」判——纯宿主产物打宿主标签，仅设计/原则层面可复用打 `shared`。

登记时给宿主标签附上简短 description（`name:desc` 形式）便于筛选，例如
`pi: 仅 pi 宿主使用的扩展/设置`。
