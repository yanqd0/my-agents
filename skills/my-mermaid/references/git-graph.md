# Git Graph

## 选型

分支合并历史可视化、分支策略说明、rebase vs merge 流程演示。

## 语法

```
gitGraph
  commit id: "初始化"
  branch develop
  checkout develop
  commit id: "核心功能"
  branch feature/login
  commit id: "登录页"
  commit id: "JWT 集成"
  checkout develop
  merge feature/login
  branch feature/payment
  commit id: "支付接口"
  checkout develop
  merge feature/payment
  checkout main
  merge develop tag: "v1.0"
```

- `commit` 提交，`id:` 可选，标注简短 hash 或说明
- `branch <name>` 创建分支（从当前 checkout 位置）
- `merge <name>` 合并分支到当前 checkout
- `tag:` 在 merge 时标注版本号
- `type: REVERSE` 回退提交，`type: HIGHLIGHT` 高亮提交

## 分支策略演示

- **GitFlow**：main ← develop ← feature/* ← hotfix/*
- **Trunk-based**：main ← short-lived feature branches
- **GitHub Flow**：main ← feature branches（PR 后 squash merge）

## 配色

gitGraph 自动着色——不同分支分配不同颜色，`type: HIGHLIGHT` 的提交会突出显示。

## 大小限制

超 20 个 commit 或 5 个分支时提示精简——只保留关键节点和 merge 点。
