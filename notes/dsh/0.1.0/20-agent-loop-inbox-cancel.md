# dsh 0.1.1-rc.2 Agent Loop / Turn / Inbox / Cancellation

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## Agent Loop 定位

- 包：`dsh-agent-loop`，ctx：`agentLoop`
- 是 harness 里唯一包含具体 loop 逻辑的包
- 外部不依赖 driver 内部；通过 session events + `agent/*` events + `ctx.agents` 观察/控制

## Config

```ts
{
  maxParallelToolCalls?: number, // 默认 10；1 表示串行
  agents: Array<{
    id: string,
    provider?, model?, maxTokens?, resumeSessionId?, cwd?
  }>
}
```

- `maxParallelToolCalls` 是唯一进入 settings 的 agent-loop 配置
- `agents[]` 在服务启动时消费，不在运行中热改

## Inbox 语义

| 操作 | 行为 |
|---|---|
| `agent.followup(content)` | 加到 next-turn FIFO，并唤醒 driver |
| `agent.steer(content)` | 加到 next-step，并唤醒 |
| `agent.inject(content)` | 加到 next-step，不唤醒 |
| `agent.cancel(cause, {keepInbox?})` | 取消当前 turn；keepInbox 可保留 pending work |
| `agent.inbox.claim(target)` | 原子领取下一批输入 |

- turn 边界会领取 next-step 输入 + 一条 next-turn prompt；step 边界只领取 next-step。
- 每次 inbox mutation 发布标准 `agent/inbox/spliced` durable event。
- `agent/pre-step` 返回 reject 或完整 messages 进入 step。

## Durable 事件与 live 事件

- 消息、turn/step、assistant chunk、tool call/result 都以 session events 持久化。
- `agent/*` live events 主要给 UI/协调者做实时状态。
- UI 历史从 session log 重建，不从 live events 重建。

## Cancellation

- 取消是协作式：`exec.signal` 只通知，tool body 必须自己停止。
- cancel 后 pending work 默认清除；`keepInbox:true` 保留。
- cancellation 原因记录在 durable `turn/end`：user/parent/disposed。
- 未被 dispatch 的 tool call 会得到 synthetic `tool/call` + `ABORTED_BEFORE_DISPATCH`。

## 插件扩展点

- 几乎所有“额外行为”都应写在 plugin 里，不改 agent-loop：
  - policy/权限：tools/pre-execute、guard
  - 重试：agent/request-error + llm-retry
  - 压缩：agent/pre-step + request-error
  - 子代理：ctx.subagents + tools
  - 持久化：session/event + session/flush
  - UI：session/event + agent/status

## dsh-mint 注意

- 监听 `agent/session-start` 时只能做 setup/注入，不要驱动 agent。
- 若要“在 turn 前/后注入 mint 提醒”，应选对应 agent/tools 事件点，而不是自己改 loop。
