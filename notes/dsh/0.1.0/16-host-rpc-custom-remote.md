# dsh 0.1.1-rc.2 Host RPC / 自定义 Remote 扩展

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 现状

- Host 侧 RPC 主入口：`dsh-host-apiproxy` 提供 `ctx.apiProxy`
- 浏览器传输：`dsh-client-connection`
- BFF 组装：`dsh-api-remotes` 是 Host/Client 双面包
- 领域方法：`SessionsApi` / `HostApi` / `EventsApi` 等
- 协议消息：ClientRequest/ServerResponse/ServerRequest/ClientResponse；response echo `rpcId`

## 当前 Remote capability 是显式装配

- `dsh-api-remotes` 目前只 mount 了 Goal Remote 和 plugin inventory 等少数 capability。
- 它不是运行时自动发现所有 Host Service。
- 文档明说：新增 capability 需要显式 `/remote` value import + 在该 assembly 中 mount。

## 扩展大致路径

1. Host 侧定义/暴露 Remote capability（Typert Remote 或 API 方法）。
2. 在 `api-remotes` Host assembly 显式引入并挂载该 capability。
3. Client 侧 import 生成的 `/remote` 产物并 `ctx.remote.$mount()`。
4. 若需要把某个 Host cordis event 转发给浏览器，还要把它加入 `API_REMOTE_FORWARDED_EVENTS` allowlist。
5. 客户端只能 `ctx.remote.$on` allowlist 里的事件。

## 备选：不新增 Remote

如果只是给模型加能力，继续用 `ctx.tools.register()` + host 插件即可。

如果只是给 mint tab 拉数据，优先看现有 API/session projection 是否能覆盖：
- 自定义面板需要“issue 列表”时，通常还是应该走 Host RPC/Remote。
- 不要在浏览器端直接 spawn/读 mint CLI 或 db。

## 注意事项

- Remote 方法在 Host 侧解析 Service；per-session isolate 服务不一定能被 Remote 直接访问。
- POST 必须 `application/json`；业务错误走 RpcResult error，不靠 HTTP status。
- 客户端 Remote 集合是 build-time 固定的，不是动态发现。

## dsh-mint 结论

- mint 工具/模型能力走 `tool` 注册。
- mint issue 面板数据走 Host RPC/Remote；否则 UI 无法安全访问 host 侧 mint 能力。
- 若 mint 有事件要推给 UI（如 issue 状态变化），需要走 Host forwarded event allowlist，而不是另开 socket。
