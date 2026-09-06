# skills 复用架构：my-claude submodule + 软链拼装

> 记录 my-agents 如何复用 my-claude 的 skill 设施、避免双份维护。含一次走弯路的纠正，
> 避免重蹈。落地于 0.1.0（plan #4）。

## 结论（当前架构）

- **my-claude = 只管 Claude Code 自身**（Claude 专属内容），不承担跨宿主职责，**不做任何
  面向 my-agents 的中性化改写**。
- **my-agents = 跨宿主层**，经 `vendor/my-claude`（git submodule，相对 URL `../my-claude`）
  引入上游，skills **通过软链拼装**：
  - 整 skill 内容与 pi 需求一致 → 整目录软链；
  - `SKILL.md` 因宿主差异（Claude 用 `AskUserQuestion`，pi 用 `question`）→ **本地各写各的**，
    不入共享；
  - 与上游字节一致的中性 references/scripts → 软链自 submodule（单源）；
  - 纯 pi 专属 references（如 my-image-vision 走 DeepSeek 而 claude 走 Anthropic）→ 本地留。

## 落地细节

- 25 个字节一致中性 references/scripts 已软链 `vendor/my-claude`（commit `5f2ddc1`）；
  submodule 引入为 `b7a99e8`（相对 URL、钉 origin `42115b5`）。
- 本地维护：全部 pi `SKILL.md` + 差异 references（`next-version.md` / `commit-split.md` /
  `version-check-npm.md` / `analysis-framework.md` / `writing-guide.md` / `describe.py` 等）。
- install.py 对齐上游 my-claude：**扁平 CLI（无子命令）**，默认安装、`--revert` 卸载，
  配 `--dry-run`/`--yes`/`--force`；内置 `_verify_nested_links`（失效软链）与
  `_audit_dedup`（实体副本本应软链）两类守卫（commit `2984fed`/`c6517d2`）。

## 后续变更怎么做

- **共享中性内容**改动 → 在 my-claude 仓库提交 → 回 my-agents bump `vendor/my-claude` 子模块指针。
- **pi 专属差异**改动 → 在 my-agents 本地对应文件改。
- 别把共享文件改成 my-agents 内的实体副本（去重守卫会在安装时 warn）。

## 走过的弯路（教训）

- 最初把"复用"理解成 **把 my-claude 中性化成跨宿主 canonical**（机制 Y：正文逐字一致 +
  每宿主 allowed-tools 覆盖），已在 my-claude 做了 my-mermaid / my-code-io 的中性化改写，
  被用户纠正回撤。
- 原因：**my-claude 应该只管自己（Claude Code），不需要为 my-agents 这套跨宿主机制服务**；
  真正的复用方向是 my-agents 作为消费者，用 submodule + 软链拼装，而非改上游。
- 借鉴：跨宿主想复用宿主仓库内容时，优先"下游软链消费 + 本地覆盖宿主差异"，不要反向改造上游。
