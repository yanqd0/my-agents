# dsh 0.1.1-rc.2 默认开关评估

> 基于 dsh 0.1.1-rc.2 的已安装代码评估。dsh 为早期版本，不承诺 API/机制稳定；后续新版本需要重新评估比对。

## 开（当前 web profile 默认）

- Web server：`127.0.0.1:3080`
- Agent 默认模型：`deepseek-official / deepseek-v4-flash`
- Bash 工具/沙箱：POSIX 开；PowerShell：仅 win32
- fs 读写、glob/grep：开
- 后台任务 / goal / skill / subagent / workflow 注册表：开
- 沙箱：`workspace-write`
- 审批：`ask`（danger-full-access 下 `never`）
- web 搜索：开；web_fetch：关
- 会话持久化、标题、checkpoint：开
- 默认 agent preset：`standard`
- code-runtime host 挂载；Code Mode 不作为默认展示

## 关（默认不启用）

- shared HMR：web-app 里 `hmr.disabled=true`（headless 也关）
- 全文会话搜索：`session-query-sqlite.openAt=never`，只保留精确读/标题/workspace
- Session telemetry：`mode=DISABLED`，需 `DSH_TELEMETRY_MODE=FULL|FEEDBACK_ONLY`
- web_fetch：`fetch=false`
- skill-badge：`disabled=true`
- Code Mode/PTC：默认不用；需 code preset 或 `DSH_TOOLS_MODE=code`
- codex/claude-code 子代理：disabled（未安装 provider）
- llm-pi-ai：dormant，需 settings 提供 provider
- `@yanqd0/dsh-mint`：package.json 已装 link，但未在 cordis.patch.yml 挂载
- headless profile：未初始化

## 环境变量开关

| 变量 | 含义 |
|---|---|
| `DSH_PERMISSION_MODE` | read-only/workspace-write/danger-full-access |
| `DSH_TOOLS_MODE` | native/code/both；不设=native |
| `DSH_TELEMETRY_MODE` | FULL/FEEDBACK_ONLY |
| `DSH_TELEMETRY_DISABLED` | 非空即硬关 |
| `DSH_TELEMETRY_OTLP_URL` | 覆盖 OTLP 地址 |
| `DSH_CWD` | minimal/fs-local 可覆盖 cwd |
| `DEEPSEEK_API_KEY` | 聊天/搜索凭据 |

## 关键机制说明

- patch 对已存在行是“整行 config 替换”，不是 merge。
- Web 层把 base 的模型工具先禁用，再通过 agent-presets 在会话层按 preset 启用。
- 当前 profile 无用户 patch（`cordis.patch.yml=[]`），无 home patch。
