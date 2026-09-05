# Mermaid 图类型选择索引

本文件为 mermaid 图类型的**单一事实来源**。`my-mermaid` 和依赖它的 skill（如 `my-code-io`）均引用此表。

## 类型选择表

| 核心叙事 | 图类型 | 参考文件 | 触发场景（代码阅读 / 技术介绍） |
|---------|--------|---------|------|
| 结构关系 | `flowchart` | `flowchart.md` | 模块依赖、调用链、条件分支 / 系统架构、部署拓扑、算法流程 |
| 块结构 | `block` | `flowchart.md` | 系统方块图、组件层次 / 部署架构块图、模块划分 |
| 交互顺序 | `sequenceDiagram` | `sequence-diagram.md` | API 调用、消息传递、中间件链路 / 认证流程、协议握手 |
| 状态转移 | `stateDiagram-v2` | `state-diagram.md` | 订单/任务/连接生命周期 / TCP 状态机、Promise 状态、CI 流水线 |
| 类型层级 | `classDiagram` | `class-diagram.md` | 类继承/组合、接口实现 / 设计模式、框架核心类型 |
| 数据实体 | `erDiagram` | `er-diagram.md` | Schema 定义、ORM 外键 / 数据库设计、API 嵌套结构 |
| 进度/计划 | `gantt` | `gantt-timeline-journey.md` | 功能排期、版本路线图 |
| 时间线 | `timeline` | `gantt-timeline-journey.md` | git log 可视化 / 技术演进史、版本变更年表 |
| 用户旅程 | `journey` | `gantt-timeline-journey.md` | 用户操作追踪 / 引导流程、功能体验路径 |
| 占比分布 | `pie` | `pie.md` | 文件类型占比、测试覆盖率 / 流量分布、资源分配 |
| 量化对比 | `xychart` | `xychart.md` | benchmark 对比 / 框架性能横向对比、QPS 柱状图 |
| 分支拓扑 | `gitGraph` | `git-graph.md` | 分支合并历史 / 分支策略、发布流程 |
| 因果分析 | `ishikawa-beta` | `venn-ishikawa.md` | Bug 根因追溯 / 问题分解、故障归类 |
| 知识层次 | `mindmap` | `mindmap.md` | 项目目录结构 / 技术体系全景、功能拆解 |

## 选择优先级

结构 > 交互 > 状态转移 > 时间/分布 > 量化对比。

## 约束

- `flowchart` 不要用已废弃的 `graph`。
- `stateDiagram-v2` 不要用旧版 `stateDiagram`。
- `venn-beta` 已移除（不稳定），方案对比等场景改用文字描述或 `ishikawa-beta`。
