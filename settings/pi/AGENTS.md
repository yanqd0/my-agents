# settings/pi — pi 宿主设置片段

`*.json` 由 `install.py --target pi` deep-merge 到 `~/.pi/agent/settings.json`。

## 设计原则（首版）

1. **只放宿主无关、安全、可加性**的偏好：遥测/分析关闭、安静启动、技能命令等。
2. **不放 provider/model/thinking/auth**：pi 的模型与登录是用户本地配置
   （`models.json`/`auth.json`/settings 里的 `defaultProvider` 等），由用户自己管理。
   仓库不存，避免 merge 时误覆盖用户选择。deep-merge 默认**不覆盖**已存在的标量键，
   需覆盖才用 `--force`。
3. `_` 前缀文件（如 `_xxx.json`）默认跳过安装，用 `./install.py --force` 显式启用。

## 新增片段

1. 片段键**逐键对照 pi settings 文档**的合法键，且只放宿主无关/可加性偏好（见设计原则）。
2. 落地为 `settings/pi/<name>.json`；默认跳过/实验项用 `_` 前缀命名。
3. **验证 deep-merge 不覆盖**用户已有键：用户 settings 的标量键优先于片段键，仅
   `--force` 才覆盖；可用 `./install.py --target pi --dry-run` 预览不落盘。
4. 在下方「当前片段」表登记该片段。

## 当前片段

| 文件 | 内容 | 说明 |
|------|------|------|
| `default.json` | `quietStartup`、`enableInstallTelemetry:false`、`enableAnalytics:false` | 安静启动 + 关遥测/分析 |
