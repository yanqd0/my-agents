# State Diagram (stateDiagram-v2)

## 选型

有状态转移、生命周期的实体：订单、任务、连接、进程、事务、Promise。

## 语法

```
stateDiagram-v2
  [*] --> Idle
  Idle --> Running: 启动
  Running --> Success: 完成
  Running --> Failed: 异常
  Failed --> Running: 重试
  Success --> [*]
  Failed --> [*]
```

- `[*]` 起始/终止状态
- `state 状态名 { ... }` 嵌套子状态（复合状态）
- 含中文/特殊字符/长描述的状态，用 `state "描述" as id` 或 `id : 描述` 写法，不把描述直接写进状态 ID
- `--` 无方向转移，`-->` 带方向转移
- 转移标签用简短中文

## 复合状态（嵌套）

```
state Running {
  [*] --> Loading
  Loading --> Processing: 资源就绪
  Processing --> [*]: 完成
}
```

## 配色

```
classDef idle fill:#f3f4f6,stroke:#9ca3af,color:#1f2937
classDef active fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
classDef success fill:#dcfce7,stroke:#22c55e,color:#14532d
classDef error fill:#fee2e2,stroke:#ef4444,color:#7f1d1d
classDef warning fill:#fef3c7,stroke:#f59e0b,color:#78350f
```

语义对照：
- `idle`：初始、空闲、等待
- `active`：运行中、处理中
- `success`：成功、完成、正常结束
- `error`：失败、异常、超时
- `warning`：暂停、挂起、需要干预

应用：`class Idle idle`、`class Running active`（一个状态只能用一个 class）。

## 大小限制

超 12 个状态时提示拆分或使用复合状态精简。嵌套不超过 2 层。

## 常见模式

- **TCP 状态**：CLOSED → LISTEN → SYN_SENT → ESTABLISHED → CLOSE_WAIT
- **进程生命周期**：Created → Ready → Running → Terminated（中间态 Waiting/Suspended）
- **订单流程**：Pending → Paid → Shipped → Delivered（异常路径：Cancelled、Refunded）
- **Promise**：Pending → Fulfilled / Rejected
