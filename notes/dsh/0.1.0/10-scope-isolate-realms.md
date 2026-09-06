# dsh 0.1.1-rc.2 Scope 与 Isolate Realm

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 两个不同机制

1. **Cordis `ctx.isolate(name, label)`**：让某个 Service 在 child context 内解析到独立实例。
2. **dsh-scope**：`createScope(ctx, key)` 创建带 tag 的 context；经它注册的工具/section/事件属于该 scope，并随 scope 一起 dispose。

## dsh-scope 关键 API

| API | 作用 |
|---|---|
| `createScope(ctx, key, options?)` | 创建 scope context；注册的 effects 归该 fiber |
| `scopeOf(ctx)` | 读 ctx 的 scope key |
| `bindScopeParent(key, parent)` | 建立 scope 父子链 |
| `scopeTarget(base, key)` | 构造按 scope 过滤的事件 dispatch carrier |
| `Scope.ctx` | scope 自己的注册 context |
| `Scope.dispose()` | 幂等清理 scope 内所有注册 |

## Scope 可见性链

- 注册视图沿 parent chain **向下继承**：child scope 能看到 ancestors 的注册，nearest 覆盖 farthest。
- 事件 admission 沿 parent chain **向上扩展**：ancestor listener 能收到 descendant 的事件。
- Agent 链：`agent -> preset -> global`。

## Agent preset 里为什么需要 isolate

- 如果 preset 里的某行会 `provide()` Service，它必须放进一个带 `isolate` 的 group。
- 否则多个 session/preset 同时注册同名 Service 会冲突。
- `isolate: true` = entry-local realm，每预设一份独立实例。
- Host plane 的 registry 不应放进 preset isolate；preset 只放“只被该 agent 读到的服务/工具”。

## 常见归类

| 应留在 host plane | 可放进 agent/preset isolate |
|---|---|
| session、persistence、sandbox/approval | plan-mode |
| tools registry、skill registry | compaction 系列（读 host tokenMeter） |
| subagent registry、jobs registry | workflow engine（无 host 读者） |
| API gateway、webserver | 自定义 agent 私有 service |

## 注意

- Scope 是注册可见性/生命周期机制，**不是安全边界**。
- 通过 scope context 也会暴露 minting plugin 的 service-resolution 能力。
- 多 membership policy 集尚不支持；一个 context 只有一个最近 scope key。

## 对 dsh-mint

- 如果 mint 只是注册工具/上下文/listener，不需要 isolate。
- 如果 mint 预设未来要提供私有 Service，要放 group + isolate。
