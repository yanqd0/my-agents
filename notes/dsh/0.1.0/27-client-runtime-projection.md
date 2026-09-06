# dsh 0.1.1-rc.2 Web 端 SessionRuntime / ProjectionValueStore

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 角色

- 包：`dsh-client-runtime`
- 浏览器端核心对象服务，不依赖 React：
  - SlotRegistry：UI slot 注册/渲染
  - SessionRuntime：Session 列表、打开窗口、历史分页、queue/projection
  - WorkspaceRuntime：Workspace 列表、会话归属、blank reuse
- 浏览器 Session 一律由 Host 创建；客户端没有“本地先建 session”的状态

## ProjectionValueStore

- 每个 Session 持有 generic projection value store。
- 初始值来自 history tail 的 `projections` block。
- 之后由 `session/projection` frame 更新，`higher-seq-wins`。
- UI 用 `projections.faceOf` / `useProjection` 读取领域数据（todos、goals 等）。
- 不要从 ConversationSnapshot 直接读这些领域状态。

## 常见同步流

```
Host 提交 session event
 → sessionProjections 更新
 → api-proxy 推 session/projection frame
 → client ProjectionValueStore 更新
 → React useProjection 触发 UI
```

## 列表与多 tab

- Workspace/Session 列表有独立 pending→ready baseline。
- 增量 upsert/removal/order frames 会覆盖/重放；reconnect 后重发 baseline。
- 多个 tab 通过 host broadcast frame 保持一致。
- Workspace 顺序以 Host durable order 为权威；本地乐观操作只接受最新 unary echo。

## 自定义 UI 数据建议

- 优先把“领域值”做成 host projection unit，再走 standard projection 通道。
- 不要自己在浏览器维护一份从 RPC/event 手工同步的 session 状态。
- UI 组件只消费 final Node/value；不要自己 fold events。

## dsh-mint

- mint tab 若展示 per-session mint 状态，最好在 host 侧注册 mint projection unit。
- 若只是“当前 workspace 的 issue 列表”，可走 Remote/RPC + 本地组件状态，不必强制投影。

## 增补：reconnect / queue / jobs 镜像

- 连接层会维护 mux baseline/replay：
  - 断线重连后 Host 重发 baseline，客户端按 generation 丢弃旧 generation 数据
- `session/queue`：Host 对 pending next-turn 的权威快照
  - baseline + 每次 inbox/spliced 变化后推送整快照
  - 客户端不自行从 `agent/inbox/*` live events 重建 queue
- `session/jobs`：后台任务快照
  - 无 owner 的任务对所有订阅可见；有 owner 的任务按 session 过滤
  - 空任务集发 `[]`；不保留陈旧镜像
- `SessionSummary.pendingInteraction`：approval/question/plan-review 的跨连接状态
- 自定义 UI 应消费这些已有镜像/投影，不要自己另做同步逻辑
