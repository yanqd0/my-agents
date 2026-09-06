# dsh 0.1.1-rc.2 Typert / API Gateway / Remote RPC

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 组件

| 包 | 作用 |
|---|---|
| `dsh-typert-registry` | 生成包反射 + Zod schema 运行时注册表 |
| `dsh-typert-loader` | Typert 包贡献集成进 Loader |
| `dsh-api-gateway` | host 端 Typert Remote 分发 |
| `dsh-host-apiproxy` | HTTP 可用的 ApiProxy gateway |
| `dsh-api-remotes` | Remote BFF 组装；Host Agent/Session lookup |
| `dsh-client-connection` | 浏览器传输层（POST + SSE/WebSocket-down） |

## Wire 形态

四个象限的 discriminated union：

- ClientRequest：POST `/api/<method>`
- ServerResponse：POST 的 response body
- ServerRequest：SSE 推给 client 的 frame
- ClientResponse：POST `/api/respond` body

所有 response 都 echo 请求的 `rpcId`；不会新建其它 id。

## 方法契约

- `RpcMethodMap` 注册方法；`SessionsApi` / `HostApi` / `EventsApi` 等领域接口定义参数/返回值。
- Zod schema 校验两层：envelope 先，业务 payload 后。
- 业务错误走 `RpcResult` error branch，HTTP status 只表达 carrier。
- POST 必须 `application/json`，否则 415。

## 常见 Host push

- `session/projection` frame：session 投影变化推送
- `session/jobs` frame：后台任务快照
- `session/queue` frame：待处理用户消息快照
- `host/*` frame：workspace/session 列表变化
- `agent-preset/selected` 等非 scope 事件可被 client-safe 类型导出

## 客户端消费

- browser `api-remotes` / `client-runtime` 把远程调用接到本地 object/scope 模型。
- UI 插件通常不直接手写 WebSocket；通过 Remote/typed API + projection store 读写。
- Host 端 Remote 方法在 host plane 解析服务，因此被 Remote 调用的服务通常不能放进 per-session realm。

## 插件开发提示

- 如果自定义 client 要读 host 数据，优先看现有 Remote/API 是否够用；不够再扩展契约。
- Remote 方法找 Service 是 host 侧解析；不能假设它能看到某个 preset 的 isolate 服务。
- 只给自己 client 用的领域数据，可参考 session projection 机制（host 计算 → push frame）。
