# notes 索引（项目记忆）

> `notes/` 是**特殊项目文档**（给 AI / 内部开发者）：记录技术选型、设计决策、宿主现状等
> 不可从代码直接看出的信息。本文档是全部 notes 的**索引**，便于快速定位与发现。
>
> **维护规则**：新增/删除/改名任一 notes 文件，或某文档关键结论/状态变化，必须在下方登记
> 一行（可含一句定位 + 现状 + 关键决策）。此文件本身不作备注，只当索引。

## 文档清单

| 文件 | 主题 / 定位 | 现状 / 关键结论 | 关联 |
|------|------------|----------------|------|
| `my-agents-skills-reuse.md` | skills 复用架构**决策**：my-claude submodule + 软链拼装 | my-claude=只管 Claude Code（不做跨宿主中性化）；my-agents 经 `vendor/my-claude` submodule + 软链拼装，SKILL.md/pi 专属 references 本地留；25 中性文件已软链；install.py 扁平 CLI/`--revert`。曾走弯路（把 my-claude 中性化成 canonical）已纠正 | vendor/my-claude、install.py、AGENTS.md |
| `pi-extension-plugin-selection.md` | pi 扩展/插件**技术选型**：T0/T1/T2 三档政策与候选清单 | T1 采用**「(B) 动态软链已装 pi」**（曾选 (a) 收编 vendor，已重审撤销并清历史）；T2 落地前需审源码+锁版本 | tools/pi-examples.sh、install.py 扩展步、issue #9-#12 |
| `pi-config.md` | pi 宿主**配置现状与默认值速查**：已生效键↔片段对照 + 未配置默认 | 快照 2026-09-05、pi 0.85.0；改配置须三处同步（当前片段表 + 本文 + README） | settings/pi/ |
| `dsh/skills-settings-loading.md` | dsh 宿主 skills/settings **加载机制** + **插件管理框架**（issue #8/#17/#34/#35） | skills：`~/.agents/skills` 被 dsh 直接读（filesystem 提供方 user-agents 根 rank500），与 pi 同源零插件；settings：`~/.dsh/settings.yaml` YAML namespace；dsh **无 pi models.json/cost 对应物**；插件：经 `dsh plugin --profile <p> add/remove`，清单 `DSH_PLUGINS_BY_PROFILE`（当前空，仅框架） | install.py #17/#35 |
| `dsh/architecture.md` | dsh **运行架构总览**：profile/bundle/插件/前端(web·headless)/skill·context·hook/overlay patch 契约；dsh 资料库政策 | dsh 官方资料稀缺，本文件 + `notes/dsh/` 为 dsh 知识库**持续补充**；版本依据 0.1.1-rc.2/profile=web 实机；overlay `--patch` 语法已定案，实际交付留首个真实消费方（issue #36） | issue #36、notes/dsh/ 全目录 |

> **dsh 资料库（notes/dsh/）**：dsh 官方资料少，涉及 dsh 的调研/决策持续归入 `notes/dsh/`
> 下新建或增补文件，并在上方文档清单登记；勿散落到 notes/ 根目录。

## 反查用法

- **想了解 pi 上装了/设了什么** → 查 `pi-config.md`（现状表）与 `settings/pi/`。
- **想评估某个能力（plan/subagent/反问/MCP/审查…）要不要用哪个包** → 查
  `pi-extension-plugin-selection.md` 三档表。
- **要改 pi 配置或扩展** → 先读对应文档的「如何调整」/「版本锁定」节，避免破坏同步契约。
- **想了解 dsh 机制**（profile/bundle/插件/前端/skill·context·hook/overlay patch）→ 查
  `notes/dsh/architecture.md`；dsh skills/settings 落点 → `notes/dsh/skills-settings-loading.md`。
