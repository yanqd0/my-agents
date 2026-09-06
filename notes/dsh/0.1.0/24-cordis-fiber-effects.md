# dsh 0.1.1-rc.2 Cordis Fiber 生命周期与 effect 清理

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## Fiber 状态机

`PENDING → LOADING → ACTIVE → FAILED/UNLOADING → DISPOSED`

- PENDING：等待 inject 的服务
- LOADING：执行 plugin apply/构造函数
- ACTIVE：已加载并提供服务
- FAILED：config/plugin body 抛错
- UNLOADING：正在运行 disposers
- DISPOSED：已清理，不能重启

## Effect 机制

- `ctx.effect(fn)`：立即执行 fn；fn 返回 disposer / promise / (async) iterable
- 每个 disposer 在 fiber unload 时按**注册逆序**执行
- generator effect 可一次 yield 多个 disposer，作为事务化注册
- effect disposer 是 single-shot；重复调用/并发清理会合并
- `INACTIVE_EFFECT`：不能在已 inactive context 上建 effect

## 事件监听、服务、工具注册的清理归属

- 插件通过 `ctx.on(...)`、`ctx.provide(...)`、`ctx.tools.register(...)` 等创建 effect。
- 这些 effect 都挂在当前 fiber 的 disposables 上。
- fiber dispose 时自动撤销事件监听、服务提供、工具注册、scoped context 等。

## 对 dsh 插件作者

- 不要手动 unregister；正确注册为 effect/disposable，让 fiber 清理。
- 若创建一次性后台任务/长生命周期资源，要返回 disposer。
- 避免在插件 apply 中启动不可取消的全局副作用。
- 动态加载/热重载依赖 fiber 正确清理，否则会重复注册/资源泄漏。

## Loader 与 Fiber

- Loader 的每个 entry 对应一个 plugin runtime/fiber。
- entry update/remove 会触发 fiber reload/dispose。
- 插件代码 import 失败或 apply 失败会记录在该 entry 的 FAILED 状态。

## 增补：Cordis Reflect / Registry / Intercept

- `ctx.reflect`：context proxy 背后的服务解析层
  - `ctx.provide(name, impl)` 注册 Service
  - `ctx.get(name)` 读取当前可见 Service
  - 未声明 inject 而直接访问会报错，是 Cordis 的显式依赖约束
- `ctx.registry`：plugin 注册与 DI 管理
- `intercept`：给某个 Service 的 config 做按插件粒度的合并；Loader entry 的 `inject` 可携带 intercept config
- Service 的 resolved config 由 ancestor/entry 的 intercept 按顺序合并
- 这对“提供 Service 的插件”尤其重要：需要清楚谁在什么 scope/intercept 下看到你的 Service
