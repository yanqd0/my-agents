# dsh 运行架构与机制总览（持续补充的资料库）

> dsh = `@deepseek-ai/dsh`（DeepSeek Harness），cordis 插件系统。官方资料稀缺（多数是
> 各包 `README.zh.md` 与 bundle 的 `cordis.patch.yml`），**本目录 `notes/dsh/` 作为 dsh 知识
> 库持续补充**。新增/改动任一 notes 文件须在 `notes/MEMORY.md` 登记。本文 = 会话调研的
> dsh 了解总览（版本依据 0.1.1-rc.2，profile=web 实机）。

## 1. profile 与装配（bundle 层）

- profile 即 `$DSH_HOME/profiles/<name>` 目录，本质是一个 npm 项目：`package.json`
  （依赖 + manifest `dsh.profile.bundles` 有序列表）、`cordis.patch.yml`（用户 patch 层）、
  `pnpm-workspace.yaml`（+lock）。默认 `$DSH_HOME=~/.dsh`（`dsh-home-paths`）。
- **bundle = 其 `package.json` 声明 `"dsh":{"bundle":{"patch":"./cordis.patch.yml"}}` 的 npm 包**；
  真实装配树由各 bundle patch 拼出（本机 web：`bundles=[dsh-base, dsh-web-app]`，
  `dsh-base` 挂 agent/llm/session/skill/commands… 等 ~几十个核心 entry）。
- **层叠顺序**（后写覆盖同 id 行）：空根 `cordis.yml` `[]` → `dsh.profile.bundles` 各 patch →
  profile `cordis.patch.yml` → `~/.dsh/cordis.patch.yml` → `--patch` overlay（bin 启动 flag，可重复）。
- 启动/初始化：`dsh-app-boot` 首次用即按模板 init profile；**已存在文件绝不被改写**，只补缺失。
  web 与 headless 是内置模板名；自定义名 init 为 `[dsh-base]`（经 `dsh plugin`）。

## 2. 前端形态（在终端用 dsh）

- **web = 唯一官方交互客户端**（浏览器 GUI，`dsh web` = `--profile web`，`dsh-web-app` bundle）。
- **headless = 一次性问答**：`dsh --profile headless "task"`，跑完把最后一条 assistant 文本写
  stdout 退出，无端口/无交互（dsh-headless）。
- **无官方 TUI 客户端**：`tui` 不是内置模板；交互式 TUI 需自建 client bundle（远期）。
- agent 内部的 `dsh-terminal`/`dsh-cmdline` 是「终端工具/参数解析」底座，不是客户端。
- 本仓库对 dsh 的 skills/settings/插件安装不依赖某前端形态；skills 直接读 `~/.agents/skills`。

## 3. skill / context / hook：三个正交机制（非统一伞）

- **skill**（注册表 `ctx.skills`）：`dsh-skill` 只做注册表；`dsh-skill-filesystem` 是文件系统
  provider，默认扫描根（rank）：项目 `.dsh/skills`(100)/`.agents/skills`(200) → `customSkillDirs`(300)
  → `~/.dsh/skills`(400) → `~/.agents/skills`(500)；一层格式 `name/SKILL.md` 或 `name.md`。
  `dsh-tool-skill` 消费：会话目录 + `skill` 工具，以 `<skill_content>` 渲染。→ my-agents 落
  `~/.agents/skills` 即被直读（详见 skills-settings-loading.md）。
- **context/指令**：`dsh-system-prompt` 组装有序 sections + 动态 context 快照 + variables
  （如 "Current runtime context…" 前缀）；插件以 snapshot/section 注入；项目级指令文件由
  `dsh-agent-instructions` 注入（repo `AGENTS.md`/`CLAUDE.md` + 全局 `~/.dsh/AGENTS.md`）。
  → my-agents 仓库 `AGENTS.md` 天然被 dsh 读，跨宿主成立。
- **hook**：即 cordis 事件/waterfall（`tools/pre-execute→execute→post-execute→finalizeContent`、
  只观测 `tools/result`；另有 `agent/pre-step`、`skills/change`、`settings/updated`…）。**只能写插件
  代码监听**，无纯配置文件 hook → 归入插件管理边界。

## 4. 插件管理（`dsh plugin` 与 bundle 机制）

- `dsh plugin --profile <p> <pnpm add|remove|... <pkg>>`：薄 pnpm 转发器。缺 profile 自动按模板
  init（web/headless 模板，自定义 init 为 `[dsh-base]`）；成功后把**声明 `dsh.bundle` 的依赖自动
  并入** `dsh.profile.bundles`（remove 则移出）；纯库只作依赖、告警不入层。相对 `./`/`file:`/`link:`
  spec 会按调用者 cwd 锚定。
- my-agents 框架：`install.py` 的 `DSH_PLUGINS_BY_PROFILE`（`profile → [bare 包名]`，目前为空）。
  幂等/回滚细节见 skills-settings-loading.md §插件。
- 原生/安装脚本模块需在 profile `pnpm-workspace.yaml` 的 `allowBuilds` 放行；`nodeLinker: hoisted`。

## 5. 配置型插件 / context 的 patch & overlay 契约（issue #36；落地待真实消费方）

格式权威样例 = `dsh-base/cordis.patch.yml`。patch 是**顶层 YAML 数组**：
- 插入：`- insert: [ {id, name, config…}, … ]`（插一整组 entry；`name` 为模块 spec）。
- 覆盖：后续层**按 `id` 定位行、整行 `config` 替换**（非 merge）；同 id 后写胜。
- 叠加方式（三选一，由用途定）：
  a) **随项目交付 overlay + `dsh --profile <p> --patch <file>`**：去 flag 即回滚、零持久变更，适
     合「体验/临时」与给非 bundle 插件挂 entry 的首跑验证。
  b) **持久写进 profile `cordis.patch.yml`**（用户层）：适合「本机常驻」，但 profile 由用户拥有，
     内容项目不应整体覆写，可 append 自己命名的 insert。
  c) bundle 包自带的 patch：仅随发布，非本项目职责。
- 覆盖例：`@yanqd0/dsh-mint` 自身不声明 `dsh.bundle`，属非 bundle 配置型插件 → 需以 entry
  `- insert: [{id: mint, name: '@yanqd0/dsh-mint', config: {...}}]` 挂载（dsh-mint 文档的 MOUNTING）。
- **注意**：overlay `--patch` 是启动 flag，本机 web GUI 的常驻挂载不靠它（用 b）；做 `--patch`
  验证时另开进程、勿干扰运行中 GUI。`--dump-config` 可打印合成树用于核对。
- **本项目当前立场（#36 定案）**：overlay/`--patch` 的**语法与用法已写入本文档**；因暂无真实
  非 bundle 配置型插件/context section 要交付，**不预建空示例 overlay 文件**。待首个真实消费方
  （如确要常驻某配置插件）出现时，按本契约落地并同步 notes/MEMORY。

## 6. 结论速览（跨文档指针）

- skills → `notes/dsh/skills-settings-loading.md`（落 `~/.agents/skills`，跨宿主）。
- settings/模型/cost → skills-settings-loading.md（无 pi models.json；settings 为 YAML namespace）。
- 插件管理框架 → skills-settings-loading.md §插件 + 本文 §4。
- overlay/patch（配置型/context）→ 本文 §5。

## 未决 / 待确认
- web 常驻如何给非 bundle 插件挂 entry（本机 `cordis.patch.yml` 为空但 `@yanqd0/dsh-mint` 在
  dependency 且能加载——其真实挂载点?待核实 dsh-mint 自带 bundle/或经别层挂载）。
- 未来交互式 TUI 客户端形态、headless 一键封装入 install（issue #37）。
