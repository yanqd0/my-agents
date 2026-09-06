# dsh web profile 第三方插件清单：选择与评估（2026-09）

> 支撑 install.py `DSH_PLUGINS_BY_PROFILE["web"]` 的选型依据与逐插件评估。评估对象版本
> dsh 0.1.1-rc.2 / profile=web 实机；数据快照 2026-09-06。目录/市场来源：
> [awesome-dsh-plugin](https://awesome-dsh-plugin.com)（dshmarket 插件市场的同源注册表）。
> 更新机制细节见 `skills-settings-loading.md` §四；本文件只记「选了什么、为什么、注意什么」。

## 一、清单（install.py 单一真源 = 以下 4 项，全部装入 web profile）

| 声明 npm 名 | pnpm spec | 上游仓库 | 一句话用途 |
|---|---|---|---|
| `dshmarket` | `dshmarket`（npm） | [dsh-market/dsh-market](https://github.com/dsh-market/dsh-market) | 设置页内的社区插件市场：浏览/搜索/一键装/更新/备份（app 本体） |
| `dsh-whale-widget` | `dsh-whale-widget`（npm） | [MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget) | DSH Web 右下角余额/今日已用小鲸鱼挂件（UI 向） |
| `graph-memory` | `github:adoresever/graph-memory`（备选 codeload tarball） | [adoresever/graph-memory](https://github.com/adoresever/graph-memory) | 知识图谱记忆：接管模型可见历史、跨会话图+向量召回 |
| `dsh-calculator` | `github:bobcat848/dsh-calculator`（备选 codeload tarball） | [bobcat848/dsh-calculator](https://github.com/bobcat848/dsh-calculator) | 右上角费用（会话/今日）+ 余额卡片（费用向） |

> 注意「dsh-calculator」消歧：市场条目 = bobcat848/dsh-calculator（无 npm 发布）。npm 同名
> `dsh-calculator@0.0.1` 是他人占位空壳（无 dsh.bundle），非本清单对象；`dsh-plugin-calculator`
> 是另一类（数学工具），均未选用。

## 二、逐插件评估（快照 2026-09-06）

| 插件 | ★/fork | 开放 issue | 最近 push | npm 下载 | 评估要点与风险 |
|---|---|---|---|---|---|
| dshmarket | 3287 / 172 | 30 | 09-05 | ~300k | 成熟（v1.44.0，日更节奏）；bundle patch 极小、只 insert 自身 id。装它后插件浏览/一键更新/备份多在 GUI 内完成，可覆盖本清单的手动 `--update`。风险：它是「装其它插件」的入口，会对任意目录源执行 pnpm——代码级信任仍是用户决策（README 明示 Listing ≠ endorsement）。要求 dsh web ≥ 0.1.0-rc.6（0.1.1-rc.2 满足） |
| dsh-whale-widget | 1797 / 68 | 33 | 08-24 | ~11k | 纯 UI 挂件；余额走 `api.deepseek.com/user/balance`（读 dsh 凭据缝 DEEPSEEK_API_KEY）；「今日已用」默认本地余额差记账（`.dshw-usage.json`），可选 `DEEPSEEK_PLATFORM_TOKEN`（平台网页会话 token，非 API key，注意保管）实时模式。bundle patch 只 insert 自身 id，无全局 config，面小。与 calculator 的余额功能重叠 → 二选一亦可（whale 偏装饰+记账，calculator 偏费用） |
| graph-memory | 593 / 88 | 15 | 09-05 | npm 1.5.8 仅 OpenClaw | **选 github 的原因**：dsh 支持（`dsh.bundle`+cordis.patch）只存在于仓库 main（1.6.0-beta.x，README 自述 beta、124/124 测试、实测基准公开），npm 最新 1.5.8 仍是纯 OpenClaw 插件 → 用 npm 名会装成无 bundle 的普通依赖（不激活）。行为级：接管「发给模型的历史」（默认保留最近 5 完成轮，旧历史图化），抽取只用「用户问题+最终回答」、本地 SQLite 于 `~/.dsh/graph-memory/`，可选 embedding/独立抽取模型经 env 配（无则 FTS5 降级），messageRetention 默认 keep all 不删原文。风险：主分支 beta 直装=随 HEAD 漂移；语义召回需自备 key；非纯展示类，装前确认想要「上下文接管」 |
| dsh-calculator | 5 / 0 | 0 | 09-06 | 无 | 小但活跃、README 详尽（v1.2.0+ 只兼容带 `shell.overlay` 插槽的 dsh ≥ rc.6；0.1.1-rc.2 满足）。仓库自带 `lib/` 构建产物 → github 直装可用。host 半订阅会话 usage 记账（fork 去重）+ `/user/balance` 30s 缓存；client 注入 `shell.overlay` 右上角浮层。风险：单人社区项目、无独立测试佐证，UI 对宿主插槽版本敏感（作者在 README 已列已知 z-index 兼容问题与解法） |

## 三、选源规则（为什么 npm 与 github 混用）

- **registry npm spec**（whale、market）：上游已发布同版本 npm 包且声明 `dsh.bundle`。
  国内镜像可用（`mirrors.cloud.tencent.com/npm` 命中）、安装快、更新检查直接 `pnpm view`。
- **github spec**（graph-memory、calculator）：dsh 支持未发 npm / 无 npm 发布。仓库必须自带
  构建产物（dist/ 或 lib/）或 prepare 脚本，否则 plugin tree 崩溃（官方 discussion #3154）。
  两仓库均自带产物；install.py 候选源 = `github:` clone，失败自动退 codeload tarball
  （两种传输 2026-09 均已在隔离 profile 实装验证，reconcile 后声明名入 bundles）。
- 升级语义（install.py 统一处理）：registry → `dsh plugin … update --latest <名>`；
  github → `dsh plugin … update <名>`（pnpm 重解析分支 HEAD）。已装重跑默认只**报告**
  新版本（registry 对比 / GitHub HEAD 对比），`--update` 才执行升级。

## 四、注意事项 / 运维

- **真实安装前置（一次，dsh-calculator 必需）**：web profile 的
  `~/.dsh/profiles/web/pnpm-workspace.yaml` 若为 `autoInstallPeers: true`，装 dsh-calculator
  会失败——它声明 peer `@deepseek-ai/dsh-client-runtime` / `dsh-client-ui-slots@^0.0.1`，
  而 npm 只有 `0.0.1-rc.1` 预发布、正式 0.0.x 不存在 → pnpm 自动装 peer 时报
  `ERR_PNPM_NO_MATCHING_VERSION`（与传输无关，本机 scratch 已实证）。改成
  `autoInstallPeers: false`（**dsh initProfile 默认值**；host 内核 peer 经
  `profiles/node_modules` 闭包解析，不需要 auto-install）即可，graph-memory/whale/market
  不受影响。install.py 检测到此类失败会打印该提示。
- **传输与回退（2026-09 实测）**：`github:` spec 走 git https clone，github 偶发不可达
  （RPC/connect 超时）→ install.py 自动退到 `codeload.github.com` tarball（pnpm 自带 fetch，
  不经 git，更稳；graph-memory/calculator 均已按两种传输在隔离 profile 实装成功并完成
  bundles reconcile）。保持 https，**勿**按 dsh 报错建议改用 SSH insteadOf。
- **graph-memory 无原生依赖**：仓库 main（1.6.0-beta.x，dsh 版）依赖仅 `@sinclair/typebox`；
  早期 npm 1.5.8（OpenClaw 版）才带 `@photostructure/sqlite`。故装 main 不需要 allowBuilds
  放行（若未来上游调整再按 install.py 提示处理）。
- **profile 忙**：web 是正运行 GUI 的 profile；真实 add/remove/update 建议 profile 空闲时做，
  装完**重启 dsh web**（client 侧新包需 F5/重启才注入）。install.py 默认只报告、--update 显式
  升级，正为避免静默改动运行中 profile。
- **凭据前提**：whale/calculator/graph-memory(可选 embedding) 依赖 dsh 凭据缝里的
  `DEEPSEEK_API_KEY`（及可选平台/向量 key），未配则对应功能缺失而非报错。
- **与 dshmarket 的关系**：装了 dshmarket 后其 GUI 的 per-plugin 更新同样覆盖这四个；
  install.py 的角色收敛为「声明式装齐 + 每次重跑提醒更新」，二者互不冲突。
- **验证**：`dsh --profile web --dump-config | grep <名>` 见 bundles/entries；web 重启后
  右下角鲸鱼/右上角费用卡/设置→Plugin Market 出现即生效。
