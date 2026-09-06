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

## 反查用法

- **想了解 pi 上装了/设了什么** → 查 `pi-config.md`（现状表）与 `settings/pi/`。
- **想评估某个能力（plan/subagent/反问/MCP/审查…）要不要用哪个包** → 查
  `pi-extension-plugin-selection.md` 三档表。
- **要改 pi 配置或扩展** → 先读对应文档的「如何调整」/「版本锁定」节，避免破坏同步契约。
