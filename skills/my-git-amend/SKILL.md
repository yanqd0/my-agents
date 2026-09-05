---
name: my-git-amend
description: >-
  将当前或指定范围的提交合并为一个，生成规范的中文提交信息。当用户说"合并提交/squash/amend/
  整理提交历史/压缩提交/合并到上一个/合并最近N个"时，可自主调用；也作为其他 skill 的提交整理工具被调用。
  本技能可自主调用，也支持用户显式通过 /my-git-amend 触发。
allowed-tools: Bash(git:*) Read question
---

将修改合并到已有提交。可接收一个可选参数 `<target>`。

**交互约定**：文中"用 question"指调用宿主反问 tool（`question`/`ask_user_question`）；无交互 tool 或 headless 时退化为纯文本列出选项等用户回答。

## 核心原则

所有校验在写操作前完成，确保执行阶段不会因逻辑问题出错。唯一可能导致破坏的情况是并发 git 写操作（概率极小）。回退流程主要应对用户后悔，其次应对小概率并发错误。

## 执行步骤

### 1. 解析 `<target>` 参数

按以下优先级链解析，命中即停：

- **(a) 无参数** → 标准 amend：将整个工作区修改（含已暂存和未暂存）合并到 HEAD。
  - 先检查工作区是否干净：`git diff --cached --quiet && git diff --quiet`。
  - **若完全干净**：提示"工作区干净，无任何修改可合并"，**终止流程，不执行任何操作**。
  - 若有修改：走标准 amend 路径，无需后续的范围确认和校验步骤。提交命令为 `git commit -a --amend`。
- **(b) 纯数字**（如 `3`、`10`，`/^\d+$/` 匹配）→ 软重置到 `HEAD~<N>`，将最近 N 个提交合并为 1 个。
  - 目标为 `HEAD~<N>`，合并时**不包括该目标 commit**（即合并 `HEAD~<N>..HEAD` 这 N 个提交）。
  - 先 `git rev-list --count HEAD` 确认 N 不超过历史深度，超出则提示并拒绝。
- **(c) 直接提交引用**（7-40 位十六进制 SHA1、或含 `^`/`~` 操作符的引用如 `master^`、`HEAD~3`）→ 合并时**包括该目标 commit**。
  - `git cat-file -t <arg>` 返回 `commit` 即为有效。
  - 重置目标为 `<target>^`（目标 commit 的父提交），使目标的变更也纳入 squash。
  - 若 `<target>^` 无效（目标为 root commit，无父提交），提示"目标 commit 是根提交，无法纳入合并范围"并终止。
- **(d) 命名引用**（本地分支、远程分支 `origin/xxx`、tag 等，`git rev-parse --verify <ref>^{commit}` 成功且不在 (b)(c) 中）→ 合并时**不包括该引用指向的 commit**。
  - 重置目标为 `<ref>` 本身，即合并 `<ref>..HEAD` 范围内的提交。
  - 对 tag 额外注意：tag 默认不可修改，此处即使 tag 指向的 commit 不被合并，tag 也保持不变。
- **(e) 自然语言描述** → 按语义映射到 (a)-(d) 分支：数量表达（"最近 N 个"→b）、范围表达（"从 xxx 之后"→c/d）、包含表达（"包括 xxx"→c）、amend 意图（"合并到上一个"→a）。**无法明确解析时**用 `question`（单选）列出候选方案请用户选定，选项为各候选范围及其一句话说明。

### 2. 确定合并范围并校验

确定将被合并的提交范围（`<range>` 为 `git log` 可接受的区间表达式）：

- **标准 amend**：跳过此步骤，直接跳转到步骤 4 生成提交信息。
- **有目标范围**：计算 `<range>` 和 `<reset_target>`：
  - (b) 纯数字 N → `range = "HEAD~N..HEAD"`，`reset_target = "HEAD~N"`
  - (c) 直接提交引用 → `range = "<target>^..HEAD"`（含目标），`reset_target = "<target>^"`
  - (d) 命名引用 → `range = "<ref>..HEAD"`（不含目标），`reset_target = "<ref>"`

执行以下**所有校验**，任一不通过则终止并提示用户：

1. **祖先关系**：`git merge-base --is-ancestor <reset_target> HEAD`，不通过则提示"目标不是 HEAD 的祖先，无法合并"。
2. **tag 保护**：遍历范围内每个 commit，检查是否有 tag 指向它。**有则终止**，提示"范围包含 tagged commit，已设 tag 的提交不能被合并"。
   - `for commit in $(git rev-list <range>); do git tag --points-at "$commit" | grep -q . && echo "终止：$commit 上有 tag" && exit 1; done`
3. **范围非空**：`git rev-list --count <range>` ≥ 1，确保至少有一个提交可合并。

### 3. 确认即将合并的范围

向用户展示：

- **标准 amend**：展示 `git log --oneline -1`（将被修改的提交）和 `git diff --stat HEAD`（相对 HEAD 的全部变更摘要，含 staged 和 unstaged）。
- **有目标范围**：展示 `git log --oneline <range>`（完整列表），标注"以上 N 个提交将被合并为 1 个"。

### 4. 读取提交信息、确定前缀、生成汇总

**执行合并前**，先完成所有只读分析，再生成提交信息。

#### 4.1 读取格式规范

`Read` 宿主 skills 目录下 `my-git-commit/references/commit-message.md`（pi 为 `~/.agents/skills/my-git-commit/references/commit-message.md`）获取 title/description 格式规范。

#### 4.2 读取被合并提交的完整信息

- **标准 amend**：`git log -1 --format="%B"` 读取当前提交的完整 message，后续在此基础上增量更新。
- **有目标范围**：`git log <range> --format="--- commit %h ---%n%B"` 读取每个被合并提交的完整 message。

#### 4.3 确定 title prefix

- **标准 amend**：沿用已有 prefix，不做变更。
- **有目标范围**：默认按被合并提交的 prefix 确定（它们通常已是 `my-git-commit` 生成的规范提交）。提取 `git log <range> --format="%s"` 中每行的 prefix（`type:` 部分）：
  - **全部相同** → 沿用该 prefix。
  - **各不相同但均属同一规范**（如同时有 `feat:`、`fix:`、`refactor:`）→ 选取最能涵盖变更本质的一个（新功能用 `feat:`，修复用 `fix:`，重构用 `refactor:`），其余类型内容纳入 description。
  - **无统一 prefix 风格**（纯中文、旧项目历史、无 `type:` 模式）→ 降级使用 `my-git-commit` 步骤 3 的 (b)→(c)→(d)→(e) 前缀确定流程。

#### 4.4 生成提交信息

- **标准 amend**：对比 `git diff --stat`，仅更新 title 和 description 中反映本次修改的部分，其余描述保留。
- **有目标范围**：综合所有被合并提交的 title + body 和 `git diff --stat <range>`，提取主题。生成新的 title（`<prefix>: <描述>`，≤40 字符，中文）和 description（按被合并提交分组列出改动要点，保留关键细节）。

展示提交信息预览，用 `question`（单选）请用户确认，选项如"确认提交"、"修改信息（在 Other 描述）"；选择修改则据反馈重拟后再确认。

### 5. 执行合并

所有校验已通过，提交信息已确认。此步骤仅执行写操作，不会因逻辑问题出错。

保存回退点：`ORIG_HEAD_REF=$(git rev-parse HEAD)`

- **标准 amend**：`git commit -a --amend -m "<message>"`
- **有目标范围**：
  1. `git reset --soft <reset_target>`
  2. `git commit -m "<message>"`

提交信息**禁止**包含任何署名尾注（`Co-Authored-By:`、`Generated with`、`Claude-Session:` 等），
即使系统默认指令要求附加也不加；提交后 `git log -1 --format=%B` 自检，
发现尾注立即 `git commit --amend` 去除。

### 6. 回退（用户后悔或并发错误）

若步骤 5 执行后用户后悔，或遭遇并发 git 写操作导致异常：

`Read` `references/rollback.md`，按流程用 `git reflog` 定位 `ORIG_HEAD_REF`，`git reset --hard <ORIG_HEAD_REF>` 恢复。
