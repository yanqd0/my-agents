# dsh 0.1.1-rc.2 Agent Preset 生命周期

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 入口

- 包：`@deepseek-ai/dsh-agent-presets`
- Web 层 host 行：`agent-presets`，`config.default: standard`
- 根目录：shipped `config/agent-presets/` + `$DSH_HOME/.agent-presets`（user）
- 文件：目录内 `agent.cordis.yml` + 可选 `preset.yml`（仅展示信息）

## 核心生命周期

- preset 是一个“standing mount”：每个进程每个 preset 只装配一次。
- 会话通过 scope parent chain 加入预设：`agent -> preset -> global`。
- 预设里的工具/prompt 注册进 preset 自己的 scope layer，对所有 join 的 agent 可见。
- 同一 preset 多个 session 共享同一实例；内部状态按 Session/Agent key 隔离。
- 换 preset 只允许 blank agent（尚未产生任何内容），否则破坏已记录工具历史。

## 关键 API

| API | 作用 |
|---|---|
| `agentPresets.defaultId` | 默认预设 id |
| `list()` / `resolve(id?)` | 列出/解析预设 |
| `mount(agentCtx, id?)` | 为 agent 装配预设 |
| `composeFrom(agentCtx, parentCtx)` | 子代理直接 join 父代理的预设 |
| `recompose(agentCtx, id)` | 空白会话切换预设 |
| `read/copy/remove` | 读取/复制/删除 user preset |

## 会话与预设状态

- 创建 header 记录启动时的 preset id。
- 会话切换后写 `agent-preset/selected` session event。
- 冷读历史时必须 resolve 当前运行预设，不能只看 header。
- 子代理通过 `composeFrom()` join 父代理，而不是重新 `mount()`。

## 写插件需知

- 若 preset 行提供 Service，必须放进带 `isolate` 的 group，否则多会话/多预设会冲突。
- bare `@deepseek-ai/dsh-*` 包名从 host 解析，不从 preset 目录解析。
- 相对路径从 preset 自己的目录解析；绝对路径需指向文件。
- 可复制 shipped preset 到 `$DSH_HOME/.agent-presets` 后再改。

## 对 dsh-mint 的意义

- 若想按项目/仓库用不同 mint 配置，可做自定义 preset 或 preset 内注册 mint 工具/上下文。
- 要修改运行时预设能力，应 copy 一份 preset 文件到 user root，不要改 shipped install。
