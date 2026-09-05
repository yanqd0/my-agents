# pi 扩展与插件技术选型

> 目标：补齐 pi 相对 Claude Code / Codex 的能力，同时守住"核心精简、可审计、多宿主可控"。
> 状态：初稿（评审中）。范围仅 pi；dsh/codex 复用其中**跨宿主部分**后各自补丁。
> 结论类型：**T0/T1** 为已定选型；**T2** 为口碑代理下的初选，落地前需源码审查 + 锁版本。

## 三档政策

| 档 | 定义 | 政策 |
|---|---|---|
| **T0** | pi 原生能力 | **不动，用默认**（不评估、不装插件覆盖） |
| **T1** | pi 无、但**官方 extension** 有能力 | **支持安装**（安装/分发方案待定，见 §安装方案） |
| **T2** | **只有第三方插件**能支持 | **选口碑最好**（下载量 + 维护活跃为口碑代理）；落前审源码、锁版本 |

备选（PK 失败项）一律保留，便于未来换用。

## T0 — pi 原生（默认，不选型，仅登记）

Agent Skills（`~/.agents/skills` 递归发现）、AGENTS.md/CLAUDE.md 上下文、compaction、
headless/`-p`/json/rpc、sessions/fork/clone/tree、prompt templates、themes、thinking/models/providers。

## T1 — 官方 extension（已定：收编官方 example，方案待定）

官方 = pi 仓库自带 `examples/extensions/`，随版本同源维护，是唯一"官方出品"。能力与
CC/Codex 对应、须支持安装：

| 能力 | 官方 example | 说明 | 备选(T2 提升项，保留) |
|---|---|---|---|
| Plan 模式 | `plan-mode/` | `/plan`(Ctrl+Alt+P/`--plan`)、只读禁 edit/write、bash 白名单、`Plan:` 分步 `[DONE:n]` | `@narumitw/pi-plan-mode`(29k,Codex风)、`@janvitos/pi-plan-build`(7k)、`@bacnh85/pi-plan` |
| Subagent | `subagent/` | 独立 `pi` 子进程隔离上下文；自带 scout/planner/reviewer/worker + implement/implement-and-review prompts；支持 single/parallel/chain | `@narumitw/pi-subagents`(10k,异步job)、`@zhushanwen/pi-subagent-workflow`(4.8k)、`@d3ara1n/pi-subagent`(3.5k,角色化)、`pi-subagents`(362k,单agent委派/脚本编排)、`@agwab/pi-subagent`(极简) |
| 反问(AskUserQuestion) | `question.ts` | 模型可调用 `question` tool：选项列表+"Type something."自由文本，≈CC AskUserQuestion | `@juicesharp/rpiv-ask-user-question`(117k)、`pi-interview`(13k,表单)、`pi-ask-user`(10k)、`@pi-unipi/ask-user`、`@zhushanwen/pi-ask-user` |
| Hooks/守卫(基础) | `permission-gate.ts` `protected-paths.ts` `confirm-destructive.ts` `dirty-repo-guard.ts` `interactive-shell.ts`(bash spawn) | pi 无 CC 的 hooks 配置结构，等价物=extension 事件拦截，逐用途单文件 | 强引擎见 T2 |
| Todo | `todo.ts` | todo tool + `/todos` + 持久化渲染 | `@pi-archimedes/todo` |
| Checkpoint | `git-checkpoint.ts` `auto-commit-on-exit.ts` `git-merge-and-resolve.ts` | git 存档/自动提交/合并 | — |
| 后台/异步(轻) | subagent 的 chain/parallel | 真后台 jobs 官方缺，见 T2 | — |

### 安装方案（待定 → issue 决策）
三个候选，倾向 (a)/(c)：
- (a) **收编 vendor**：把选定官方 example 拷进 my-agents `extensions/pi/`，由 `install.py --target pi`
  分发到 `~/.pi/agent/extensions/`（多文件需 `extensions/<name>/index.ts` 形态）。可控、可复现、喂 dsh/codex。
- (b) 直接软链 pi 包内 example：依赖 pnpm store 版本路径，**升级即漂移，不推荐**。
- (c) 在 my-agents 内组织成 pi 本地 package（`package.json` + `pi` 清单），`pi install /path/to/my-agents/extensions-pi`。

## T2 — 仅第三方（初选口碑最好，落前审源码+锁版本）

| 能力(官方缺) | 首选(口碑) | 备选(PK 失败保留) |
|---|---|---|
| **MCP 接入**（pi 无原生/无官方） | `pi-mcp-adapter` (761k) | `pi-mcp-extension`(11k)、`@pi-unipi/mcp`(2.9k,管理)、`@xynogen/pix-mcp`(token高效)、`pi-mcp-router`(1.9k,path多账号) |
| **深度代码/PR 审查**（官方仅极简 reviewer） | `pi-pr-review` (6.2k, PR 并行分层) 或 `@georgedong32/pi-review`(2.1k,N 并行) — 按使用场景二选一 | `@plannotator/pi-extension`(52k,plan+PR注解)、`@howaboua/pi-subagent-review`(/review)、`pi-ai-slop-review`、`@fyeeme/pi-review` |
| **强权限引擎 / CC 兼容 hooks**（官方仅极简守卫） | `@gotgenes/pi-permission-system` (30k) | `@aliou/pi-guardrails`(6.5k)、`@inobit/pi-permission`(2.9k)、`pi-yaml-hooks`(2.9k,YAML hooks)、`@agimon-ai/doompi-hook`(3.1k,CC 兼容 runner) |
| **后台持久任务/jobs** | `pi-background-tasks` (107k) | `@mjasnikovs/pi-task`、`pi-better-background-tasks`、`@arhen/pi-core-subagent`、`simple-subagents` |

> 下载量为口碑代理（示意，来自 npm registry 搜索，非精确日活）；"首选"落定前必须各自 GitHub
> 审源码，并 `pi install` 带**精确版本**锁定（勿用 `pi update --all` 自动浮升）。

## 决策原则（贯穿全部）

1. **官方优先于第三方**：结构性能力（plan 门、subagent 运行时、反问、基础守卫/todo/checkpoint）
   用官方 example；第三方只补"官方确缺"。
2. **不堆重叠包**：同类只装 1 个；多个都注册同名命令(`/plan`/`/review`/`question`)会冲突。
3. **安全底线**：extensions 有完整系统权限；第三方一律审源码 + 锁精确版本；只装真需要的。
4. **Token/性能克制**：优先功能精简、无重 UI/无"另起模型分类"的包；重体验/审查类按需触发。
5. **跨宿主可迁移**：能下沉成 skill 的（review、plan 流程文本）尽量 skill 化（走 `~/.agents` +
   Agent Skills，dsh/codex 复用）；只有真需事件/UI 的才用 extension。

## 反问的跨宿主适配（AskUserQuestion）

pi 不向模型暴露 AskUserQuestion：本选型用 T1 `question.ts`/自写薄 `ask_user_question` tool
（`ctx.ui.select/input`）。依赖交互的 skills 迁移规则：
- frontmatter `allowed-tools` 的 `AskUserQuestion` → 改为实际 pi tool 名（`ask_user_question`/`question`），
  并要求该 extension 已装。
- skill 正文交互点写成**统一动作名**（如"反问 ask 二选一"），由各宿主 adapter 层映射到本宿主 tool
  （对齐 mint `references/agent/*` 思路）。
- 无 UI/headless(`-p`/rpc)：`ctx.ui.*` 为 no-op → 交互点必须写明"退化为纯文本陈述等用户文字回答"。

## 落地待办（挂 plan）

- [ ] 决策 §安装方案 (a)/(c) → 并入 my-agents `install.py` 设计（issue #1）。
- [ ] T2 首选逐个审源码 + 定精确版本后，再进选型。
- [ ] AskUserQuestion 适配层 + 依赖交互 skills 改写规则 → 写入 AGENTS.md 迁移原则。
- [ ] MCP/深度审查/强权限/后台 jobs 属 0.2.0 及以后范围，按需再细化。
