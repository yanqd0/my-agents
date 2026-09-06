# dsh 0.1.1-rc.2 Session 事件溯源与投影系统

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 核心模型

- `dsh-session`：append-only 的 `session/event` log 是 Session 的真相源。
- 模型看到的 message history 是**从 log 推导出来的 surface**，不是独立存储。
- 事件被 snapshot/freeze；插件通过 merge 扩展 `SessionEventMap`。

## 常用概念

| 概念 | 说明 |
|---|---|
| `Session` | 事件日志 + 内存 session store |
| `session.append(type, data)` | 追加事件，同步提交后通知 |
| `session.surface` | 已排序投影出的消息视图 |
| `session.deriveMessages()` | 增量重建完整消息数组 |
| `ctx.sessions.flush(session)` | 等待持久化 checkpoint 完成 |
| `ctx.sessions.fork(source, boundary?)` | 以历史前缀创建子 session |
| `session/event` | 每个已提交事件的 live 通知 |
| `tool/result` | durable 工具结果事件（与 live `tools/result` 不同） |

## 持久化链路

- `dsh-session-persistence-jsonl`：JSONL 后端，写入 `$DSH_HOME/sessions`
- `session-checkpoint-policy`：模型请求前/工具副作用前做 checkpoint
- 冷 session 可通过 persistence 读取/重建，不一定要 resume live Agent

## Projection 系统

- 包：`@deepseek-ai/dsh-session-projection`
- 注册表：`ctx.sessionProjections.register(unit)`
- 每个 unit：`{ key, stateSchema, init(), apply(state, event), wire?, stateVersion }`
- 框架订阅 `session/event`；每个已提交事件都喂给所有 unit 的 `apply`

### 规则

- unit 计算必须同步、纯状态变换
- `apply` 对无关事件必须返回同一 state reference，否则视为 change
- 状态事件必须携带**完整 post-change state**，不能只带 delta
- `stateVersion` 变更时旧 cache 失效
- client-visible unit 通过 `wire.view` 输出 schema 化视图
- host-only unit 不给浏览器

### 提供方与消费方

- Domain 提供方：todo、goal、session title、token-meter 等注册自己的 unit
- 消费方：api-proxy history tail 带 `projections` block；连接后通过 `session/projection` frame 推变化
- client runtime 维护 generic `ProjectionValueStore`，UI 用 `projections.faceOf/useProjection` 读取

## Cache / Search

- `dsh-session-projection-cache`：持久投影 checkpoint，避免每次冷读全量回放
- `dsh-session-query-sqlite`：SQLite FTS5 后端；默认 `openAt:never`（全文搜索关闭）
- 精确读、标题、workspace 搜索不需要 SQLite 索引

## 对插件作者

- 需要展示“从会话历史派生状态”时，优先注册 projection unit，而不是自建事件订阅。
- 需要持久化用户可见状态，应先写 session event，再做投影。
- 不要手写 session log 消费循环；让 framework 驱动 projection。
