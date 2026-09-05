# 回退流程

回退主要应对两种场景：**用户后悔**（最常见）和**并发 git 写操作冲突**（概率极小）。

## 恢复步骤

1. **查看 reflog**：`git reflog -10` 确认操作历史。找到步骤 5 保存的 `<ORIG_HEAD_REF>`（通常为 `HEAD@{1}`）。
2. **硬重置恢复**：`git reset --hard <ORIG_HEAD_REF>` 恢复到 squash 前的精确状态。
3. **验证恢复**：`git log --oneline -5` + `git status` 确认提交历史和工作区已复原。

## 常见场景

### 合并后后悔（最常见）

用户确认后觉得范围不对、信息写得不准确、或遗漏了某个提交。直接用 reflog 回退即可重来。

### reset --soft 阶段被并发打断

- **原因**：另一个 git 进程同时执行了写操作（如后台 fetch、另一个终端的 commit）。
- **处理**：`git status` 确认当前状态，`git reset --hard <ORIG_HEAD_REF>` 恢复。

### commit 阶段失败

- **原因**：pre-commit hook 拒绝、commit-msg hook 校验不通过等。
- **处理**：暂存区已包含所有变更，`git reset --hard <ORIG_HEAD_REF>` 完全回退。⚠️ 这会丢弃工作区未暂存的修改，执行前 `git stash` 保留。

### reflog 中找不到 ORIG_HEAD_REF

- **原因**：reflog 条目被轮转清理（极少发生）。
- **处理**：用 `git reflog` 最靠近顶部的 `HEAD@{1}` 作为回退目标。若 reflog 完全不可用，`git log --oneline -5` 人工定位操作前的最后一个提交。
