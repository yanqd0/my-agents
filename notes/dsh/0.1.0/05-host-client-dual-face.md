# dsh 0.1.1-rc.2 Host/Client 双面插件链路

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 一句话

同一 npm 包可以同时有 host 半面和 browser 半面；host 由 `cordis.patch.yml` 普通行挂载，browser 由 `dsh.client` 声明 + `dsh-client-modules` 装载。

## package.json 关键声明

- `dsh.client`：浏览器面声明，形如 `{ platform:'web', inject?, immediately?, external? }`
- `exports["./client"]`：必须指向预构建的 browser bundle；缺失会 MissingClientBundleError
- `dsh.bundle.patch`：只有整包 bundle 使用，普通插件不需要

## 链路

1. Host 的 `cordis.patch.yml` 挂载一个“双面插件行”，包需有 browser half。
2. `dsh-client-modules` Node half 扫描已挂载行中带 `dsh.client` 的包。
3. Node half 解析各 `exports["./client"]`，构建 `window.__DSH_BOOT__` entry graph。
4. Host 在 `/plugins/<id>/client.js` 提供每个 client bundle。
5. 浏览器先用 `window.__ModuleLoader__` 注册 factory，再由 `client-runtime` 的 Cordis kernel 装载成真实插件。

## 双面插件如何识别

- 宿主面不靠 package.json 自描述；靠组合行 name + ESM export（`apply`/`inject`/`Config`）。
- 浏览器面必须靠 `dsh.client` 显式声明。
- “npm 装了”不等于 UI 已安装；必须先挂 host 行，且包内有 client bundle。

## 模块加载要点

- client bundle 是 lazy CJS：script 执行只注册 factory，副作用在 materialize 时执行。
- 动态依赖按图顺序 preload/注册。
- `external` 可声明 React/Cordis/静态库等共享 specifier。
- 修改客户端插件需重新 build client bundle；host 端可只热更 host JS。

## 与 UI Slot / 会话数据关系

- 浏览器侧有 `SlotRegistry`、`SessionRuntime`、`WorkspaceRuntime`。
- UI 通过 Slot 注册到 conversation view/sidebar/settings 等位置。
- Host 到浏览器数据一般经 API gateway + session/projection frames；不是自定义 WebSocket。

## dsh-mint 参考

- 0.2.0 mint tab 属于客户端半面，需要：
  - `dsh.client` 声明
  - 预构建 client bundle
  - 在 host 的已挂载 mint 插件行上让 `client-modules` 发现它
  - 用 Slot 注册 `conversation.view` 或其它 UI 位置

## 增补：Web Frontend 构建与静态资源

- web profile 使用 `dsh-web-frontend` 提供浏览器前端产物
- `dsh-host-frontend-static` 负责 dist fallback；实际服务路径通常挂在 webserver/web-runtime
- client bundle 由 host 从 `exports["./client"]` 读取并 serve：
  - 路径形如 `/plugins/<package-id>/client.js?rev=...`
  - rev hash 用于缓存失效
- client bundle 缺失会报 `MissingClientBundleError`；开发环境必须先 build client
- 官方开发流程通常有 `pnpm run dev:web` watcher：
  - 改写 client bundle 后由 `client-hmr` 做 invalidate/prefetch/fiber swap
- 第三方插件作者不能依赖开发仓库的 watcher；发布前必须预构建 client bundle
