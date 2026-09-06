# dsh 0.1.1-rc.2 Agent 预设热编辑 / 动态 Cordis（tool-cordis）

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 定位

- `dsh-tool-cordis`：模型可调用的 Cordis 工具集
- `dsh-cordis-host-runner`：宿主侧 vm 沙箱 + 动态 package 生命周期
- `dsh-cordis-client-runner`：浏览器侧加载动态 package 的 client half

## 五个工具

| 工具 | 作用 |
|---|---|
| `cordis_inspect` | 只读查看服务、fiber、工具、动态包、client slots |
| `cordis_define` | 记录 package（host code / client code），只语法检查，不运行 |
| `cordis_run` | 在 vm 中运行 host half，并广播 client half 到页面 |
| `cordis_stop` | 停止并清理 host/browser 贡献 |
| `cordis_undefine` | 停止并遗忘定义 |

## 生命周期

- define → run → stop → undefine
- 动态包只存在进程内存，**不落盘、不写 cordis.yml、不跨重启**
- 定义是 session-scoped：只在该会话可见/可控
- run 一个带 browser half 的包会走人批准 round trip

## 信任边界

- vm 沙箱隔离 globals，但**不是安全边界**；模型写的代码可触及 host realm
- 加载 `tool-cordis` 等于给模型 shell access
- 普通开发/生产插件仍走正式 profile/pnpm 安装，不应依赖动态包持久化

## 对 dsh-mint / 学习价值

- 这是“agent 自改运行时”的实验面，适合做 preset 原型、快速验证 UI slot。
- 想长期/跨重启使用，仍要把代码写成真实插件并挂载到 profile。
- `cordis_inspect` 可快速查看当前服务、事件、slots，是插件开发的强诊断工具。
