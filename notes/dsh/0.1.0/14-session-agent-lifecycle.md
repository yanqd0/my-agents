# dsh 0.1.1-rc.2 Session 创建 / Resume / Fork / Subagent 生命周期

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 关键约定

- Agent 与其 Session 共用同一个 `SessionId`。
- Session log 是真相源；resume 时重建 history 后继续，不丢失原 turn 编号。
- 同一 id 并发创建只允许一个最终进入 registry，失败者回滚。

## Create / Resume

| 路径 | 入口 | 流程 |
|---|---|---|
| Create | `ctx.agents.create()` / `ctx.agentLoop.create()` | 建 private session/agent/scope → 执行 unpublished setup → 进入 session/agent registry → announce → emit `agent/session-start` → 启动 driver |
| Resume | `ctx.agents.resume()` | 从 persistence 加载 session → 按同一 id 重建 agent/history → 重新 setup → publish |
| 配置启动 | agent-loop `agents[]` | host 启动自动建 agent；支持 `resumeSessionId` 恢复持久会话 |

- setup 是 trusted composition code，不能驱动未发布的 agent。
- `AgentHandle.dispose()` 是唯一消费方 teardown 能力；loop provider 卸载是独立清理边。

## Fork

- `ctx.sessions.fork(source, boundary?, childSessionId?)`：从源 session 的历史前缀创建 child。
- boundary 默认到当前最后事件，且要求前缀不在 open turn 中间。
- fork child 继承 lineage、seed、cwd、模型选择，并可能加入 workspace。
- fork 的子代理“看得到父代理已完成历史”。

## Subagent

- 抽象：`ctx.subagents`（`@deepseek-ai/dsh-subagent`）
- provider：`spawn`（全新子代理）、`fork`（历史前缀）、未来的 out-of-process
- 本地 in-process provider 使用 `ctx.agents.create()` + owned handle
- `start(name, request)`：one-shot，等真实 child published 后返回 run
- `startContinuable(spec)`：可续接子代理，返回 `{childId, messageId}`，不等待 turn 完成
- `followup(parent, childId, content)`：可续接子代理下一条消息
- `interrupt(targetSessionId, authority)`：中断可续接子代理当前 turn
- 子代理 join 父代理的 agent preset：通过 `applyChildComposition(childCtx, parent, composition)` 调用 `composeFrom()`
- child durable header 记录：`parentSession`、`delegationDepth`、preset id

## 策略继承

- in-process 子代理继承父会话的 sandbox override。
- 子代理 approval policy 常被 pin 成 `never`：无人看 prompt，直接拒绝 escalation。
- spawn（全新）不继承父历史；fork（前缀）继承已发生历史。
- 子代理不能因为父会话后来切 preset 而改变运行中的组成。

## dsh-mint 注意

- `agent/session-start` 是最早可安全做上下文注入的 host 侧事件。
- 事件 payload 是 `{ agent, source }`，项目目录用 `agent.session.header.cwd`。
- 子代理也会触发 session-start；若不想重复注入，需要判断是否为 root/是否已有父 preset 组成。
