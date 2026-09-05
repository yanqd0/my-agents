# settings/pi — pi 宿主设置片段

顶层 `*.json`（本目录）由 `install.py --target pi` deep-merge 到
`~/.pi/agent/settings.json`。**模型定义与价格**在 `model/` 子目录，deep-merge 到
`~/.pi/agent/models.json`（见 `model/AGENTS.md`）——两者合并目标不同，故分开。

## 设计原则（首版）

1. **只放宿主无关、安全、可加性**的偏好：遥测/分析关闭、安静启动、compaction、
   启动模型默认、技能命令等。
2. **模型处理**：模型**定义与价格**（models.json）固化在 `model/` 子目录片段；
   `apiKey`/auth **永不入库**——deep-merge 默认**不覆盖**已有标量键，保证本地
   `apiKey` 不被片段覆盖。provider/model 的**运行选择**（`defaultProvider`/
   `defaultModel`/`defaultThinkingLevel`）属用户偏好，可按需放本目录片段；deep-merge
   默认不覆盖已存在的标量键，需覆盖才用 `--force`。
3. `_` 前缀文件（如 `_xxx.json`）默认跳过安装，用 `./install.py --force` 显式启用。

## 新增片段

1. settings 片段键**逐键对照 pi settings 文档**的合法键；模型定义走 `model/` 子目录
   （对照 pi models.md + 该目录 AGENTS.md 的价格表）。
2. settings 片段落地为 `settings/pi/<name>.json`；默认跳过/实验项用 `_` 前缀命名。
3. **验证 deep-merge 不覆盖**用户已有键：用户 settings 的标量键优先于片段键，仅
   `--force` 才覆盖；可用 `./install.py --target pi --dry-run` 预览不落盘。
4. 在下方「当前片段」表登记该片段（含 `model/` 子目录项）。

## 当前片段

| 文件 | 内容 | 说明 |
|------|------|------|
| `default.json` | `quietStartup`、`enableInstallTelemetry:false`、`enableAnalytics:false` | 安静启动 + 关遥测/分析 |
| `startup.json` | `defaultProvider:deepseek`、`defaultModel:deepseek-v4-flash`、`defaultThinkingLevel:low` | 启动模型默认（当前仅 deepseek） |
| `compaction.json` | `compaction.enabled`、`reserveTokens:100000`、`keepRecentTokens:25000` | 1M 窗口留 100K 输出 → 约 900K 触发压缩；保留近期 25K |
| `model/deepseek.json` | deepseek-v4-pro/flash 定义 + RMB cost（元/百万 tokens） | → models.json；价格/来源见 `model/AGENTS.md` |

## 与现状文档的对应（改动必同步）

本目录片段经 `install.py --target pi` deep-merge 落地到 `~/.pi/agent/settings.json` 与
`models.json` 后，成为 **pi 实际运行配置**。已生效键的**现状 + 来源片段对照表**固化在
[`notes/pi-config.md`](../../notes/pi-config.md)（§2），另有「尚未配置、跟随 pi 默认值」的
速查（§3）与完整调整流程（§4）。

**同步契约**：任何片段新增/删除/改值、或真实 pi 配置发生与片段相关的变更，必须同步更新：

1. 上方「当前片段」表（含 `model/` 项）；
2. `notes/pi-config.md` §2 现状表（改值 + 刷新「现状日期」）；若改动触及 §3 默认值取向或
   片段命名规则，也一并校正；
3. `README.md`（涉及片段/能力增减时）。

**反向约束**：`notes/pi-config.md` 描述的默认值/键语义以 pi 官方 `docs/settings.md` 为权威，
pi 升级后若键或默认值漂移，以 pi 文档为准更新片段与现状表。
