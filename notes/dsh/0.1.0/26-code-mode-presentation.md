# dsh 0.1.1-rc.2 Code Mode / Tool Presentation

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 概念

- `dsh-tools.mode`：`native | code | both`
- `dsh-agent-tool-presentation`：preset 里声明本 agent 用哪种 tool presentation
- `dsh-code-runtime`：抽象 code runtime
- `dsh-code-runtime-worker-thread`：worker_thread 实现

## 各 mode 含义

| mode | 模型看到 |
|---|---|
| native | 普通每个工具 schema |
| code | 只暴露 `run_code` + 生成的 TypeScript SDK + “只准调 run_code”规则 |
| both | 原生函数 + run_code 都可用 |

- code mode 下模型直接调用其它工具会解析成 `UNKNOWN_TOOL`。
- preset 里加 `tool-presentation` 行即可让该 agent 使用 code mode。
- 没有该行的 agent 使用 deployment 默认（native）。

## Worker-thread Runtime 设计要点

- 每次 run 使用一个全新 worker，无 pooling。
- TypeScript 可执行 erasable syntax；top-level await/return 可用。
- 隔离性：独立 isolate、空环境、heap cap、可强杀。
- 限制默认：computeMs=60000、maxWallMs=600000、maxOutputBytes=64MiB、heap 512MB。
- worker 内没有环境变量/凭据；工具绑定通过 message port 传 JSON。
- 信任姿态：**containment 不是安全边界**，约等于 bash 信任。

## Code Mode 适用场景

- 让模型用一段 TypeScript 程序组合多个工具调用，减少 round trip。
- 适合“批量文件操作、链式查询、流程编排”类任务。
- UI/卡片展示仍由工具结果流回后渲染，不改变 host 侧工具语义。

## dsh-mint

- 若 mint 使用场景是频繁连续 CLI 查询，code mode 可减少 round trip。
- 但 mint 仍应优先提供简单原生工具给通用 agent；code mode 作为可选 preset 增强。
- mint 插件本身不需要 code mode；只是可被 code 预设的 run_code 调用。
