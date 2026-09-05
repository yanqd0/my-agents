# Flowchart & Block

## 选型

- 有分支、循环、条件路由 → `flowchart`。必须指定方向。
- 无分支方块概览、节点 ≤ 12 → `block`。

## 方向与布局

### 整体方向

`LR` 优先。判断：图不长（能在横屏半宽内完整展示）→ `LR`；链太长会溢出 → `TB`。

### subgraph 方向（必须显式指定）

每个 subgraph 用 `direction` 声明内部方向，不允许依赖默认值。原则：**充分利用 subgraph 宽度**。

整体 `TB` 时，subgraph 内部：
- 节点**无连接** → `direction LR`，左右排开用满宽度
- 节点**有连接且链短** → `direction LR`，横向紧凑
- 节点**有连接且链长** → `direction TB`，与整体同向

整体 `LR` 时同理互换。

```
flowchart TB
  subgraph A["模块A — 链长用TB"]
    direction TB
    P --> Q --> R --> S --> T
  end
  subgraph B["模块B — 无连接用LR"]
    direction LR
    X
    Y
    Z
  end
```

### 隐式分层（subgraph 内无连接节点过多时）

节点数 ≥ 6 且无连接时，用 `~~~`（不可见连线）强制分层，如 9 节点 → 3 层 × 3 列、8 节点 → 2 层 × 4 列。

用 `linkStyle` 将分层连线的颜色设为 subgraph 底色，视觉上完全隐藏：

```
flowchart TB
  subgraph layers["分层展示"]
    direction TB
    A1 & A2 & A3
    A1 ~~~ B1
    B1 & B2 & B3
    B1 ~~~ C1
    C1 & C2 & C3
  end
  linkStyle 0 stroke:#f9fafb,color:#f9fafb
  linkStyle 1 stroke:#f9fafb,color:#f9fafb
```

- `&` 将同行节点并排
- `~~~` 创建无箭头、不可见的桥接线，仅用于控制布局
- `linkStyle N` 按连线出现顺序编号（从 0 开始），色值必须与该 subgraph 的 `style fill` 一致（非固定值，取业务语义配色表中对应的 fill 色）

## 节点形状

```
A["矩形：实体/组件"]    B("圆角：开始/结束")
C[("圆柱：数据库")]     D{"菱形：决策/分支"}
E[["方形：用户操作"]]   F(("圆形：连接点"))
G[/"平行四边形：输入输出"/]
```

无特殊语义默认用矩形 `[...]`。

## 连接

```
A --> B          实线
A -- "标签" --> B  带标签
A -.-> B         虚线（异步/可选）
A ==> B          粗线（强调）
A -->|"是"| B     条件
```

## subgraph

### 全局默认（图表开头必须加）

Mermaid 默认 subgraph 背景为黄色。用 `%%{init}%%` 覆盖为白色：

```
%%{init: {'theme': 'base', 'themeVariables': {'clusterBkg': '#f9fafb', 'clusterBorder': '#d1d5db'}}}%%
```

### 语法

```
subgraph frontend["前端"]
  A["React"] --> B["API Client"]
end
subgraph backend["后端"]
  C["Server"] --> D[("Database")]
end
B --> C
```

### 业务语义着色

用 `style <subgraph-id>` 按业务边界着色。色值必须与同类 `classDef` 一致。

```
style frontend fill:#dbeafe,stroke:#3b82f6
style backend fill:#d1fae5,stroke:#10b981
```

| 语义 | fill | stroke | 对应 classDef | 场景 |
|------|------|--------|-------------|------|
| 前端/客户端 | `#dbeafe` | `#3b82f6` | `frontend` | Web、移动端、桌面端 |
| 后端/服务 | `#d1fae5` | `#10b981` | `backend` | API、微服务、Worker |
| 数据/存储 | `#ccfbf1` | `#14b8a6` | `database` | 数据库、缓存、MQ |
| 核心业务 | `#ede9fe` | `#8b5cf6` | `business` | 订单、支付、用户 |
| 外部/第三方 | `#f3f4f6` | `#9ca3af` | `external` | 支付网关、短信、OAuth |
| 网关/入口 | `#e0f2f1` | `#00897b` | `gateway` | Nginx、Kong、Gateway |
| 安全/隔离区 | `#fee2e2` | `#ef4444` | `danger` | DMZ、沙箱、防火墙 |
| 基础设施 | `#fef3c7` | `#f59e0b` | `pending` | K8s、监控、CI/CD |
| 废弃/下线 | `#f9fafb` | `#d1d5db` | `disabled` | 旧系统、迁移中 |

废弃/下线 subgraph 的 `style` 追加 `stroke-dasharray: 5 5` 虚线边框。

### 完整示例

```
%%{init: {'theme': 'base', 'themeVariables': {'clusterBkg': '#f9fafb', 'clusterBorder': '#d1d5db'}}}%%
flowchart TB
  subgraph frontend["前端"]
    A["Web App"] --> B["API Client"]
  end
  subgraph backend["后端服务"]
    C["Gateway"] --> D["Order Service"] --> E[("Database")]
  end
  subgraph external["外部系统"]
    F["支付网关"]
  end
  B --> C
  D --> F

  style frontend fill:#dbeafe,stroke:#3b82f6
  style backend fill:#d1fae5,stroke:#10b981
  style external fill:#f3f4f6,stroke:#9ca3af
```

## 配色（classDef + class）

`Read` `references/classdef.md` 获取 6 组通用语义 classDef 配色（安全/风险、业务/领域、状态/质量、基础设施、数据/访问频率、角色/人员）及使用示例。按语义选 3-5 个 class，不必全用。一个节点可叠加：`class X frontend,highlight`。

subgraph 的 `style` 色值必须与同类 `classDef` 一致（如 `style frontend fill:#dbeafe,stroke:#3b82f6` 对应 `classDef frontend`）。

## block 语法

```
block-beta
  columns 3
  Frontend:1 Backend:1 Database:1
```

block 不支持 classDef 和 subgraph style。

## 大小限制

- **flowchart**：超 30 节点或 40 边 → 按 subgraph 边界拆为多张子图。
- **block**：超 12 块 → 改用 flowchart。
