# dsh 0.1.1-rc.2 Tools 管线与事件

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 服务

- `ctx.tools`（`@deepseek-ai/dsh-tools`）
- 插件通过 `ctx.tools.register(def)` 注册工具
- `register` 的 layer 来自调用 ctx：普通 ctx = global，`agent.ctx` = 仅该 agent

## 工具执行顺序

```
model 调用
 → tools/pre-execute      allow/deny/ask 可重排瀑布
 → ctx.tools.guard()      单调防护（不能反悔）
 → tools/execute           around wrapper：timeout/retry/metrics
 → tool body 执行
 → tools/post-execute      inspect/replace/attach context
 → definition.finalizeContent  最后一次 content-only 收口
 → tools/result           observe-only 通知
 → agent loop 写 durable tool/result session event
```

## 插件常接的钩子

| 钩子 | 类型 | 用途 |
|---|---|---|
| `tools/pre-execute` | 可改 allow/deny/ask | 权限、门禁 |
| `ctx.tools.guard()` | 同步单调 deny | 规则强制拦截 |
| `tools/execute` | wrapper | 超时、重试、metrics |
| `tools/post-execute` | 可改 result/content | 结果 enrich、上下文追加 |
| `tools/result` | 只读通知 | 记录、统计、失败信号 |

## 关键规则

- 访问别的服务必须先 `inject`，否则 Cordis 拒绝访问。
- 工具定义必须声明 `output.schema` 和 `execute(args, exec)`。
- `exec.signal` 是协作取消；body 必须观察/转发 signal。
- `ctx.approval` 是可选注入：没有 approval 服务时 `ask` 降级 deny。
- `tools.restrict()` 可对 agent 做 allow/deny mask，但这是可见性组合，不是安全边界。

## 展示模式

- `tools.mode`：`native`（默认）| `code` | `both`
- `code` 模式只暴露 `run_code` transport + SDK 提示，模型直接调用其它工具会 UNKNOWN_TOOL
- Code Mode 需要 `codeRuntime`，worker-thread 包提供 TS SDK renderer
- agent 可通过 `ctx.tools.presentAs(mode)` 只覆盖自己的展示

## dsh-mint 已用钩子

- `tools/post-execute`：commit reminder
- `tools/result`：失败信号
- `tools/pre-execute` / approval：mint 沙箱提权 gate

## 增补：Shell Env / 终端 / 持久 Shell

- `dsh-shell-env` 管理 `DSH_*` 环境变量；Web 会注入 `DSH_WEB_URL`/`DSH_WEB_MODE` 给模型 shell
- 普通一次性 shell 工具：`tool-bash` / `tool-pwsh`，底层走 bash-sandbox/pwsh-sandbox
- 持久 shell 栈（minimal preset）：
  - `dsh-terminal` + `dsh-terminal-bash` 提供 PTY
  - `dsh-tool-bash-persistent` / `dsh-tool-pwsh-persistent` 注册为模型工具
  - 放在带 isolate 的 group 里，因为 terminal/PTY 是 agent-owned service
- 后台任务：`tool-jobs` 通过 `ctx.jobs` registry；`tool-bash` 可把命令放到后台
- shell 命令默认受 sandbox-policy 约束；persistent shell 不改变沙箱边界
