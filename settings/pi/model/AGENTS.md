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
3. **价格更新流程**：改官方价格 → 本文件核对/更新下面价格表与汇率 → 更新对应
   `*.json` 的 `cost` → `./install.py --target pi --force`（模型 `models` 数组为既有键，
   需 `--force` 才覆盖）→ 更新下面「已录价格」表。

## deepseek（V4 pro / flash，2026-09 官方定价）

官方按「百万 tokens」计价，区分 命中(cache hit)输入 / 未命中(cache miss)输入 / 输出，
并分 空闲/高峰 两档（空闲=高峰一半）。本仓库按**空闲档最低价**折算美元（USD/百万
tokens），汇率取 **1 元 = 0.1489 USD**（2026-09 行情，er-api/ECB 簇 ~0.1490）。

| 模型 | 输入·未命中 | 输入·命中(cacheRead) | 输出 | 备注 |
|------|-----------|--------------------|------|------|
| deepseek-v4-flash | 1.5元 = 0.2234 | 0.05元 = 0.007445 | 4.5元 = 0.6701 | cacheWrite 无单独费率=0 |
| deepseek-v4-pro | 4.5元 = 0.6701 | 0.15元 = 0.02234 | 13.5元 = 2.0102 | cacheWrite=0 |

`cost` 字段含义（pi models.md）：每百万 token 费率，美元；`input`=未命中输入、
`cacheRead`=命中输入、`cacheWrite`=缓存写入、`output`=输出。
