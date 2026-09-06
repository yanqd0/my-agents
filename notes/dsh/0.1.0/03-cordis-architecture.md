# dsh 0.1.1-rc.2 Cordis 插件系统与 dsh 架构

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## Cordis 核心概念

- `Context`：依赖容器/作用域，运行时 proxy
- `plugin(ctx)`：安装插件，返回 `Fiber`
- `Fiber`：插件生命周期/清理单元
- `Service`：服务基类，需注册到 ctx
- `inject`：声明依赖；未声明而直接访问会报错
- `ctx.isolate(name, label)`：为服务创建独立作用域
- loader/include/group/timer/hmr 是官方周边包

## dsh 启动结构

```
dsh CLI
 └─ prepareProfile：组合 profile 的 patch 层
     └─ boot()：建 root Context + 装 Loader + Include
         └─ 读 cordis.yml / 应用 patches
             └─ 插件按需 import 并启动
```

## Profile patch 分层

```
空根 []
 ├─ dsh.profile.bundles 各 bundle patch（dsh-base -> dsh-web-app）
 ├─ profiles/<name>/cordis.patch.yml
 ├─ $DSH_HOME/cordis.patch.yml
 └─ --patch overlay
```

Patch 语义：
- `- id: x ...` = 覆盖/禁用既有行；config 整行替换
- `- insert: [...]` = 新增行
- 新插件必须 `insert:` 包起来

## Module 解析

- `cordis:` 内置
- `.` / 相对路径：相对 profile 或 preset 目录
- 裸包名：从 harness 自身 node_modules 解析
- 绝对路径：必须指向 ESM 文件，不能 import 目录

## Host plane vs Agent plane

- Host plane：跨会话共享的注册表/服务，由 bundle 挂载
  - session、persistence、sandbox/approval、LLM route、subagent registry、API gateway、webserver
- Agent plane：每会话可见的工具/prompt，由 `agent-presets` 按 preset 装配
  - Web 把 base 的模型工具 disable，再由 standard/code/cordis/minimal 在会话作用域启用
  - 注册行必须放进 `isolate` realm，避免不同会话/预设服务冲突

## 双面插件（Host + Browser）

- 宿主面：`cordis.patch.yml` 行挂载，普通 Cordis 插件契约
- 浏览器面：包内 `dsh.client` 声明；由 `client-modules` 扫描已挂载行，生成 `window.__DSH_BOOT__`，加载 `/plugins/<id>/client.js`
- 仅有 npm 依赖不等于 UI 已安装；必须先挂 host 行

## 开发结论

- dsh 0.1.1-rc.2 是“薄 CLI + 配置驱动的 Cordis 树”
- 插件的识别不靠 package.json 的 dsh 字段；靠 Cordis 模块导出（apply/inject/Config）
- `dsh.bundle.patch` 只用于整包 bundle
- `dsh.client` 只用于浏览器半边

## 增补：dsh CLI / app flags

- dsh 只解析自己的 launcher flags；之后的参数交给 booted profile
- launcher flags 在前，第一个不认识的 token 开始 app 参数
- `cmdlineArgs` 以不可变快照注入树中，web-startup/headless-startup 等插件读取
- `--dump-config` 输出完整树；`--dump-default-config` 不含用户层与 --patch
- `dsh plugin --profile <name> <pnpm args>` 实际转发到 profile 目录执行 pnpm

## 增补：boot fail-loud / shutdown

- `boot()` 挂完 include 树后会 `assertEntriesLoaded/Activated`
  - enabled 但没有 fiber = 启动失败
  - pending 服务 / failed plugin = 启动失败并报告
- `installFailLoud` 把 unhandled boot/Loader rejection 转成一行错误 + exit(1)
- SIGINT/SIGTERM 走 bounded shutdown：默认约 5s，dispose 后退出
- dispose 会清理 fiber/effect；卡住时强制退出
- `watchUserPatches` 热更新失败保留 last-good tree，不把进程带崩
