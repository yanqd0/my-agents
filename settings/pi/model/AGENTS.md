# settings/pi/model — 模型定义与价格片段

`*.json` 由 `install.py --target pi` deep-merge 到 `~/.pi/agent/models.json`（provider/model
定义 + 各模型 `cost`）。与 `settings/pi/*.json`（→ `~/.pi/agent/settings.json`）分开存放，
因两者合并目标不同。

## 原则

1. **不入库 apiKey/auth**：片段只含 provider 的 `baseUrl`/`api`/`models`（模型 + 价格）。
   本地 `models.json` 里的 `apiKey` 是标量键，deep-merge 默认**不覆盖**，故本仓库片段可
   安全分发；首次安装后需手动在 `~/.pi/agent/models.json` 补 `apiKey`。
2. **价格来源 URL 固化于此**（此文件作为各模型价格引用清单，未来新增模型在此追加）：
   - DeepSeek V4：<https://api-docs.deepseek.com/zh-cn/quick_start/pricing/>
3. **价格更新流程**：改官方价格 → 重访官方定价页核对原值（勿用汇率反推）→ 更新
   下面价格表与对应 `*.json` 的 `cost` → `./install.py --target pi --force`（模型
   `models` 数组为既有键，需 `--force` 才覆盖）→ 更新下面「已录价格」表。
4. **币种直接用人民币原值，不做 USD 折算**：`cost` 是无币种纯数值（pi 只做算术、
   硬编码 `$` 前缀显示）。DeepSeek 按人民币计费，故直接填官方「元/百万 tokens」
   原值，TUI 里 `$0.xxx` 的数字即 ¥0.xxx 金额（符号为 $，自行心读为 ¥）。

## deepseek（V4 pro / flash，2026-09 官方定价）

官方按「百万 tokens」计价，区分 命中(cache hit)输入 / 未命中(cache miss)输入 / 输出，
并分 空闲/高峰 两档（空闲=高峰一半）。本仓库取**空闲档**（最低价）人民币原值直接
入库（来自官方定价页 <https://api-docs.deepseek.com/zh-cn/quick_start/pricing/>）。

| 模型 | 输入·未命中(`input`) | 输入·命中(`cacheRead`) | 输出(`output`) | 备注 |
|------|---------------------|----------------------|------|------|
| deepseek-v4-flash | 1.5元 | 0.05元 | 4.5元 | cacheWrite 无单独费率=0 |
| deepseek-v4-pro | 4.5元 | 0.15元 | 13.5元 | cacheWrite=0 |

`cost` 字段含义（pi models.md）：每百万 token 费率；`input`=未命中输入、
`cacheRead`=命中输入、`cacheWrite`=缓存写入、`output`=输出。数值为人民币原值，
无币种换算；pi 仅算术累加并以 `$` 前缀显示。
