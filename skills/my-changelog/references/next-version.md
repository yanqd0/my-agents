# 目标版本号判断

确定「这次要处理的版本号」——在 my-changelog 语境下即**当前版本**（正在整理的版本），在 my-git-tag 语境下即**下一个 tag**。两者共享本逻辑（my-changelog 通过 `references/next-version.md`、my-git-tag 通过宿主 skills 目录下 `my-changelog/references/next-version.md` 引用同一份）。

## 输入

- 可选 `<version>`：调用方或用户显式指定的版本号。命中即直接采用，仅做下方「格式校验」。

## 判断流程（命中即停）

1. **已指定版本号** → 直接采用，跳到「格式校验」。
2. **自动判断**：
   - `git describe --tags --abbrev=0` 取最近一个 tag（记为 `<last_tag>`；仓库无任何 tag 则视为首个版本）。
   - `Grep`（pattern `^## `）取 CHANGELOG.md 最新（最上）一行，跳过 `[Uu]nreleased` 等非版本占位符。从匹配行提取 `## ` 之后、第一个空格或行尾之前的 token 作为 `<top_ver>`（去日期、括号注解等尾部文本，如 `## 0.1.0 (2026-07-18)` → `0.1.0`，`## [0.1.0]` → `0.1.0`，`## 0.1.0` → `0.1.0`）。用 `git tag -l <top_ver>` 和 `git tag -l v<top_ver>`（若 `<top_ver>` 不带 `v`）或 `git tag -l <top_ver_no_v>`（若带 `v`）双向检查是否已有对应 tag：
     - **`<top_ver>` 无对应 tag** → 它就是目标版本（未发布、正在积累），直接采用 `<top_ver>`。
     - **`<top_ver>` 已有对应 tag**，或 CHANGELOG 为空/不存在 → 目标版本是其后尚未记录的新版本，按下一步语义化推算。
3. **语义化推算**（依据 `<last_tag>..HEAD` 区间内 commit 的性质）：
   - **`<last_tag>` 是正式版本**（不含预发布后缀）：破坏性变更 → 升 MAJOR；新功能（feat）→ 升 MINOR；仅修复/杂项（fix/refactor/docs/ci…）→ 升 PATCH。结果不含预发布后缀。
   - **`<last_tag>` 是预发布版本**（含 `-alpha`/`-beta`/`-rc`/`-dev` 后缀）→ 使用 `question`（单选）询问用户下一步：
     - "继续当前阶段：`<next_phase>`"（如 `<last_tag>` 为 `v0.1.0-alpha.1`，则选项为 `v0.1.0-alpha.2`）
     - "推进到下一阶段：`<next_stage>`"（alpha → beta → rc → 正式；如 `v0.1.0-alpha.1` 之后为 `v0.1.0-beta.1`）
     - "正式发布：`<release>`"（去掉预发布后缀，如 `v0.1.0`）
     - 选项版本号均由推算得出：继续当前阶段则递增 `.N`，下一阶段取对应后缀 `.1`，正式发布去掉后缀。`-dev` 特殊处理：下一阶段为 `-alpha.1`，正式发布为去掉后缀的正式版本。
   - **不明确时询问**：若变更性质无法明确对应单一 bump（如 `1.0.0` 之后可能是 `2.0.0` / `1.1.0` / `1.0.1`）→ 使用 `question` 列出候选版本号请用户选择，不擅自决定。

## 格式校验

- **格式一致**：自动生成的版本号，`v` 前缀与 `<last_tag>` 保持一致（上一个带 `v` 则带，不带则不带）。
- **手动输入**：可带 `v` 可不带。
- **校验**：须符合以下格式之一（可带 `v` 前缀）：
  - 正式版本：`[v]MAJOR.MINOR.PATCH`（如 `v1.0.0`、`0.1.0`）
  - 预发布版本：`[v]MAJOR.MINOR.PATCH-<prerelease>[.N]`
    其中 `<prerelease>` 为 `alpha`、`beta`、`rc`、`dev` 之一，`.N` 为可选数字后缀（省略时默认为 `.1`）。
    示例：`v0.1.0-alpha.1`、`1.2.0-beta.2`、`v2.0.0-rc.1`、`v0.1.0-dev`。
  - 不符合格式则尝试修正并告知用户修正内容。
- **确认调整**：若对用户非空的输入做了任何调整（修正格式、改动版本号等），继续前须用 `question`（单选）请用户确认，选项如"采用调整后的 `<version>`"、"保留原输入"、"改用其它（在 Other 填写）"。

## 输出

- `<version>`：确定的目标版本号（可能为正式版本如 `v1.0.0`，或预发布版本如 `v0.1.0-alpha.2`）。
- `<last_tag>`：上一个 tag，供调用方组装区间 `<last_tag>..HEAD`。
- `<is_prerelease>`：布尔值。版本含 `-alpha`/`-beta`/`-rc`/`-dev` 后缀时为 `true`，供调用方决定是否跳过 CHANGELOG 同步。
