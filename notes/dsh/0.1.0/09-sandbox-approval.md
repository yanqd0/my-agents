# dsh 0.1.1-rc.2 沙箱与审批体系

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 分层

| 包 | 角色 |
|---|---|
| `dsh-sandbox` | 抽象沙箱 seam（ctx.sandbox） |
| `dsh-sandbox-local` | 本地后端：bwrap/landlock/Seatbelt/Windows ACL；探测失败 fail-closed |
| `dsh-sandbox-policy` | 每调用策略解析；默认 workspace-write |
| `dsh-bash-sandbox` / `dsh-pwsh-sandbox` | shell 执行器；所有命令经 ctx.sandbox |
| `dsh-fs-sandbox` | 文件读写边界；写/编辑按 sandbox mode 裁决 |
| `dsh-user-approval` | 审批 seam；默认 fail-closed |
| `dsh-permission-presets` | 产品层权限预设：sandbox mode + approval 组合 |

## 权限预设

| preset | sandbox | approval |
|---|---|---|
| read-only | read-only | ask |
| workspace-write | workspace-write | ask |
| danger-full-access | danger-full-access | never |

- 默认 mode：`workspace-write`
- 可通过 `DSH_PERMISSION_MODE` 改部署默认
- approval 在 danger-full-access 下自动 never；否则 ask

## 文件效应边界

- workspace-write：可写 workspace/cwd 与临时区；workspace 外写会被拒
- 沙箱只缝在 shell 工具与 fs 工具
- **插件直接 `child_process.spawn` 不自动经过该沙箱**——宿主信任代码能绕开
- dsh-mint 的 mint CLI 走“宿主信任子进程”直接 spawn，所以任何会话模式都可用；模型手动跑 mint 命令才受沙箱约束

## 审批瀑布

- `ctx.approval` 未组合时，工具 `ask` 降级 deny
- 审批通常是异步 user question/approval answerer 组成瀑布
- 单次允许可在同会话内被 dsh-mint 的 B-v2 gate 记住，后续 mint 提权自动放行

## 关键结论

- 沙箱是“文件效应策略”，不是命令白名单。
- 它是进程内策略，不隔离受信任 host 插件代码。
- 想给 mint 双 root（workspace + mint 数据目录）目前无法直接表达；可写根集合在沙箱实现中固定。

## 增补：提问 / 审批 UI 全链路

- 抽象提问：`dsh-user-questions`（ctx.userQuestions）
- 工具 ask 走 approval waterfall，question 走 user-questions；两者最终都可能接管 composer
- 浏览器端：
  - `SessionSummary.pendingInteraction` 标出 `approval` / `plan-review` / `question`
  - composer takeover：ui-user-questions、ApprovalPanel 等注册到 `conversation.composer`
  - 用户回答后通过 `/api/respond` 或对应 RPC 回到 Host，挂起请求被 settle
- Host 侧请求会被验证 pending request；bad/mismatched response 会拒绝
- 插件发起“向人提问”的正确方式：
  1. 不要直接造 UI/自己弹窗
  2. 调用 `ctx.userQuestions` / approval seam
  3. Host 通过现有协议推给浏览器 composer takeover
- 没有 UI/answerer 时 `ask` 应降级 deny（fail-closed），不能阻塞无头流程
