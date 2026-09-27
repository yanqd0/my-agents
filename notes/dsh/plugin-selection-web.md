# dsh web profile 第三方插件清单：选择与评估

> 支撑 install.py `DSH_PLUGINS_BY_PROFILE["web"]` 的选型依据与**选入 / 挑出记录**。
> 初评对象 dsh 0.1.1-rc.2（快照 2026-09-06）；**0.1.7-rc.2 复评 2026-09-27**。目录/市场来源：
> [awesome-dsh-plugin](https://awesome-dsh-plugin.com)（dshmarket 插件市场的同源注册表）。
> 更新机制细节见 `skills-settings-loading.md` §四；本文件只记「选了什么、挑了什么、为什么」。

## 一、当前清单（选入）

install.py 单一真源 = 以下 **2 项**，全部装入 web profile。0.1.7-rc.2 实机验证可用。

| 声明 npm 名 | pnpm spec | 上游仓库 | 一句话用途 |
|---|---|---|---|
| `dshmarket` | `dshmarket`（npm） | [dsh-market/dsh-market](https://github.com/dsh-market/dsh-market) | 设置页内的社区插件市场：浏览/搜索/一键装/更新/备份（app 本体） |
| `dsh-whale-widget` | `dsh-whale-widget`（npm） | [MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget) | DSH Web 右下角余额/今日已用小鲸鱼挂件（UI 向） |

> 另有自研 `@yanqd0/dsh-mint`（本地 `link:`，见其仓库）装入同一 profile，不属本清单管理。

## 二、0.1.7 复评（2026-09-27）

dsh 升级到 0.1.7-rc.2（启用**会话格式 V4**、新增 **peer 兼容门禁**）后逐项复核：

| 插件 | 版本 | peer 门禁 | 实机启动 | 运行时 | 结论 |
|---|---|---|---|---|---|
| `dshmarket` | 1.66.1 | 通过 | 正常挂载 | 无落库旧格式 | ✅ 保留 |
| `dsh-whale-widget` | 0.3.15 | 通过（无 dsh peer） | 正常挂载 | 无落库旧格式 | ✅ 保留 |
| `graph-memory` | 1.6.0-beta.16 | 通过（peer 声明宽松，门禁抓不到） | 正常挂载 | ❌ 见下 | ⏸ 挑出 |
| `dsh-calculator` | 1.4.1 | ❌ 不通过 | dsh 跳过、不加载 | 依赖已移除的 `dsh-client-runtime` | ⏸ 挑出 |

判定依据：peer 门禁 = dsh 0.1.7 对 `@deepseek-ai/dsh-*` peer 做 semver 校验
（`dsh-app-boot` 的 `evaluatePluginCompatibility`）；实机启动 = 临时端口重跑 `dsh web` 抓 mount
警告；运行时 = 扫描已装插件的 V4 废弃写法（`kind:"plugin"`、`tool-result`、`header.system`、
`session.append`），仅 graph-memory 命中。

### 挑出记录

| 插件 | 挑出原因 | 恢复条件 |
|---|---|---|
| `graph-memory`（[adoresever/graph-memory](https://github.com/adoresever/graph-memory)） | 1.6.0-beta.16 仍以旧式 `source:{kind:"plugin"}` 调 `session.append`（`dist/src/format/dsh-compaction.js`、`dsh-turn-projection.js`）；dsh 0.1.7 会话格式 V4 写盘前拒绝 `kind:"plugin"`，一旦触发滚动压缩/工具轨迹归档即整轮失败：`format v4 message requires a producer-owned source kind`。上游 [issue #113](https://github.com/adoresever/graph-memory/issues/113)（open，无修复）。 | 上游合并修复（把落库 source 改为 `plugin:graph-memory` 等 V4 生产者 kind）后重新评估 |
| `dsh-calculator`（[bobcat848/dsh-calculator](https://github.com/bobcat848/dsh-calculator)） | 1.4.1 声明 peer `@deepseek-ai/dsh-client-runtime` / `@deepseek-ai/dsh-client-ui-slots` `@^0.0.1`，与 dsh 0.1.7 的 `0.1.7-rc.2` 不匹配 → 被兼容门禁拒绝加载；且 `dsh-client-runtime` 在 0.1.7 已被移除（其 client 注入 `dsh.client.inject` 指向不存在的包）。 | 作者更新 peer 范围（并处理 `dsh-client-runtime` 缺失）后重新评估 |

> 挑出即从 profile 卸载：`dsh plugin --profile web remove graph-memory dsh-calculator`
> （会同步移除 `package.json` 的 deps 与 `dsh.profile.bundles`）。
> **勿用临时改 `node_modules` 的方式绕过**：随重装/更新即失效，且掩盖真实兼容性问题。

## 三、选入评估（快照 2026-09-06，dsh 0.1.1-rc.2）

| 插件 | ★/fork | 开放 issue | 最近 push | npm 下载 | 评估要点与风险 |
|---|---|---|---|---|---|
| dshmarket | 3287 / 172 | 30 | 09-05 | ~300k | 成熟（日更节奏）；bundle patch 极小、只 insert 自身 id。装它后插件浏览/一键更新/备份多在 GUI 内完成，可覆盖本清单的手动 `--update`。风险：它是「装其它插件」的入口，会对任意目录源执行 pnpm——代码级信任仍是用户决策（README 明示 Listing ≠ endorsement）。要求 dsh web ≥ 0.1.0-rc.6 |
| dsh-whale-widget | 1797 / 68 | 33 | 08-24 | ~11k | 纯 UI 挂件；余额走 `api.deepseek.com/user/balance`（读 dsh 凭据缝 DEEPSEEK_API_KEY）；「今日已用」默认本地余额差记账（`.dshw-usage.json`），可选 `DEEPSEEK_PLATFORM_TOKEN`（平台网页会话 token，非 API key，注意保管）实时模式。bundle patch 只 insert 自身 id，无全局 config，面小 |
| ~~graph-memory~~ | 593 / 88 | 15 | 09-05 | npm 1.5.8 仅 OpenClaw | **已挑出**。原选 github 的原因：dsh 支持（`dsh.bundle`+cordis.patch）只存在于仓库 main（1.6.0-beta.x）；npm 最新 1.5.8 仍是纯 OpenClaw 插件 → 用 npm 名会装成无 bundle 的普通依赖（不激活）。行为级：接管「发给模型的历史」、本地 SQLite 于 `~/.dsh/graph-memory/`。风险：主分支 beta 直装=随 HEAD 漂移；语义召回需自备 key |
| ~~dsh-calculator~~ | 5 / 0 | 0 | 09-06 | 无 | **已挑出**。原评估：小但活跃，仓库自带 `lib/` 构建产物 → github 直装可用；host 半订阅会话 usage 记账 + `/user/balance` 30s 缓存；client 注入 `shell.overlay`。风险：单人项目、UI 对宿主插槽版本敏感 |

> 「dsh-calculator」消歧：市场条目 = bobcat848/dsh-calculator（无 npm 发布）。npm 同名
> `dsh-calculator@0.0.1` 是他人占位空壳（无 dsh.bundle）；`dsh-plugin-calculator` 是另一类
> （数学工具），均未选用。

## 四、选源规则（为什么 npm 与 github 混用）

- **registry npm spec**（当前选入的 market、whale）：上游已发布同版本 npm 包且声明
  `dsh.bundle`。国内镜像可用（`mirrors.cloud.tencent.com/npm` 命中）、安装快、更新检查直接
  `pnpm view`。
- **github spec**（已挑出的 graph-memory、calculator）：dsh 支持未发 npm / 无 npm 发布。仓库
  必须自带构建产物（dist/ 或 lib/）或 prepare 脚本，否则 plugin tree 崩溃（官方 discussion
  #3154）。install.py 候选源 = `github:` clone，失败自动退 codeload tarball。
- 升级语义（install.py 统一处理）：registry → `dsh plugin … update --latest <名>`；
  github → `dsh plugin … update <名>`（pnpm 重解析分支 HEAD）。已装重跑默认只**报告**
  新版本（registry 对比 / GitHub HEAD 对比），`--update` 才执行升级。

## 五、注意事项 / 运维

- **全自动自愈（install.py 已实现，无需手工编辑）**：安装失败时自动处理——① peer 自动安装
  无正式版（`ERR_PNPM_NO_MATCHING_VERSION`）→ 自动把 profile pnpm-workspace.yaml 的
  `autoInstallPeers` 置 `false`（**dsh initProfile 默认值**；host 内核 peer 经
  `profiles/node_modules` 闭包解析，不需要 auto-install）后重试；② 构建脚本被阻断 → 自动把
  pnpm 报出的包名加入 `allowBuilds` 后重试；③ GitHub 网络抖动 → 换备选源并多轮自动重试。
  改的是行级文本、保留注释，均幂等。
- **传输与回退**：`github:` spec 走 git https clone，github 偶发不可达 → install.py 自动退到
  `codeload.github.com` tarball（pnpm 自带 fetch，不经 git，更稳）。保持 https，**勿**按 dsh
  报错建议改用 SSH insteadOf。
- **profile 忙**：web 是正运行 GUI 的 profile；真实 add/remove/update 建议 profile 空闲时做，
  装完**重启 dsh web**（client 侧新包需 F5/重启才注入）。install.py 默认只报告、`--update`
  显式升级，正为避免静默改动运行中 profile。
- **主机内核包拦截层易被污染（0.1.7 复评发现）**：dsh 靠 `~/.dsh/profiles/node_modules`
  拦截层把 `@deepseek-ai/dsh-*` 路由到运行中的 host 版本；若 profile 自己的
  `node_modules/@deepseek-ai/*` 出现同名旧包（例：手动 `pnpm install` 把 dshmarket 的
  optional peer `@deepseek-ai/dsh-settings` 解析成 registry 旧版并 hoist），会**遮蔽 host**，
  启动报 `settings … this.load is not a function`。故 profile 的安装应由 install.py /
  `dsh plugin` 驱动，勿裸跑 `pnpm install`；发现污染时删除 profile 下 `@deepseek-ai/*` 后
  重启。另：dsh 由 npm-global 迁到 pnpm-global 后，`profiles/node_modules` 旧软链可能大范围
  失效（0.1.7 复评时 206 条中 197 条指向旧路径），需清掉让 dsh 重建。
- **凭据前提**：whale 依赖 dsh 凭据缝里的 `DEEPSEEK_API_KEY`（及可选平台 token），未配则对应
  功能缺失而非报错。
- **与 dshmarket 的关系**：装了 dshmarket 后其 GUI 的 per-plugin 更新同样覆盖已装插件；
  install.py 的角色收敛为「声明式装齐 + 每次重跑提醒更新」，二者互不冲突。
- **验证**：`dsh --profile web --dump-config | grep <名>` 见 bundles/entries；web 重启后
  右下角鲸鱼（选入）/ 设置→Plugin Market（选入）出现即生效。
