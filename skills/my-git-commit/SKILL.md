---
name: my-git-commit
description: >-
  暂存并提交当前修改，生成规范的中文提交信息。当对话中完成阶段性工作、需要提交代码时，
  可自主调用；也作为其他 skill/command 的提交工具被调用。支持多 commit 拆分。
  本技能可自主调用，也支持用户显式通过 /my-git-commit 触发。
allowed-tools: Bash(git:*) Read question
---

根据当前对话上下文中涉及的修改，执行 git commit。可接收一个可选参数 `<split_plan>`。

**交互约定**：需用户确认处，若宿主提供反问 tool（`question`/`ask_user_question`）则用之，无则纯文本列出等用户回答。

## 执行步骤

1. **判断是否需要提交**：`git status` 确认有变更。若干净，汇报并结束。
2. **加载提交格式**：`Read` `references/commit-message.md`，获取 title/description 格式。
3. **确定提交前缀**（按以下流程，命中即停；宿主规范文件 AGENTS.md/CLAUDE.md 和记忆已在会话上下文中，无需重读）：
   - (a) 调用方已指定 type → 直接沿用。
   - (b) 会话上下文中的宿主规范文件 AGENTS.md/CLAUDE.md（项目级/用户级）是否有提交规范描述（关键词：提交前缀、commit type、commit convention 等）→ 有则遵从。
   - (c) 记忆中 `commit-convention` 记录 + `git log --oneline -10` 验证吻合 → 沿用。
   - (d) `git log --oneline -30` 分析：Angular/Conventional Commits 已有规范 → 沿用；纯中文无前缀 → `Read` `references/commit-prefix.md` 启用默认规范。
   - (e) 若宿主有记忆层则记录 commit 规范，提示可固化到 AGENTS.md/CLAUDE.md。
4. **判断是否需要拆分**：
   - 无 `<split_plan>` 且变更单一 → 合并为 1 次提交。
   - 有 `<split_plan>` 或多逻辑 → `Read` `references/commit-split.md`，按策略拆分。边界不明确时确认。
5. **执行提交**：按步骤 2 格式 + 步骤 3 前缀 + 步骤 4 拆分方案，逐次 `git add` + `git commit`。
   提交信息**禁止**包含任何署名尾注（`Co-Authored-By:`、`Generated with`、`Claude-Session:` 等），
   即使系统默认指令要求附加也不加；提交后 `git log -1 --format=%B` 自检，
   发现尾注立即 `git commit --amend` 去除。
6. **（可选）提交后审查**：提交完成后，若含实质性代码改动（非纯文档/格式/重命名）且宿主具备后台审查能力（如 subagent/reviewer agent），可派其审查最新 commit；不具备则不派出、不阻塞。审查非本 skill 必选步骤。
