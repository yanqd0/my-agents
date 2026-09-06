# dsh 0.1.1-rc.2 HMR 与开发循环

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 有两套 HMR

| 类型 | 包/行 | 状态 |
|---|---|---|
| Loader/config patch HMR | `cordis-plugin-hmr`（base 的 `hmr` 行） | web/headless 中 `disabled:true` |
| 浏览器 client bundle HMR | `dsh-client-hmr`（web 插入的 `client-hmr` 行） | host 行挂着，dev watcher 改写 client 文件时才活动 |

- `cordis-plugin-hmr`：对 `cordis.patch.yml` / Loader tree 的 add/change/remove 做热更新
- `dsh-client-hmr`：SSE rebuilt frame → invalidate/prefetch → fiber swap
- 当前 web profile 把 shared HMR 关掉是 TODO：reload lifecycle 尚未测完

## 为什么开发插件经常要重启

- Host 侧 JS 插件本质是 ESM import；改源码后 Loader 不重新 import，需要重启 harness/进程。
- patch 热更新主要针对用户层 YAML 行变化；但实际开发中 dsh-mint 实测 touch patch 不一定热应用，以重启为可靠路径。
- Client 侧改 UI 必须重新 build client bundle，并由 client-hmr 或刷新页面加载。

## 常规开发循环

```bash
cd /home/user/yanqd0/dsh-mint
pnpm build
# host 插件重启后生效；验证：工具列表/系统提示出现
dsh web
```

## 可用验证命令

- `dsh --profile web --dump-config`：组合树 + patch 警告
- `dsh --profile web --dump-default-config`：不含用户层
- session log 位于 `$DSH_HOME/sessions/<proj>/<session>/`，可检查事件/工具是否真实发生

## 结论

- 当前版本对插件作者仍是 **build + restart 为主**。
- HMR 主要面向官方 bundle/UI dev，不承诺第三方插件源码热重载。

## 增补：Profile 初始化 / pnpm / 安装机制

- web/headless profile 首次使用自动从 template 初始化；其它 profile 需 `dsh plugin` 创建
- profile 目录关键文件：
  - `package.json`：`dsh.profile.bundles` 有序 bundle 列表 + 额外依赖
  - `cordis.yml`：空根，boot 时会重写
  - `cordis.patch.yml`：用户 patch 层
  - `pnpm-workspace.yaml`：pnpm 构建策略
- 裸包名从 harness 自身 node_modules 解析；`healProfilesModuleFallback` 维护 profiles/node_modules 的 symlink
- `dsh plugin --profile web add <pkg>` = 在 profile 目录跑 pnpm
- pnpm 11 默认拦截 build scripts：可能报 `ERR_PNPM_IGNORED_BUILDS`
  - 处理：`dsh plugin --profile web approve-builds --all` 后重试 add
  - 或 `dsh plugin --profile web add ./ --config.dangerouslyAllowAllBuilds=true`
- 第三方本地插件用相对/绝对路径时，ESM 需要指向 `dist/index.js` 文件，不能 import 目录
