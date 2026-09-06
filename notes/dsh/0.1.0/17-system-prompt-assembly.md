# dsh 0.1.1-rc.2 System Prompt 装配机制

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 服务

- 包：`@deepseek-ai/dsh-system-prompt`，ctx key：`systemPrompt`
- 装配结果：sections + tools + variables
- 每个 step 装配一次，渲染成完整系统提示词

## Config

| Key | 默认 | 含义 |
|---|---|---|
| `includeHarnessIdentity` | true | 固定 identity opener：`You are an AI agent powered by DeepSeek Harness.` |
| `includeRuntimeContext` | true | 是否评估动态 runtime context |
| `persona` | '' | 全局 deployment persona，order 0；空则不渲染 |
| `toolOrder` | — | 显式工具排序；需恰好一个 `'<unlisted-tools>'` rest entry |

## 主要 API

| API | 作用 |
|---|---|
| `ctx.systemPrompt.section(section)` | 注册 prompt section；`agent.ctx` 注册可只覆盖该 agent |
| `ctx.systemPrompt.context(context)` | 注册动态上下文 provider，每次装配评估 |
| `ctx.systemPrompt.suppressRuntimeContext()` | 关闭该 scope 的动态上下文 |
| `ctx.systemPrompt.tools(provider)` | 贡献 tool schemas |
| `ctx.systemPrompt.variable(name, provider)` | 注册 `{{name}}` 变量 |
| `ctx.systemPrompt.assemble(context?)` | 装配一次完整 prompt |

## Section 规则

- sections 按 `order` 升序拼接。
- order band：identity `-100`、persona `0`、tool guidance `100-199`。
- `complete: true` 的 section 会成为唯一完整 prompt；多个会拒绝装配。
- section text 中的 `{{var}}` 会严格插值；未知/无值变量抛错。
- 同一层同名 section/duplicate 会 throw。

## Scope 可见性

- 全局注册：普通 ctx
- agent 注册：`agent.ctx`，shadow 全局同名 section
- scope 链：`agent -> preset -> global`
- 子代理 join 父 preset，因此能看到父 preset 的 prompt 组成

## 动态 Context 与 Token

- 动态 context 会变成 user-role runtime-context snapshot，属于 request prefix 一部分。
- System prompt 和 context 每次请求都重复，token 成本与文本量成正比。
- KV cache：identity/persona/sections/variables/tool schemas 稳定时前缀可复用；任何变化都可能从变化点失效。
- 注入越多，越可能在每轮重复花费 token。

## dsh-mint 建议

- 优先用 `agent.ctx.systemPrompt.context()` 注入**简短、可复用**的 mint 概览。
- 不要每轮注入长 issue 列表；放工具返回或按需读取。
- 若需要完全自定义 persona（如 minimal），可用 `complete:true`，但要清楚会替换默认身份与所有普通 sections。
- 当前 dsh-mint 已用 `systemPrompt.context/section` 或 session-start 注入；需核对实际注册层是 global 还是 agent 层。

## 增补：dsh-persona / complete persona

- `dsh-persona` 是 preset 中用来给 agent 单独设置 persona 的插件行。
- `persona` config：
  - `text`：persona 文本
  - `complete`：若 true，该 persona 成为完整系统提示词（会替换默认 identity + 普通 sections）
  - `includeRuntimeContext`：若 false，关闭该 agent 的动态 runtime context
- minimal preset 示例：`complete:true` + `includeRuntimeContext:false` + 只有两工具，形成“固定 prompt 的极简 agent”。
- 与 host `system-prompt.persona` 的区别：
  - host 配置是全局 deployment persona；
  - `dsh-persona` 在 agent scope 注册，shadow 全局；
  - `complete:true` 只在极简/固定角色场景用，否则会丢弃 harness identity、工具引导等普通 section。
- `{{model}}` / `{{cwd}}` 等变量在 persona 文本中可用；由 agent loop 提供。
