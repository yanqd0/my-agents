---
name: my-git-tag
description: >-
  打语义化版本 tag，自动生成改动摘要并同步 CHANGELOG。
  当用户说"打tag/发布版本/打一个版本/创建tag/发版"时可自主调用；
  也支持用户显式通过 /my-git-tag 触发。
  预发布版本（alpha/beta/rc/dev）跳过 CHANGELOG，从 git log 归类生成 tag message；
  打 tag 前校验项目配置文件（Cargo.toml/package.json/pyproject.toml 等）中的版本号一致性。
allowed-tools: Bash(git:*,test:*) Read Edit Write Grep Skill question
---

打 `git tag`，支持一个可选参数：`<tag_name>`。

**交互约定**：文中"用 question"指调用宿主反问 tool（`question`/`ask_user_question`）；无交互 tool 或 headless 时退化为纯文本列出选项等用户回答。

## 执行步骤

### 1. 确定版本号

`Read` 宿主 skills 目录下 `my-changelog/references/next-version.md`（pi 为 `~/.agents/skills/my-changelog/references/next-version.md`），按其流程解析或推算版本号 — 提供 `<tag_name>` 则采用并校验格式，为空则自动推算下一个版本号；对用户非空输入做了调整（如修正格式）时须先用 `question` 请用户确认。记录输出的 `<version>`、`<last_tag>`、`<is_prerelease>`。

若 `<is_prerelease>` 为 `true`（预发布版本），跳过以下推算，直接进入步骤 2。

若 `<is_prerelease>` 为 `false`（正式版本），推算并确认下一开发版本：

1. `Read` `references/next-dev-version.md`，按其规则从 `<version>` 推算 `<next_dev_version>`（semver 格式，如 `0.6.0-alpha.1`）。
2. 检测项目类型（同步骤 4a 逻辑——用 `test -f` 检查全部标记文件，记录命中的类型。步骤 4 将复用此结果，无需重复检测）：
   - 全部未命中（无法识别项目类型）→ 记为 `<skip_config_update>` = true。
   - 命中一种或多种 → 记录项目类型。若命中多种，用 `question`（单选）让用户选择，选项仅列出命中的类型。
3. 按项目类型加载对应的 `version-check-*.md` reference，检查是否为动态版本方案（同步骤 4c.1 逻辑）：
   - 是动态版本（如 setuptools-scm、git-commit-id-plugin、semantic-release）→ 记为 `<skip_config_update>` = true。
   - 否 → 记录 `<skip_config_update>` = false。
4. 根据项目类型将 `<next_dev_version>` 转换为 `<next_dev_version_config>`（参照 `next-dev-version.md` 中的项目特定格式转换表）。
5. 用 `question`（单选）同时确认：
   - "确认：正式版本 `<version>`，下一开发版本 `<next_dev_version>`（推荐）" — 若 `<skip_config_update>` 为 true，附加"`（项目无需手动更新配置文件）`"。
   - "修改正式版本（在 Other 填写）"
   - "修改下一开发版本（在 Other 填写）"
   - "取消"
6. 若用户修改了版本号，刷新对应变量；若修改了正式版本，需重新推算下一开发版并再次确认。

### 2. 识别预发布版本

根据 `<is_prerelease>` 标识：
- **`true`**（版本含 `-alpha`/`-beta`/`-rc`/`-dev` 后缀）→ 跳过步骤 3（不写 CHANGELOG）。
- **`false`**（正式版本）→ 继续步骤 3。

### 3. 同步 CHANGELOG（仅正式版本）

使用 `Skill` 工具调用 `my-changelog`，传入版本号 `<version>` 与区间 `<last_tag>..HEAD`。my-changelog 会归类改动（Features / Bug Fixes / Others）、整合简化后写入 `CHANGELOG.md` 并提交。其归类结果保留在上下文中，供步骤 5 生成 tag message，无需重新分析 commit。

### 4. 项目类型检测与版本一致性检查

#### 4a. 检测项目类型

扫描项目根目录的全部标记文件，收集所有命中的项目类型：

| 项目类型 | 标记文件 | reference |
|----------|----------|-----------|
| Rust/Cargo | `Cargo.toml` | `references/version-check-cargo.md` |
| Python | `pyproject.toml`、`setup.cfg`、`setup.py` | `references/version-check-python.md` |
| npm/Node.js | `package.json` | `references/version-check-npm.md` |
| Java/Maven | `pom.xml` | `references/version-check-java.md` |
| Java/Gradle | `build.gradle`、`build.gradle.kts` | `references/version-check-java.md` |

- 用 `test -f` 检查**所有**标记文件（非命中即停），记录全部命中的类型。
- **全部未命中** → 跳过版本一致性检查，直接到步骤 5。
- **单一命中** → 直接采用该类型。
- **多类型命中**（如 monorepo 同时存在 `Cargo.toml` 和 `package.json`）→ 用 `question`（单选）让用户选择要检查的类型，选项仅列出命中的类型。

#### 4b. 加载版本检查规则

根据检测到的项目类型，`Read` 对应的 reference 文件（见上表）。

#### 4c. 执行一致性检查

按 reference 指引：
1. **动态版本检测**：先检查项目是否使用基于 git tag 的动态版本方案（如 Python 的 setuptools-scm、Java 的 git-commit-id-plugin）。命中则跳过检查，告知用户"项目使用动态版本方案，跳过配置文件校验"。
2. **读取项目配置版本**：从配置文件中提取当前版本号。
3. **版本号比较**：
   - Python 项目：将 `<version>` 按 reference 中的 PEP 440 映射规则转换为 PEP 440 格式后比较。
   - 其他项目：去掉 `<version>` 的 `v` 前缀后直接比较。
4. 一致 → 跳过步骤 4d。
5. 不一致 → 进入步骤 4d。

#### 4d. 不匹配时处理

用 `question`（单选）提供以下选项：
- **"更新项目配置文件以匹配 tag `<version>`"**：按 reference 中的修复方法自动更新配置文件。修改后不提交，继续后续步骤。
- **"调整 tag 名称以匹配项目配置的版本"**：将项目配置中的版本号覆盖 `<version>`。若配置版本格式与 tag 格式不一致（如 Python PEP 440 `0.1.0a1`），先按 reference 的映射规则**反向转换**为 semver（`0.1.0a1` → `0.1.0-alpha.1`），再根据 `<last_tag>` 的 `v` 前缀惯例添加或省略前缀。调整后返回步骤 2 重新判断（可能在预发布/正式版本间切换，影响 CHANGELOG 是否写入）。
- **"继续执行，不修复版本差异"**：忽略差异，tag 和配置各自保持当前值。（若宿主有记忆层则记录此决策。）
- **"取消此次操作"**：终止流程，不做任何修改。

### 5. 生成 tag message

**正式版本**：基于步骤 3 my-changelog 的归类结果整形为 tag message 格式（与 CHANGELOG 条目同源，仅改呈现）：
- 自动生成一句概括性的大版本标题（中文，≤50 字符），概括本次版本的主要变化方向。
- 分类标题用 `##`（不含版本号标题行），按「首行标题 → 空行 → Markdown 正文」格式：

```
<概括性标题，≤50字符>

## Features

- 改动描述 1。

## Bug Fixes

- 修复描述 1。

## Others

- 其它改动 1。
```

- 无内容的分类直接省略，不输出空标题。

**预发布版本**：自行分析 commit 记录生成完整格式的 tag message：
- 以 `<version> 预发布` 作为概括性标题。
- 读取 `git log <last_tag>..HEAD`（`<last_tag>` 不存在时取全部历史），分析每条 commit 的标题+正文。
- 按与 my-changelog 相同的归类逻辑分为 Features / Bug Fixes / Others：
  - `Features`：仅新增功能（feat 类 commit）。
  - `Bug Fixes`：仅 bug 修复（fix 类 commit）。
  - 其余（重构、文档、CI、样式等）→ `Others`。
  - 同一版本内新增又删除的功能、引入又修复的 bug，互相抵消不写入。
  - 无内容的分类整体省略。
- 输出格式与正式版本一致：首行标题 + 空行 + `## Features` / `## Bug Fixes` / `## Others`。

### 6. （可选）发版前审查/测试

打 tag 前，若宿主具备审查/测试能力（如 subagent/reviewer、测试 runner），可先对项目做发版前核查；
不具备则跳过、不阻塞。**如做了审查且发现需修复项，先经 my-git-commit / my-git-amend 修复提交后再打 tag。**

### 7. 执行 git tag

审查通过、修复完毕后，打 tag：

```bash
git tag -a <version> -m "<message>"
```

- 正式版本：tag 打在步骤 3 my-changelog 产生的 CHANGELOG 提交上（若无新提交则打在 HEAD）。
- 预发布版本：tag 直接打在 HEAD。

### 8. 更新项目配置文件为下一开发版本

仅 `<is_prerelease>` 为 `false` 时执行；预发布版本跳过本步。

1. **跳过条件检查**：
   - `<skip_config_update>` = true（动态版本或无法识别项目类型）→ 告知用户原因，直接到步骤 9。
   - 步骤 1 中用户自定义了 `<next_dev_version>` → 直接采用用户值，仅做格式转换。
2. **更新配置文件**：按步骤 4 检测到的项目类型，参照对应 `version-check-*.md` 中的修复方法，用 `Edit` 将版本字段替换为 `<next_dev_version_config>`：
   - Rust：`Cargo.toml` 中 `[package]` 下的 `version = "..."`
   - npm：`package.json` 中 `"version"` 字段
   - Python：`pyproject.toml` 中 PEP 621 `/` Poetry 或 `setup.cfg` `/` `setup.py`
   - Java：`pom.xml` `<version>` 或 `build.gradle[.kts]` `version=`，若原版本含 `-SNAPSHOT` 则保留后缀
3. **提交**：直接 `git add` + `git commit`（不用 `my-git-commit`，确保提交信息确定可预测）：
   ```
   chore: bump version to <next_dev_version_config> for next development cycle
   ```

### 9. （若宿主有记忆层）保存摘要

若宿主具备记忆能力则保存以下摘要；无记忆层则跳过，不影响打 tag 结果：
- 版本号 `<version>`
- 是否为预发布版本
- 版本类型（Rust/Python/npm/Java/无）
- 版本一致性检查结果（一致/已修复/跳过/忽略差异）
- tag message 摘要（概括性标题）
- 下一开发版本 `<next_dev_version>`（如适用）
- 下一开发版本更新结果（已更新/跳过-动态版本/跳过-预发布/跳过-未知类型）
