# dsh skills / settings 加载机制（0.2.0 调研）

> 承接 issue #8：在 my-agents 支持 `--target dsh` 前，摸清 dsh 读 skills/settings 的
> 方式，结论落地 `install.py` 的 dsh 宿主布局。调研对象为运行中的 `dsh web`
> （`@deepseek-ai/dsh` 0.1.1-rc.2，profile=web），宿主定位依据 dsh-mint skill 的
> `references/agent/dsh.md`。

## 结论速览

- **skills：`~/.agents/skills/` 被 dsh 直接读，无需额外 plugin/配置**。这正好是 pi 用的
  共享位置 → dsh 与 pi 走**同一份 skills 落点**（跨宿主复用成立）。
- **settings：dsh 的配置是 `~/.dsh/settings.yaml` 的分层 namespace 文档**（默认模型路由
  在 `agent-default-model` 段）；模型清单/计价**不存用户可编辑文件**，由 provider 插件
  （`dsh-llm-deepseek` 的 `models` 配置等）承载 → **dsh 无 pi `models.json` 对应物**。
- **install.py --target dsh**：只装 skills（复用既有 `~/.agents/skills` 软链步）；dsh 首版
  不引入 settings/models 片段（无 cost 文件可合并，且 dsh settings 为个人 harness 配置）。

## 一、skills 来源（dsh 如何发现技能）

技能经 `ctx.skills` 分层注册表（`@deepseek-ai/dsh-skill`）聚合各 provider；本地文件系统由
`@deepseek-ai/dsh-skill-filesystem` 提供。其默认扫描根（按 rank 升序，越靠后越外层、越弱）：

| Rank | source | 路径 | 说明 |
|---|---|---|---|
| 100 | `project-dsh` | `<projectRoot>/.dsh/skills` | 项目级（最近 `.git` 祖先） |
| 200 | `project-agents` | `<projectRoot>/.agents/skills` | 项目级共享 |
| 300 | `custom` | `Config.customSkillDirs` | 显式自定义根 |
| 400 | `user-dsh` | `<dshHome>/skills`（默认 `~/.dsh/skills`） | 跳过 `.system` 子目录 |
| 500 | `user-agents` | `<agentsHome>/skills`（默认 `~/.agents/skills`） | `$DSH_AGENTS_HOME` 可覆盖 |

- **`~/.agents/skills` 是内置默认用户根**（rank 500），开箱即用、零配置。本会话实证：
  available skills 的 base 目录即 `/home/user/.agents/skills/…`（mint、my-* 全在此），
  确证 dsh 直接消费该共享位置。
- 只识别一层 bundle（`<root>/<name>/SKILL.md`）或平铺 `<name>.md`；不支持嵌套 `**/SKILL.md`。
- 项目根 `.dsh/skills`/`.agents/skills`（rank 100/200）**会遮蔽**同名的用户级技能。
- 结论：my-agents 把 skills 软链到 `~/.agents/skills/`（与 pi 相同）即可被 dsh 使用，
  无需在 dsh profile 挂额外插件。

## 二、settings 落点与格式

- **文件**：`~/.dsh/settings.yaml`（默认，`dsh-settings-file` 提供方，`$DSH_HOME` 下；
  也可 `.json`，扩展名定格式）。分层解析：schema 默认值 ← 插件组合 `base` ← 用户文档段。
- **namespace**：各插件注册自己的段；本机 `agent-default-model` 段含 `provider/model/
  reasoningEffort`（默认路由）。写入是「读-改-写」的叶子级 diff，保注释/保其它段，跨进程持锁。
- **profile 组合**：每 profile 在 `~/.dsh/profiles/<profile>/`，`cordis.yml`（空 entry 列表）
  叠 `cordis.patch.yml`（用户 patch 层）与插件包 `package.json` 的 `dsh.profile` bundles。
  模型 provider 插件级配置（如 `llm-deepseek` 的 `models` 清单/容量/`apiKeyEnv`）放这里，不是
  用户可移植文件。
- **模型/计价**：dsh 无 pi 式 `models.json`（模型定义 + cost 价格）可深合并；模型路由由
  provider 插件配置，用量/token 计量由 provider 上报 + `dsh-token-meter` 启发式，非用户文件。
  → my-agents 对 dsh **不**提供 model cost 片段（与 pi 的关键差异）。

## 三、install.py --target dsh 布局建议（落 #17）

对照现有 `HOSTS["pi"]` 结构，dsh 只需：

```python
"dsh": {
    "name": "dsh",
    "skills_src": "skills",
    "skills_dest": HOME / ".agents" / "skills",   # 与 pi 同；dsh 自动发现(rank500)
    # settings：dsh 为 YAML namespace 文档、个人 harness 配置；首版不深合并（settings_src=None）
    # model：dsh 无 cost 文件对应物（provider 插件管理）→ 不装（model_src=None）
}
```

- skills 安装/回滚逻辑已 host 无关（skills_src/skills_dest），dsh 复用同一共享目标即可。
- settings/models：dsh 置空（None）。若日后确需写 dsh 默认模型路由，作为独立需求单列，
  且以「写/不覆盖其它 namespace」的 YAML 语义实现（非 JSON 深合并），默认 dry-run 提示。

## 四、与 pi 差异对照

| 项 | pi | dsh |
|---|---|---|
| skills 目录 | `~/.agents/skills`（需 pi 递归发现） | `~/.agents/skills`（同；自动，rank500） |
| settings 文件 | `~/.pi/agent/settings.json`（JSON deep-merge） | `~/.dsh/settings.yaml`（YAML namespace；非纯 merge） |
| 模型/cost 文件 | `~/.pi/agent/models.json`（含 cost） | 无（provider 插件管理） |
| extensions 自动发现 | 官方 examples 软链进 `~/.pi/agent/extensions` | 无对应（skill 即扩展；插件走 profile） |

## 五、未决 / 待确认

- `~/.dsh/skills`（rank 400）与本项目 `~/.agents/skills`（rank 500）并存时 dsh 的取用排序：
  rank 500 更外层，理论上 user-dsh(400) 优先；实际当前 `~/.dsh/skills` 为空，未实测冲突。
- 是否需为 dsh 提供 `settings/dsh/*` YAML 片段（如默认模型路由）→ 待真实需求再定，暂不建。
