# pi 宿主配置现状与默认值速查

> 受众：**人 + AI**。用于对齐「pi 当前实际生效的配置」与「pi 官方默认值」，
> 并指导下次如何调整、以及如何与本仓库 `settings/pi/` 片段保持同步。
> 适用 pi 版本 **0.85.0**（对齐其 `docs/settings.md` / `models.md` / `compaction.md`；
> 升级 pi 后若设置键/默认值变化，需回看本文并校正）。

## 0. 配置落地位置

| 文件 | 作用 | 是否入库 |
|------|------|---------|
| `~/.pi/agent/settings.json` | **全局**设置（所有项目） | 片段来源见 §2；apiKey 永不入库 |
| `~/.pi/agent/models.json` | 自定义 provider / model 定义 + 价格 | 片段来源见 §2 |
| `.pi/settings.json` | 项目级设置（**本项目未使用**） | 无 |
| `~/.pi/agent/auth.json` | provider 认证存储 | 不入库（敏感） |
| `~/.pi/agent/trust.json` | 项目信任决策 | 不入库（本机） |
| `~/.pi/agent/models-store.json` | pi 内部缓存的模型商店 | 不入库（生成物） |
| `~/.pi/agent/bin/`、`sessions/` | 用户脚本 bin、会话记录 | 不入库（生成物） |

仓库侧对应源码：`settings/pi/*.json` → `~/.pi/agent/settings.json`；
`settings/pi/model/*.json` → `~/.pi/agent/models.json`。两者由 `install.py --target pi`
deep-merge 落地。**路径上下文**：settings.json 里相对路径以 `~/.pi/agent` 解析。

## 1. 设计原则（本仓库采用，务必遵守）

- **只放宿主无关、安全、可加性**偏好；`_` 前缀文件默认跳过安装，`--force` 显式启用。
- **模型定义与价格**走 `model/` 片段；`apiKey`/auth **永不入库**。
- deep-merge 默认**不覆盖**用户已有的标量键 → 本地 `apiKey` 等安全。需覆盖才 `--force`。
- 隐私/体验类默认会**显式关闭**（见 §2），其余一律**跟随 pi 默认**（最小配置，见 §3）。

## 2. 当前已生效配置（现状 2026-09-14）

### 2.1 settings.json 已生效键

| 键 | 当前值 | pi 默认 | 来源片段 | 说明 |
|----|-------|---------|---------|------|
| `quietStartup` | `true` | `false` | `default.json` | 隐藏启动头部，安静启动 |
| `enableInstallTelemetry` | `false` | `true` | `default.json` | 关匿名安装/更新 ping + provider 归属头 |
| `enableAnalytics` | `false` | `false` | `default.json` | 显式关分析（与默认同，明确表态） |
| `defaultProvider` | `deepseek` | — | `startup.json` | 启动 provider |
| `defaultModel` | `deepseek-flash` | — | `startup.json` | 启动模型（当前仅 deepseek；V4.1-Flash） |
| `defaultThinkingLevel` | `low` | — | `startup.json` | 启动思考级别 |
| `compaction.enabled` | `true` | `true` | `compaction.json` | 开自动压缩 |
| `compaction.reserveTokens` | `100000` | `16384` | `compaction.json` | 1M 窗口留 100K 给 LLM 输出 |
| `compaction.keepRecentTokens` | `25000` | `20000` | `compaction.json` | 保留近期 25K 不摘要 |
| `lastChangelogVersion` | `0.85.0` | — | pi 自动写入 | 非片段管理，忽略 |

> `compaction` 语义：`reserveTokens` = 为 LLM 响应预留的 token；`keepRecentTokens` =
> 不被摘要的近端 token。1M 窗口配 100K 预留 → 接近窗口上限时触发压缩；保留 25K。

### 2.2 models.json 已生效

provider **deepseek**（`settings/pi/model/deepseek.json`）：

| 字段 | 值 |
|------|-----|
| `baseUrl` | `https://api.deepseek.com` |
| `api` | `openai-completions` |
| `apiKey` | 本地**手动补**（片段不含；deep-merge 不覆盖，安全） |
| 模型 | `deepseek-v4-pro`（`input:["text"]`）、`deepseek-flash`（V4.1-Flash，`input:["text","image"]`），各含 `contextWindow:1000000`、`maxTokens:384000`、`reasoning:true`、`cost`（元/百万 tokens，空闲档）、`compat`（`requiresReasoningContentOnAssistantMessages`、`thinkingFormat:"deepseek"`、`reasoningEffortMap`） |

价格源见 `settings/pi/model/AGENTS.md`（DeepSeek 官方按百万 tokens、命中/未命中/输出 +
空闲/高峰两档；直接录**空闲档人民币原值**，不做 USD 折算——pi 的 `cost` 为无币种数值，
仅算术累加并以 `$` 前缀显示，填入的元/百万token 原值让 TUI 花费数字直接等于人民币）。

### 2.3 auth / trust

- `auth.json`：保存 deepseek 的 key（`pi /login` 维护），不入库。
- `trust.json`：记录已信任项目文件夹（含 `.pi` 资源/项目 skills 的目录）。

## 3. 尚未配置、跟随 pi 默认的键（可按需调整）

> 以下键当前**未写入** `settings.json`，即采用 pi 默认。完整权威清单见 pi
> `docs/settings.md`；下表为**值得关注**的子集，按块分类并给出本仓库的建议取向。

### 3.1 模型与思考

| 键 | 默认 | 建议 |
|----|------|------|
| `hideThinkingBlock` | `false` | 保持（展示思考过程利于审查） |
| `showCacheMissNotices` | `false` | 保持关闭（减少噪音） |
| `modelThinkingLevels` | — | 未配；如需按模型差异化思考级别再设 |
| `thinkingBudgets` | — | 未配；默认即可，用不到自定义预算 |

### 3.2 UI / 显示 / 终端

| 键 | 默认 | 建议 |
|----|------|------|
| `theme` | `"dark"` | 未配，跟随默认 |
| `externalEditor` | `$VISUAL`/`$EDITOR` | 未配，继承环境变量即可 |
| `doubleEscapeAction` | `"tree"` | 保持 |
| `tuiMode` | `"regular"` | 保持（未开实验性 fullscreen） |
| `terminal.images` | `"auto"` | 保持自动协商图像协议 |

### 3.3 项目信任（headless 安全，重要）

| 键 | 默认 | 建议 |
|----|------|------|
| `defaultProjectTrust` | `"ask"` | **保持 `ask`**：headless（`-p`/json/rpc）下无交互提示时，按 `ask`/`never` 不加载项目 `.pi` 资源与项目扩展。如需脚本免提示跑项目可临时 `--approve`/`-a`，勿全局放开 |

### 3.4 重试（Retry）

| 键 | 默认 | 建议 |
|----|------|------|
| `retry.enabled` | `true` | 保持 |
| `retry.maxRetries` | `3` | 保持 |
| `retry.baseDelayMs` | `2000` | 保持 |
| `retry.provider.maxRetries` | `0` | **保持 0**（文档明确建议；>0 会让 SDK 层吞掉超限错误致卡住） |
| `retry.provider.maxRetryDelayMs` | `60000` | 保持 |

### 3.5 资源加载

| 键 | 默认 | 建议 |
|----|------|------|
| `packages` / `extensions` / `skills` / `prompts` / `themes` | `[]` | 当前未配：skills 走 `~/.agents/skills` 递归发现，无需在此列。`extensions` 由 `install.py` 把**已装 pi 包**白名单官方 example 软链到 `~/.pi/agent/extensions/`（不写 settings；见 `notes/pi-extension-plugin-selection.md` §(B)） |
| `enableSkillCommands` | `true` | 保持（skills 注册为 `/skill:name`） |

### 3.6 其它（默认即可）

- `defaultTools`（未设 → pi 标准内置工具集）；`enabledModels`（Ctrl+P 循环模型，未配）。
- `httpProxy`（未配；无需代理时不要设）。
- `warnings.anthropicExtraUsage`（`true` 默认；deepseek 无关，可不管）。
- `markdown.mermaid`（`"streaming"`）；`markdown.codeBlockIndent`（`"  "`）。

> 完整键表（含各类 cosmetic 项）见 pi `docs/settings.md` 的 *All Settings* 各块；
> 价格键语义见 pi `docs/models.md` 的 *Model Configuration*；压缩细节见 `docs/compaction.md`。

## 4. 如何调整 + 与仓库同步（下次改配置必走）

1. **判断归属**：属「模型定义/价格」→ 改 `settings/pi/model/<provider>.json`；
   属「偏好/隐私/体验」→ 改/新增 `settings/pi/<name>.json`（可 `_` 前缀暂缓）；均对照
   pi `docs/settings.md` 合法键。
2. **落地**：`./install.py --target pi --dry-run` 预览 → `./install.py --target pi`
   （覆盖既有键才 `--force`；模型 `models` 数组为既有键需 `--force`）。models 首次需
   手动在 `~/.pi/agent/models.json` 补 `apiKey`。
3. **验证**：`cat ~/.pi/agent/settings.json`（或 models.json）确认 deep-merge 未误覆盖
   用户键。
4. **三处同步（缺一不可）**：
   - 本 notes §2「现状」表（更新值 + 现状日期）；
   - `settings/pi/AGENTS.md`「当前片段」表与片段说明；
   - `README.md`（若涉及片段/能力增减）。
5. **提交**：`git commit`（中文规范信息），随后 `mint issue state commit` 关联到对应 issue。

> 变更配置后回看 §2.1/§2.2 表保证文档与落地一致；pi 版本升级时回看 §0 版本与 §3 默认值是否漂移。
