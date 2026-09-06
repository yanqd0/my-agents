# dsh 0.1.1-rc.2 Settings / Credentials / Model Selection

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## Settings 文件

- 包：`dsh-settings-file`
- 默认路径：`$DSH_HOME/settings.yaml`，未设 DSH_HOME 时为 `~/.dsh/settings.yaml`
- 一个文件多个 namespace；外部编辑热发布
- `update()` 是 read-modify-write + 原子 rename + 跨进程 writer lock
- YAML 写回做 leaf-level diff，保留用户注释
- boot 时 invalid 文件 fail loud；运行中 invalid 编辑保留 last-good

当前实际 settings：

```yaml
agent-default-model:
  provider: deepseek-official
  model: deepseek-v4-flash
  reasoningEffort: low
ui-onboarding:
  welcomeNoticeVersion: 2026-08-13.1
```

## Credentials 文件

- 包：`dsh-credentials-local`
- 默认路径：`$DSH_HOME/.credentials.yaml`
- 四层优先级：inherited env > `.credentials.yaml` > project `.env` > user `.env`
- managed 文件不进入 process.env
- 文档权限：目录 `0700`、文件 `0600`
- 当前实际含 `DEEPSEEK_API_KEY`
- 注意：这不构成“模型读不到”的安全边界；同一 uid 的 bash/fs 可读该文件

## Model Selection

- 包：`dsh-agent-default-model`，ctx：`agentDefaultModel`
- 三层解析：session 当前选择 > session 最新 request/header > 默认配置
- 已运行 session 从 log 读选择；blank session 观察默认
- `saveSelection()` 保存到 settings；无 settings provider 时 no-op
- 不校验 catalog 成员；模型是否可用由实际 adapter/request 负责

## dsh-mint 设计提示

- 若 mint 需要用户配置（如 db 路径、仓库、autoApprove），可注册自己的 settings namespace。
- 不应把 mint secret 放进普通 settings；用 credentials seam 或保持用户环境层。
- 如果 mint 需要按模型/项目给不同上下文，不要在 host 层写死，优先让 settings/workspace 承载。

## 增补：LLM 接口 / Adapter / Models 设置

- `ctx.llm` 是 provider-neutral 调用面；adapter 通过注册提供实际请求能力
- 关键流程：`agent/request` 组装 → `llm.prepareCall()` → `llm/stream` → request-error/retry
- 每个模型路由可声明 adapter 默认：reasoningEffort、maxTokens 等
- `dsh-llm-deepseek` 与 `dsh-llm-pi-ai` 都是 adapter：
  - deepseek-official 是默认可用
  - pi-ai 默认 dormant，需要 settings 写 `llm-pi-ai` provider 才生效
- Models 页写 settings/credentials：
  - settings `llm-deepseek:` / `llm-pi-ai:` 段覆盖 adapter 配置
  - credentials 只存引用，不让 adapter key 进入 process.env
- 用户默认模型由 `agent-default-model` settings 段控制；当前实际 `deepseek-v4-flash + reasoningEffort low`
- 插件一般不要直接拼 provider 请求；应通过 `ctx.llm` 或工具栈，避免绕过 retry/adapter 语义
