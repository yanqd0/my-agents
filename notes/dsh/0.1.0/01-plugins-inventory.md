# dsh 0.1.1-rc.2 自带插件清单与作用

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 环境

- `@deepseek-ai/dsh` `0.1.1-rc.2`，Node 22
- profile：`web`
- bundles：`dsh-base` → `dsh-web-app`
- web profile 有 97 个依赖；96 个 @deepseek-ai，1 个 `@yanqd0/dsh-mint`（link）
- 注意：不是所有依赖都自动挂载；真正挂载靠 `cordis.patch.yml` / bundle patch

## 挂载结构

| 层 | 内容 |
|---|---|
| dsh-base | 向空根插入 78 个共享核心行 |
| dsh-web-app | 新增 57 个 Web/host 行；覆盖/禁用 27 个 base 行 |
| agent-presets | 默认 `standard`；每个会话再挂载 agent 面工具 |

## Host 面插件组（base + web-app）

### 基础设施 / Cordis
- timer：定时器
- hmr：patch 热重载（web 关闭）
- llm / session / typert / typert-loader / api-gateway：LLM、session、Typert 反射与 API 网关

### Agent / LLM / 会话
- agent / agent-loop / agent-default-model / system-prompt：agent 生命周期、默认模型、系统提示
- session-title / session-title-llm：标题生成
- user-questions：向人提问
- llm-retry / llm-deepseek / llm-pi-ai / settings / credentials：模型适配与配置
- jobs / token-meter / compaction-basic / command-compact / tool-result-pruner / checkpoint-policy：任务、token、压缩、checkpoint

### 持久化 / 存储 / 搜索
- session-persistence-jsonl：JSONL 会话日志
- attachment-local：附件
- session-query-sqlite：SQLite/FTS5，默认关闭全文搜索
- session-projection / session-projection-cache / session-reference / file-reference-local / session-stats
- storage / storage-json / storage-domain：KV 存储

### 沙箱 / 权限 / 子进程
- subprocess / sandbox / sandbox-policy / bash-sandbox / pwsh-sandbox
- approval / permission / shell-env / fs-sandbox / fs-observation-policy

### 领域服务
- goal / goal-round-driver / command-goal / command-feedback / commands
- skill / skill-filesystem / skill-badge
- web / web-search-deepseek / tool-web（web_fetch 关闭）
- spill-local / spill-policy / timeout-policy / repeat-tool-reminder
- subagent / spawn-in-process / fork-in-process / workflow-worker-thread / tool-subagent-report

### Web host / UI
- code-runtime / webserver / web-runtime / api-gateway / api-remotes / connection
- directory-picker / plugin-inventory / client-hmr / client modules
- client-runtime / cordis-client-runner / 各 `client-ui-*`

## Agent 面（standard 预设）

每个会话额外挂载：persona、agent-instructions、bash/pwsh、fs/fs-search、jobs、skill-filesystem/tool-skill、goal、plan-mode、compaction、subagent/delegation/workflow、ralph、ask-user、todo、web。codex/claude-code 两个子代理 provider disabled。

## 其余 preset

- `minimal`：持久 bash/pwsh + fs-local + str_replace_editor
- `code`：standard + Code Mode presentation
- `cordis`：standard + tool-cordis（可读写当前运行树）

## 其他自带 bundle

- `@deepseek-ai/dsh-headless`：headless 一键任务 bundle，未初始化，不属于 web。

## 增补：Skill 注册与发现

- `dsh-skill` 是 skill provider registry；注册按 scope layer：global + 各 preset/agent layer
- `skill-filesystem` 发现本地 skill 目录：
  - `$DSH_HOME/skills` / user root
  - preset 可用 `customSkillDirs` 提供随 preset 携带的 skill
- `tool-skill` 给 agent 加载 skill catalog/内容的模型工具
- 当前 shipped `skill-badge` disabled；mint 自带 skill 通过 user skill 目录安装
- skill 与工具的区别：skill 通常是文档/流程资产，模型按需用 tool-skill 读取；不是直接可调用函数
- 查看/调试：`ctx.skill`、skill-filesystem 的 collect 路径、session 中是否出现 skill 内容
